"""Release routing and real wrapper refusals, without running a container or publisher."""
import hashlib
import os
from pathlib import Path
import subprocess

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
WRAPPER = ROOT / '.github/ci/exec-in-sif.sh'


@pytest.fixture
def runtime(tmp_path):
    image = tmp_path / 'fixture image.sif'
    image.write_bytes(b'release wrapper fixture; not a runnable container')
    fake = tmp_path / 'apptainer'
    fake.write_text('#!/bin/bash\nprintf "%s\\n" "$@" > "$CAPTURE"\n')
    fake.chmod(0o755)
    parent = tmp_path / 'job space'
    parent.mkdir()
    env = dict(os.environ, SCITEX_CI_APPTAINER=str(fake),
               SCITEX_CI_SIF=str(image),
               SCITEX_CI_SIF_SHA256=hashlib.sha256(image.read_bytes()).hexdigest(),
               RUNNER_TEMP=str(parent), CAPTURE=str(tmp_path / 'argv'))
    return env, tmp_path / 'argv'


def invoke(env):
    return subprocess.run(['bash', str(WRAPPER), 'build-in-sif.sh', '3.12'],
                          cwd=ROOT, env=env, text=True, capture_output=True, timeout=15)


def test_verified_wrapper_preserves_paths_and_owned_scratch(runtime):
    # Arrange
    env, capture = runtime
    # Act
    result = invoke(env)
    args = capture.read_text().splitlines() if capture.exists() else []
    binds = [args[i + 1] for i, value in enumerate(args) if value == '--bind']
    observed = {
        'exit': result.returncode,
        'exec': args[:1],
        'script': args[-4:],
        'checkout': str(ROOT) + ':' + str(ROOT) in binds,
        'scratch': any(value.startswith(env['RUNNER_TEMP'] + '/') and value.endswith('/tmp:/tmp') for value in binds),
        'gpfs': '/data/gpfs/projects/punim0264' in binds,
    }
    # Assert
    assert observed == {
        'exit': 0, 'exec': ['exec'],
        'script': [env['SCITEX_CI_SIF'], 'bash', '.github/ci/build-in-sif.sh', '3.12'],
        'checkout': True, 'scratch': True,
        'gpfs': Path('/data/gpfs/projects/punim0264').is_dir(),
    }, result.stdout + result.stderr


def test_wrong_image_is_refused_before_container_execution(runtime):
    # Arrange
    env, capture = runtime
    env['SCITEX_CI_SIF_SHA256'] = '0' * 64
    # Act
    result = invoke(env)
    # Assert
    assert (result.returncode != 0, 'digest mismatch' in result.stdout, capture.exists()) == (True, True, False)


@pytest.mark.parametrize('scratch', ['', 'relative-job-space'])
def test_missing_or_relative_job_scratch_is_refused(runtime, scratch):
    # Arrange
    env, capture = runtime
    env['RUNNER_TEMP'] = scratch
    # Act
    result = invoke(env)
    # Assert
    assert (result.returncode != 0, 'RUNNER_TEMP' in result.stdout + result.stderr, capture.exists()) == (True, True, False)


def test_release_uses_shared_native_tests_and_source_bound_publication():
    # Arrange
    path = ROOT / '.github/workflows/pypi-publish-and-github-release-on-tag.yml'
    workflow = yaml.load(path.read_text(), Loader=yaml.BaseLoader)
    jobs = workflow['jobs']
    # Act
    native = jobs['pytest-matrix']
    checkout = next(x for x in jobs['publish']['steps'] if x.get('uses', '').startswith('actions/checkout@'))
    build_commands = '\n'.join(x.get('run', '') for x in jobs['build']['steps'])
    observed = {
        'native': native['uses'],
        'native_overrides': native.get('with'),
        'native_secrets': set(native['secrets']),
        'build_needs': jobs['build']['needs'],
        'publish_needs': jobs['publish']['needs'],
        'release_needs': jobs['release']['needs'],
        'environment': jobs['publish']['environment']['name'],
        'publisher_checkout': checkout['with']['ref'],
        'main_guard': 'git merge-base --is-ancestor HEAD origin/main' in build_commands,
        'tested_source_guard': 'test "$(git rev-parse HEAD)" = "$GITHUB_SHA"' in build_commands,
        'obsolete_test_script': (ROOT / '.github/ci/run-in-sif.sh').exists(),
    }
    # Assert
    assert observed == {
        'native': 'scitex-ai/.github/.github/workflows/pytest-matrix.yml@103726f97249dcb1bf9c37ad235dec991a0399f9',
        'native_overrides': None, 'native_secrets': {'CODECOV_TOKEN'},
        'build_needs': ['pytest-matrix', 'runner-admission'],
        'publish_needs': ['build', 'runner-admission'],
        'release_needs': ['build', 'publish', 'runner-admission'],
        'environment': 'pypi',
        'publisher_checkout': '${{ needs.build.outputs.source_sha }}',
        'main_guard': True, 'tested_source_guard': True, 'obsolete_test_script': False,
    }
