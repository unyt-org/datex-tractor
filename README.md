# Todo-extractor
---
*Early alpha, things might break*

Github action workflow for extraction of things todo from source code and turning every one of them into an issue.

## Quickstart
---
*What is what, and how is why...*

### What this workflow does?
---
- Checks if it's on latest branch (throws exit 1 if not)
- Scans the code in the repository for 'TODO's, 'FIXME's and 'todo!()'s
- Creates an Issue with a todo-list titled "Todos" with relative links
  - Creates for each todo in the repo an issue
    - With a permalink to the correlated file, line and commit
    - Injects the corresponding issue ID into the codebase
- If nothing to do is found in the code base
  - The todo-list-issue get's closed, as well as all issues mentioned in it
- In order to work properly the last header of your projects README.md needs to be `# Datex-tractor`
  - This way the bot can increment a number, to make sure it has something to commit, even if nothing to do was found
- Labels for the created issues are `placeholder`, `todo` and `disappeared-todo`
  - The default `documentation` label is used for the `Todos` list issue

Their color's can be adjusted (via the issues web interface of your github repository) which is available at
```
https://github.com/your-org-name/your-repo-name/labels
```

### What this workflow does not?
---
- If an already mentioned todo marker is removed from code it does not close the corresponding issue
  - Instead it labels it with `disappeared-todo`
      - It's recommended to close the corresponding issue with a developer comment

### What to watch out for?
---
- While the bot is running and creating issues it's recommended to not create any issues (data-races caused by users might cause wrong mapping)
- It actually edits code in the repo and commits, reviewing the pull request is highly recommended
- If the Todo's are already numbered on the initial run mapping goes wild

## Configuration
---
Supported semver are 'v/x.x.x.' and 'release/x.x.x' with following configuration

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

## Developer comment
---
- Prototype of github-action-workflow for todo-extraction from repositories source code (following called `bot`)
- Supports branch with semver v/x.x.x.

In order to work the target repository requires to have
- `README.md` file in the project root directory
  - Last header has to be set to `# Datex-tractor` in order to work as intended

Bot is walking through repositories file system, from root on 
- Only checking files with  `[".rs", ".cpp", ".py", ".sh",".java", ".ts", ".js", ".php"]`  extensions
  - Does line wise regular expression matching of each file in question

*Note*: Patterns are matched hierarchically (`"todo!()" first, "(//|#) TODO" next, "(//|#) FIXME" last`) to prevent unclear classification of the match.

After acquiring the information 
- Enumerates matched expressions and inserts issue ID into source code
- Reads in the `README.md` and...
  - Either appends a number below
  - Or increments the number if it's already there
- Commits the changes made
 
*Note*: This is by design, so the bot has something to commit - even if no changes of the "todos" in the source code have occurred - in turn this allows to track the state of todos precisely via commit hashes submitted by the bot - making its actions transparent via git.

- Creates an Issue with a todo-list titled "Todos" with relative links
  - Creates for each todo in the repo an issue
    - With a permalink to the correlated file, line and commit
- If nothing to do is found in the code base
  - The todo-list-issue get's closed, as well as all issues mentioned in it
  
By design the bot updates the permalink of the issued todo upon every of it's runs 
- Labels for the created issues are `placeholder`, `todo` and `disappeared-todo`
  - The default `documentation` label is used for the `Todos` list issue
- allows inverse checking of as "todo" labelled issues which didn't receive an update upon the current commit 
- changing their label form "todo" to "disappeared-todo"

*Note*: The labels are hard coded, their colors are not
- renaming them prevents the bot from functioning correctly 

Per default the bot is set to send at peak one request per second
- Tailored towards running on free tier runners 
- Everything below that one second threshold seemed to hit the secondary rate limit of the github api 
- While the bot is running it may happen the issues page of your github repository not being available 
- Wrong mapping might occur if issues are handed in while the bot is creating the placeholder issues

# Datex-tractor
---
Something that will be overwritten.
