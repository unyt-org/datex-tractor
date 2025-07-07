# Todo-extractor
Early sketch of a tool for automatic creation of a todo list from source code and transform it into an issue. Optionally it also automates updating a Todo-section in the end of your readme.

## Features
- Crawls from root to leaf through your repo
- Matches todo comments left in source code
- Automatically creates an issue containing a todo list
  - Optionally: Updates a '# Todo-section' at the tail of your readme

## Integration
Per default git and github prevent accidental implementation of others projects into an own one - thus a few steps have to be gone through with to integrate this workflow into your project.

### Placement 
Setup a `.github/workflows/` directory in the root of your project - if you haven't one yet - change directory and clone this repository into it like 
```bash
cd .github/workflows
git clone -b v/0.0.1 https://github.com/unyt-org/todo-extractor
```

### Preperation
Delete the `.git` and `.github` directory of this project like
```bash
rm -fr todo-extractor/.git/
rm -fr todo-extractor/.github/
```
otherwise your github project will prevent this workflow from happening.

### Configuration
For this workflow to be registered you will have to create a configuration file

#### 'datex-tractor.yml'
Create a file like `datex-tractor.yml` and paste the following contents into it
```yml
name: datex-tractor

on:
  push:
    branches:
      - 'main'
      - 'v/**' # Triggers on branches like 'v/x.x.x'

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

### Readme Sentinel
*Careful - experimental feature - this activates automatic edits of your readme.*


The 'Todo-section' below is managed automatically. To set it up you have to append following header to your readme (make sure it is at the end, because the bot will delete everything beneath it whenever an update is triggered) like this

```md
# Todo-section
---
```
or with a number of your choosing like
```md
# Todo-section
---
256
```
otherwise the bot might append a default.

# Datex-tractor
---
- 4 files to do.
- 8 expressions matched.

## './.github/workflows/todo-extractor/datex_tractor.py'
- 47: 'todo!("Consider writing docs...")'
## './.github/workflows/todo-extractor/datex_tractor/todo_context.py'
- 5: '// TODO: update readme'
- 6: '// FIXME: corner cases'
- 7: 'todo!("improve ux and write docs")'
## './datex_tractor.py'
- 47: 'todo!("Consider writing docs...")'
## './datex_tractor/todo_context.py'
- 5: '// TODO: update readme'
- 6: '// FIXME: corner cases'
- 7: 'todo!("improve ux and write docs")'

-4027