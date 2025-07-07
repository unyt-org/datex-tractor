# Todo extractor
Early sketch of a tool for automatic creation of todo lists from source code via github actions. 

### Workflows.yml
Create a file like `run-main.yml` and paste the following contents to it
```yml
name: datex-tractor

on:
  push:
    branches:
      - 'main'
      - 'v/**'

permissions:
  contents: write
  issues: write

jobs:
  Datex-tractor:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout own repo
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with: 
          python-version: 3.13
 
      - name: Run datex_tractor_script.sh
        run: bash .github/workflows/todo-extractor/datex_tractor_script.sh
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```
# Todo-section
---
- 2 files to do.
- 4 expressions matched.

## './.github/workflows/todo-extractor/datex_tractor.py'
- 46: 'todo!("Consider writing docs...")'
## './.github/workflows/todo-extractor/datex_tractor/todo_context.py'
- 5: '// TODO: update readme'
- 6: '// FIXME: corner cases'
- 7: 'todo!("improve ux and write docs")'

-4029