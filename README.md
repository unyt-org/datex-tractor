# Todo-extractor
---
*Simple tool for bored people who are looking for something to do.*

Tool for automatic creation, update and closing of issues.

## Features
---
- Extraction of `TODO` and `FIXME` inline comments
  - Rusts `todo!("inline comments");` are included
- Creation of correlated issues to the comment in source code
  - Including path to the file, as well as line number
- Enumeration of todos with correlated issues ID
  - Keeping track and updating the comment in the issue
- Creation of a todo-list in a **Todos** titled issue
  - Contains links to the issues
  - If nothing to do closes itself as well as all listed todos
  - Reopens itself if todos reappear
  - Optionally appends the list to the README.md of your project

## Installation
---
*Assuming knowledge about what a github repository is...*

### First Step
---
Copy paste the `todo-extractor` into your `.github` directory in the root of your project. 

### Second Step
---
Configure your `.github/workflows/datex-tractor.yml` like the following
```yml
name: datex-tractor

on:
  push:
    branches:
      - 'v/*' # Replace 'v' with the branch-name you're tracking

permissions:
  contents: write
  issues: write

jobs:
  Datex-tractor:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout own repo
        uses: actions/checkout@v4

      - name: Check if is latest version
        run: bash .github/todo-extractor/check_latest.sh

      - name: Set up Python
        uses: actions/setup-python@v5
        with: 
          python-version: 3.13
 
      - name: Run datex_tractor_script.sh
        run: bash .github/todo-extractor/datex_tractor_script.sh
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```
### Third Step
---
If you have replaced the `v` with a branch name you're tracking - *i like 'v' for semver, hence the default* - you will have to replace the variable in the `.github/todo-tractor/check_latest.sh` as well. Otherwise that's all.

# Datex-tractor
---
Found nothing to do.
-3992