# Todo-extractor
---
*Early alpha, things might break*

## What it does?
---
- Checks if it's on latest branch (throws exit 1 if not)
- Scans the code in the repository for 'TODO's, 'FIXME's and 'todo!()'s
- Creates an Issue with a todo-list titled "Todos" with relative links
  - Creates for each todo in the repo an issue
    - With a permalink to the correlated file, line and commit
    - Injects the corresponding issue ID into the codebase
- If nothing to do is found in the code base
  - The todo-list-issue get's closed, as well as all issues mentioned in it
- In order to work properly the last header of your projects README.md needs to be `# Datex-traxtor`
  - This way the bot can increment a number, to make sure it has something to commit, even if nothing to do was found

## What it does not?
---
- If an already mentioned todo marker is removed from code it does not close the corresponding issue
  - It's recommended to close the corresponding issue with a developer comment

## What to watch out for?
---
- While the bot is running and creating issues it's recommended to not create any issues (data-races caused by users might cause wrong mapping)
- It actually edits code in the repo and commits, reviewing the pull request is highly recommended
- If the Todo's are already numbered on the initial run mapping goes wild

## Developer comment
---
- Labels are `placeholder`, `todo` and `disappeared-todo`
  - and `documentation` is used for the `Todos` list issue

They can and need to be setup manually (via the issues web interface of your github repository) which is available at
```
https://github.com/your-org-name/your-repo-name/labels
```

## Configuration
---
Supported semver is 'v/x.x.x.'.

### For 'v/x.x.x' use
---
```yml
name: datex-tractor

on:
  push:
    branches:
      - 'v/*'

permissions:
  contents: write
  issues: write

jobs:
  Datex-tractor:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout own repo
        uses: actions/checkout@v4

      - name: Run datex_tractor
        uses: unyt-org/todo-extractor@v0.0.1
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
```

# Datex-tractor
---
Something that will be overwritten.
