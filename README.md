# Todo-extractor
---
Github action workflow for extraction of things todo from source code and turning every one of them into an issue.

*Early alpha, things might break*

# Quickstart
---
*What is what, and how is why...*

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

## What this workflow does?
---
- Checks if it's on latest branch (throws exit 1 if not)
- Creates an Issue with a todo-list titled "Todos" with relative links
    - With a permalink to the correlated file, line and commit
    - Comments the corresponding issue ID into the codebase
- In order to work properly the last header of your projects README.md needs to be `# Datex-tractor`
  - This way the bot can increment a number, to make sure it has in any case a change to commit
- Labels for the created issues are `placeholder`, `todo` and `disappeared-todo`
  - The default `documentation` label is used for the `Todos` list issue

Their color's can be adjusted (via the issues web interface of your github repository) which is available at
```
https://github.com/your-org-name/your-repo-name/labels
```

## What this workflow does not?
---
- If an already mentioned todo marker is removed from code it does not close the corresponding issue
  - Instead it changes its label to `disappeared-todo`

## What to watch out for?
---
- While the bot is running and creating issues it's recommended to not create any issues (data-races caused by users might cause wrong mapping)
- It actually edits code in the repo and commits, reviewing the pull request is highly recommended
- If the Todo's are already numbered on the initial run mapping goes wild

# Technical design
---
- Prototype of github-action-workflow for todo-extraction from repositories source code (following called `bot`)

## Data processing
---
*Load, extract, process*

### Load
---
In order to work the target repository requires to have
- `README.md` file in the project root directory
  - Last header has to be set to `# Datex-tractor` in order to work as intended

Bot is walking through repositories file system, from root on 
- Only checking files with  `[".rs", ".cpp", ".py", ".sh",".java", ".ts", ".js", ".php"]`  extensions
  - Does line wise regular expression matching of each file in question

*Note*: Patterns are matched hierarchically (`"todo!()" first, "(//|#) TODO" next, "(//|#) FIXME" last`) to prevent unclear classification of the match.

###  Process and save state
---
After acquiring the information 
- Enumerates matched expressions and inserts issue ID into source code
- Reads in the `README.md` and...
  - Either appends a number below
  - Or increments the number if it's already there
- Commits the changes made
 
*Note*: This is by design, so the bot has something to commit - even if no changes of the "todos" in the source code have occurred - in turn this allows to track the state of todos precisely via commit hashes submitted by the bot - making its actions transparent via git.

## Synchronise with server
---
- Creates an Issue with a todo-list titled "Todos" with relative links
  - Creates for each todo in the repo an issue
    - With a permalink to the correlated file, line and commit
- If nothing to do is found in the code base
  - The todo-list-issue get's closed, as well as all issues mentioned in it
 
### Request timing
--- 
Per default the bot is set to send at peak one request per second
- Tailored towards running on free tier runners 
- Everything below that one second threshold seemed to hit the secondary rate limit of the github api 
- While the bot is running it may happen the issues page of your github repository not being available 
- Wrong mapping might occur if issues are handed in while the bot is creating the placeholder issues
 
## Issue Labels
---
By design the bot updates the permalink of the issued todo upon every of it's runs 
- Labels for the created issues are `placeholder`, `todo` and `disappeared-todo`
  - The default `documentation` label is used for the `Todos` list issue
- allows inverse checking of as "todo" labelled issues which didn't receive an update upon the current commit 
- changing their label form "todo" to "disappeared-todo"

*Note*: The labels are hard coded, their colors are not
- renaming them prevents the bot from functioning correctly 

# License
---
Currently MIT License.

# Developer Notes
---
## How to create issues
---
### Is having to find problems to solve a problem?

An incomprehensible guide - just for a change - i mean, who wants more issues… 

### First milestone
- Crawl the repo, read in files filtered by name extensions.
- Check file with regex for todo's.
- Keep track of files path and line containing todo.
- Extract block of code around every todo.

### Second milestone
Prompt your locally running AI code assistant (or unpaid Intern) to:
- Analyse unfinished code.
- Elaborate assumptions derived by implications.
- If possible suggest a plan to complete unfinished code. 

### Third milestone
- Don't unpack and don't index into it, neither you go through getters - just typecast every codeblock including metadata to a str and pass it to the model.
- generate 100+ complaints about weirdly formatted code and store them as tickets for later.

