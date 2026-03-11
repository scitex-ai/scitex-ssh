<!-- ---
!-- Timestamp: 2026-02-24 08:57:51
!-- Author: ywatanabe
!-- File: /home/ywatanabe/.dotfiles/src/.claude/to_claude/commands/audit.md
!-- --- -->

## Audit

Is everything clean and professional? For example:

- [ ] Documents
  - [ ] Organized, up-to-date, not redundant, necessary and sufficient

- [ ] Shell Script
  - [ ] Have argparser, usage command, help option

- [ ] Python API
  - [ ] Internal code are not exposed to users, minimizing APIs for better user experience

- [ ] CLI commands
  - [ ] No original logics - always use Python or shell logics as is
  - [ ] -h | --help option must be available all for all commands
  - [ ] --help-recursive option must be available for all commands with children
  - [ ] Ensure standardized naming
  - [ ] Intuitive, organized
  - [ ] Cli command is equipped with tab completion
    
- [ ] HTTP Service API
  - [ ] No original logics - always delegate to CLI commands

- [ ] MCP Service API
  - [ ] No original logics - always delegate to CLI commands
  - [ ] What AI agent called must be always reproducible by humans with the corresponding CLI command
  - [ ] Standardized sub-commands:
    $ package-name mcp {start,doctor,installation,list-tools}
    See ~/proj/scitex-code

- [ ] Tests
  - [ ] Is coverage calculated?
  - [ ] Is coverage sufficient?

- [ ] CI
  - [ ] Is CI correctly setup?
  - [ ] Is the last CI passed? If failed, are they already fixed?

- [ ] Reproducible without developer's memory
  - [ ] See `/no-long-term-memory` command

- [ ] Cleanliness
  - [ ] Is project root clean without unnecessary artifacts?

- [ ] The project will work as expected and documented
  - [ ] Run small experiments for verification if needed 

- [ ] Version consistency
  - [ ] toml, __init__.py, tag, release, pypi and so on

- [ ] No personal info
  - [ ] If package is designed for publication, do not include my own setups and keep generic tones
  - [ ] .env contents (gitignored), name, email, github should be accepted
  
- [ ] Examples
  - [ ] `./examples` must have demonstrations for main features with numbering like:
    - [ ] `./examples/00_run_all.sh`
    - [ ] `./examples/01_<descriptive-name>.{py,ipynb,sh}`
  - [ ] Artifacts must be saved close place
    - [ ] `./examples/01_<descriptive-name>_out/`

- [ ] Environmental Variables
  - [ ] Safe for name conflict with prefix (e.g., NG: "ENV_NAME", OK: "PROJECT_NAME_ENV_NAME")
  - [ ] PROJECT_NAME_DEBUG_MDOE=1
  - [ ] .env file in project root

- [ ] GitHub About Section
  - [ ] Description, Homepage, and Topics are well-written for the current codebase
  - [ ] Match user expectations and actual implementations
  - [ ] Consider SEO effectiveness as well
    - [ ] Add `scitex` to keywords for scitex ecosystem package

- [ ] SciTeX Brand
  - [ ] Keep consistency in cli commands
  - [ ] Use fastapi and fastmcp when needed
  - [ ] For delegation please check branding changer logics
  - [ ] Do not add ywatanabe@scitex.ai at the footer of project readme
    - [ ] This is new rule to show scitex is not for my project but for the community
  ## Delegation to Downstream Packages
  django (~/proj/scitex-cloud) -> scitex (~/proj/scitex-python) -> downstream packages like:
  ~/proj/figrecipe (= scitex-plt)
  ~/proj/scitex-writer
  ~/proj/scitex-dataset
  ~/proj/socialia

  Business logics to the most downstream module and upper modules should delegate to downstream packages like a cascade. Keep separation of concerns and do not repeat yourself for single source of truth.

<!-- EOF -->