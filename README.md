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

## What it does not?
---
- If an already mentioned todo marker is removed from code it does not close the corresponding issue

## What to watch out for?
---
- While the bot is running and creating issues it's recommended to not create any issues (data-races caused by users might cause wrong mapping)
- It actually edits code in the repo and commits, reviewing the pull request is highly recommended

## Configuration
---
Supported semvers are 'v/x.x.x.' and 'release/x.x.x'.

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

### For 'release/x.x.x' use
---
```yml
name: datex-tractor

on:
  push:
    branches:
      - 'release/*'

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
        uses: unyt-org/todo-extractor@r0.0.1
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
```