### Three "don't's"
- Don't solve any problems - that would kill the vibe.
- Don't try to make it useful on first try - otherwise future you will grow bored again.
- Don't unpack code objects - just stringify.

### Three "todo's"
- Unfinished code doesn't want to be finished - it just wants to be acknowledged.
- Point your LLM into the shadows - let it hallucinate clarity into chaos.
- Its not perfect - nothing ever is. 

## How to continuously create and integrate issues
---
### Is creating issues instead of resolving any an issue, a problem - neither?

A comprehensible guide - because the first one turned out to be confusing…

### First milestone
- Crawl the repo, read in files filtered by name extensions.
- Check the files contents with regexes for todo's - but not like last time - use named groups for your own sanities sake…
- Keep track of files path and line containing todo.

### Second milestone
- Get all issues of the repo - via api calls.
- Continue the primary key pattern github uses for issues -  simply increment the highest "number" you can find in your pile of json responses…
- Insert your a-priori made-up issue-ID's into the code base - commit, push - trust in git and keep the commit hash close.

### Third milestone 
- Create placeholder issues right after pushing your commit.
- Generate a link to the file and line where something to do was found.
- Update the issues body - just overwrite the placeholders body with the link to your match.

### Fourth milestone
- Change the label from "placeholder" to "todo".
- Backtrack which as "todo" labelled issues didn't receive an update upon the current commit - bookkeeping the way Dave from accounting likes - notice if and what is missing.
- Conclude they do not exist anymore - label them as "disappeared-todo", whatever that means - *There are only two kinds of people, those who can infer from missing data*

### Fifth milestone 
- Automatically create a todo-list-issue with relative links to the real issues - label it as "documentation".
- Reopen issues in case someone closed it, but left the todo comment in the source code…
- Automate the entire thing designed within constrains of github workflows.

Making todo-inline-comments traceable - it's not as if they're syntax errors - but they could be. 

## How to avoid closure
---
### Unfinished code and the beauty of leaving things undone.

An unnecessary guide - because completion is overrated, and ambiguity scales better than clarity.

### First milestone
- Re-crawl the repo - yes, again - trust issues, remember?
- Re-collect all the TODOs, but this time compare the wording to previous commits. If it's been rephrased, congratulations: it's still unfinished, but now with a literary flourish.
- Tag these reworded TODOs as "evolved". Write poetry about them - Haikus in ANSI-C.

### Second milestone
- Introduce a new label: "haunted" - this goes on every issue that has been opened, closed, re-opened, and closed again within 48 hours.
- Consider these "emotionally unstable tasks" and flag them for future interns to "learn from."
- Create a graph that maps TODOs to their issues using edges labeled: "lol no", "eh, maybe", and "who did this". The graph should be non-directional - like your roadmap.

### Third milestone
- Begin labeling files - not just issues.
- If a file contains more than 5 TODOs, label it "manifesto".
- If it contains zero TODOs, label it "coward".
- If it contains a TODO written in all caps, label it "crisis".

### Fourth milestone
- Introduce version-controlled optimism: every time a new TODO is found, record the timestamp and the ambient mood (inferred via commit message tone).
- Make a heatmap of developer regret.
- Publish a dashboard no one asked for -  but everyone secretly checks - update it only during emotionally vulnerable hours.

### Fifth milestone
Implement a sarcastic linter. 

If it finds multiple unresolved TODOs in a block, it leaves comments like:
- "Bold of you to leave this here."
- "This looks like a job for Future You - say hi to burnout."
- "This TODO has celebrated three birthdays. Cake soon?"
- Have the linter auto-comment in PR's: "I see we're still pretending this is going to be addressed."

### Three new "don't's"
- Don't ever delete a TODO - just move it around until it's someone else's problem.
- Don't treat incomplete work as failure - treat it as potential - infinite potential.
- Don't comment TODOs without a date - that way, no one knows how long the shame has been festering.

### Three new "todo's"
- Turn TODOs into fantasy - they're not bugs, they're paradoxical elven artefacts - try searching for "7f 45 4c 46" if you don't believe elf magic is a real thing…
- Feed your LLM a thousand TODOs - let it write a novel called "Abandoned futures & broken promises" - or did you already?.
- When in doubt, just add another TODO - creates the illusion of progress without burdening your soul.

### Final milestone
- Rebrand your project as conceptual art.
- Push to prod.
- Go outside.

# Datex-tractor
---
Something that will be overwritten.
