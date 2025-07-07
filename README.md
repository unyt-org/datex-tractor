# Todo extractor
---
Early sketch of a tool for automatic creation of todo lists from source code via github actions. 

## Usage
---
Create and change into the `/.github/workflows/` directory of your projects root first, then clone the repo. 

### Workflows.yml
---
Create a file like `run-main.yml` and paste the following contents to it
```yml
name: run-main-inside-todo-script

on:
  push:
    branches:
      - 'main'

permissions:
  contents: write
  issues: write

jobs:
  run-script:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout own repo
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with: 
          python-version: 3.13
 
      - name: Run todo_script.sh
        run: bash .github/workflows/todo-extractor/todo_script.sh
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

# Todo-section
---
- 2 files to do.
- 4 expressions matched.

## './.github/workflows/todo-extractor/main.py'
- 46: 'todo!("Consider writing docs...")'
## './.github/workflows/todo-extractor/todo_context.py'
- 5: '// TODO: FIXME'
- 6: '// FIXME: TODO'
- 7: 'todo!("TODO FIXME")'

-4033