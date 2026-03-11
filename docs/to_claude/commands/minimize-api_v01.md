<!-- ---
!-- Timestamp: 2026-01-30 06:27:04
!-- Author: ywatanabe
!-- File: /home/ywatanabe/.claude/commands/minimize-api.md
!-- --- -->


## Minimize, clean API Exposure

API must be clean.

### Python
Regarding variables, functions, classes, modules:
    Expose only necessary, useful, minimal APIs
    Hide internal code to user by using underscore in python.

#### After refactoring
Update corresponding imports, tests, examples, documents

#### Examples for how to hide internal code
You can learn standards in `~/proj/scitex-python`

#### Check current APIs
Check exposed APIs by scitex-python:
                                                                                         ``` bash
scitex introspect api <package-name>
```
Output will be like:

```
API tree of scitex_writer (42 items):
[M] scitex_writer -  (v2.3.1)...
[M] bib
  [F] add
  [F] get
  [F] list_entries
  [F] list_files
  [F] merge
  [F] remove
[F] build_guideline
[M] compile
  [F] manuscript
  [F] revision
  [F] supplementary
[M] figures
  [F] add
  [F] convert
  [F] list
  [F] pdf_to_images
  [F] remove
[F] generate_ai2_prompt
[F] generate_asta
[F] get_guideline
[M] guidelines
  [F] build
  [F] get
  [F] get_source
  [F] list_sections
[F] list_guidelines
[M] project
  [F] clone
  [F] get_pdf
  [F] info
  [F] list_document_types
[M] prompts
  [F] generate_ai2_prompt
  [F] generate_asta
[M] tables
  [F] add
  [F] csv_to_latex
  [F] latex_to_csv
  [F] list
  [F] remove
(.env-3.11) (wsl) scitex-writer $ 
```

<!-- EOF -->