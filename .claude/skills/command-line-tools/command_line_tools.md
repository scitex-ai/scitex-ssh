<!-- ---
!-- Timestamp: 2026-01-20 05:53:23
!-- Author: ywatanabe
!-- File: /home/ywatanabe/.dotfiles/.claude/to_claude/skills/command-line-tools/command_line_tools.md
!-- --- -->

## You can use these tools

### Especially Useful Commands (All in Path)

```
tree (installed from source; e.g., --gitignore available)
safe_rm.sh
find_large_files.sh
install*.sh
encrypt.sh
decrypt.sh
notify.sh
rename.sh
```
For details, please use `-h | --help` option


### `cp` and `rm`
You need to add `-f` flag all the time for overrides

### Full Custom Commands (All in Path)

```
# tree --gitignore ~/.bin
/home/ywatanabe/.bin
├── backuppers
│   ├── backup_ai_ielts.lock
│   ├── backup_ai_ielts.sh
│   ├── _backup_dir.sh
│   ├── backup_neurovista.sh
│   ├── backup_pac.lock
│   ├── backup_pac.sh
│   ├── _backup_ripple_wm.sh
│   ├── _backup.sh
│   ├── download_pac_dbs.lock
│   ├── download_pac_dbs.log
│   ├── download_pac_dbs.sh
│   ├── download_pac.lock
│   ├── download_pac.log
│   └── download_pac.sh
├── claude
│   └── safe_rm.sh
├── doc
│   ├── compile_tex.sh
│   └── my_pdflatex
├── emacs
│   ├── check_elisp.sh
│   ├── e
│   └── e.sh
├── fix_permissions.sh
├── gh -> /home/ywatanabe/local/bin/gh
├── git
│   ├── gh_pull_request.sh
│   ├── git_acp_custom_lisp_modules.sh
│   ├── git_create_tests_tree.sh
│   ├── git_sync.sh
│   ├── git_upload_public_dotfiles.sh
│   ├── merge_timestamp.sh
│   ├── monitor_repository.sh
│   └── update_dotfiles_priv.sh
├── git-tools
│   ├── commands
│   │   ├── git-ac
│   │   ├── git-acp
│   │   ├── git-init
│   │   ├── git-resolve-timestamp-conflicts
│   │   ├── git-st
│   │   ├── git-track
│   │   └── git-tree
│   ├── lib
│   │   ├── common.sh
│   │   ├── conflict.sh
│   │   ├── conflicts.sh
│   │   ├── constants.sh
│   │   ├── core.sh
│   │   ├── files.sh
│   │   └── repo.sh
│   ├── README.md
│   └── utils
├── installers
│   ├── install_apptainer.sh
│   ├── install_bashdb.sh
│   ├── install_claude_code.sh
│   ├── install_dnf_packages.sh
│   ├── install_docker.sh
│   ├── install_documentation_mcp_sever.sh
│   ├── install_emacs_from_source.sh
│   ├── install_formatter_linter.sh
│   ├── install_gdu.sh
│   ├── install_gemini.sh
│   ├── install_gh_from_source.sh
│   ├── install_google_chrome_from_source.sh
│   ├── install_image_viewers.sh
│   ├── install_mermaid.sh
│   ├── install_mngs.sh
│   ├── install_mu.sh
│   ├── install_nodejs_local.sh
│   ├── install_NVIDIA_driver.sh
│   ├── install_nw.sh
│   ├── install_python_from_source.sh
│   ├── install_RAID0_ssd.sh
│   ├── install_repo_mapper.sh
│   ├── install_ripgrep_from_source.sh
│   ├── install_rust.sh
│   ├── install_screen_from_source.sh
│   ├── install_shell_formatter_linter.sh
│   ├── install_shyaml.sh
│   ├── install_ssl_from_source.sh
│   ├── install_tex.sh
│   ├── install_tldr.sh
│   ├── install_tree_from_source.sh
│   ├── install_uv.sh
│   ├── install_xsel_from_source.sh
│   └── install_yq.sh
├── llm
│   ├── claude_code_streaming.py
│   ├── cld_switch.sh
│   ├── davinci-resolve-mcp.sh
│   ├── genai_claude.sh
│   ├── genai_claude_streaming.sh
│   ├── genai_commit.sh
│   ├── genai_scitex.sh
│   ├── genai.sh -> genai_claude_streaming.sh
│   ├── genai_static.sh -> genai_claude.sh
│   └── genai_stream.sh -> genai_claude_streaming.sh
├── mail
│   ├── mv_spam_mails.sh
│   └── my_mbsync
├── media
│   ├── google-chrome
│   ├── mp42gif
│   ├── teamviewer.sh
│   └── tex2pdf_ja.sh
├── nvidia
│   ├── nvidia_check_cuda.sh
│   ├── nvidia_install_cuda.sh
│   └── nvidia_install_nvidia_driver.sh
├── nw
│   └── check_dns.sh
├── priv
│   ├── shopping.sh
│   └── shop.sh
├── python
│   ├── apt_python_3.11.sh
│   ├── apt_python_3.12.sh
│   ├── check_pypi.sh
│   ├── dnf_python_3.11.sh
│   ├── _dnf_python_3.12.sh
│   ├── dnf_python_3.12.sh
│   ├── pip_01_basic.sh
│   ├── pip_02_dev.sh
│   ├── pip_03_image.sh
│   ├── pip_04_video.sh
│   ├── pip_05_dsp.sh
│   ├── pip_06_ml.sh
│   ├── pip_06_stats.sh
│   ├── pip_07_torch_cuda_10.2.sh
│   ├── pip_07_torch_cuda_11.8.sh
│   ├── pip_07_torch_cuda_12.1.sh
│   ├── python_check_tk
│   ├── python_cleanup
│   ├── python_init_with_local_scitex.sh
│   └── python_ps1_home
├── run_tests_elisp.sh
├── secrets
│   ├── ylab_adau_adad
│   ├── ylab_check_gpus
│   ├── ylab_hit_and_run
│   ├── ylab_singularity_bind
│   ├── ylab_ssh_port_forwarding
│   ├── ylab_tools_create_aliases
│   ├── ylab_tools_create_scripts
│   ├── ywata_autossh_tunnel.sh
│   └── ywata_ssh_define_aliases
├── slurm
│   ├── README.md
│   ├── sbatch2.sh
│   ├── sbatch.sh
│   ├── slogin -> slogin.sh
│   ├── slogin2 -> slogin2.sh
│   ├── slogin2.sh
│   ├── slogin.sh
│   ├── srequest_sbatch2.sh
│   ├── srequest_sbatch.sh
│   ├── srun2.sh
│   └── srun.sh
├── system
│   ├── check_host.sh
│   ├── check_sudo.sh
│   ├── cleanup_home.sh
│   ├── correct_permissions.sh
│   ├── correct_permissions_v01-emacs-inits-not-700.sh
│   ├── cron_add.sh
│   ├── crop_white_space.py
│   ├── crop_whitespace.py
│   ├── disable_wayland.sh
│   ├── disk_speed.sh
│   ├── get_specs.sh
│   ├── highlight_error_warning.sh
│   ├── setup_hostname.sh
│   ├── split_fpath.sh
│   ├── ssh_fetch_hostnames.sh
│   ├── sudo_check.sh
│   ├── system_get_info.sh
│   ├── to_screen.sh
│   └── ubuntu_add_user.sh
└── utils
    ├── buzzer.sh
    ├── check_rain.py
    ├── cleanup_directory.sh
    ├── ctee.sh
    ├── decrypt.sh
    ├── delete_zone_identifiers.sh
    ├── dimmer.sh
    ├── echo_eval.sh
    ├── encrypt.log
    ├── encrypt.sh
    ├── find_large_files.sh
    ├── flatten_directory
    ├── flatten_directory.sh
    ├── gen_pw.sh
    ├── inspect_db.sh
    ├── ln_deep_directory.sh
    ├── ls_mngs_config.sh
    ├── mbsync_generate.sh
    ├── mydu.sh
    ├── myrsync.sh
    ├── notify_command
    ├── notify_rain
    ├── notify_rain.sh
    ├── notify.sh
    ├── pipe_notify.sh
    ├── rclone_backup.sh
    ├── remove_dropbox_and_onedrive_files.sh
    ├── __rename.sh
    ├── _rename.sh
    ├── rename.sh -> rename_sh/rename.sh
    ├── rename_sh
    │   ├── Makefile
    │   ├── README.md
    │   ├── rename.sh
    │   ├── rename_v01.sh
    │   ├── rename_v02.sh
    │   ├── rename_v03-only-dir-excludable.sh
    │   ├── rename_v04-dir-fname-symlink-not-renamed-and-single-processing-and-no-echo-xxx.sh
    │   └── test_files
    │       ├── bar_link
    │       │   └── bar_module.py
    │       ├── bar_project
    │       │   └── bar_module.py
    │       ├── django_foo
    │       │   ├── migrations
    │       │   │   └── 0001_initial.py
    │       │   ├── models.py
    │       │   ├── settings.py
    │       │   └── views.py
    │       ├── foo_data
    │       │   ├── config.yaml
    │       │   └── foo_script.py
    │       ├── foo_link.py
    │       └── README.md
    ├── rename_tests.zip
    ├── rename_v08-not-working-for-directories.sh
    ├── render_mermaid.sh
    ├── rg -> /home/ywatanabe/.local/bin/rg
    ├── safe_rsync.sh
    ├── scitex
    │   ├── push_scitex.sh
    │   ├── tree_scitex.sh
    │   └── tree_scitex_v01-no-line-count.sh
    ├── ssl2gpg.sh
    ├── sync.sh
    ├── toggle_debug.sh
    ├── translate_comments_into_English.sh
    ├── tree_scitex.sh -> scitex/tree_scitex.sh
    ├── verify_tar.gz.sh
    ├── view_repo.sh
    ├── view_repos.sh
    ├── wsl2-buzzer.sh
    └── xsel -> /home/ywatanabe/.bin/xsel-1.2.0/bin/xsel

30 directories, 226 files
```

<!-- EOF -->