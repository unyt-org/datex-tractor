# Todo-extractor
---
GitHub action workflow for extraction of things todo from source code and turning every one of them into an issue.

*Early alpha.*

# Quickstart
---
- Create a `/.github/workflows/` in the root of your GitHub repository - if you haven't already
- Create a `/.github/workflows/datex-tractor.yml` configuration file
- Use one of the configurations described - or create your own

## Configuration
---
Supported semantic versions are `'v/x.x.x.'` and `'release/x.x.x'` with following suggestions of configuration.

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

## What it does?
---
Checks if it's on latest branch - throws `exit 1` if not - then it starts creating issues.
- Scans for `TODO` and `FIXME` inline-comments
  - Scans also lines with `todo!()` macros
- Creates an issue with a todo-list titled `Todos` 
- Creates individual issues with permalinks to the correlated file, line and commit
    - Writes the associated issue ID into the inline comment of the source code
    - Links each issue relatively to the main TODO list issue
- [Labels](https://docs.github.com/en/issues/using-labels-and-milestones-to-track-work/managing-labels) for the auto-generated issues are `placeholder`, `todo` and `disappeared-todo`
  - The default `documentation` label is used for the `Todos` list issue

> [!TIP] 
> Label colors can be adjusted (via the labels section of your GitHub repository) which is available at
```
https://github.com/your-org-name/your-repo-name/labels
```

## What it doesn't?
---
If an already mentioned todo-comment is removed from the code it does not close the corresponding issue
- Instead it changes its label to `disappeared-todo`

> [!IMPORTANT]
> Changing labels of the issues created by the bot, or the title of the todo-list-issue, results in undefined behaviour.

## What to watch out for?
---
> [!WARNING]
> While the bot is running and creating issues it's recommended to not create any issues (data-races caused by users might cause wrong mapping).

> [!TIP]
> It actually edits code in the repo and commits, reviewing the pull request is highly recommended.

> [!CAUTION]
> If the Todo's are already numbered on the initial run mapping goes wild.

# Technical design
---
Prototype of github-action-workflow for todo-extraction from repositories source code

## Process
---
Bot is walking through repositories file system, from root on 
- Only checking files with  `[".rs", ".cpp", ".py", ".sh", ".s", ".java", ".ts", ".js", ".php"]` extensions
  - Does line wise regular expression matching of each file in question

> [!NOTE]
> Patterns are matched hierarchically (`"todo!()" first, "(//|#) TODO" next, "(//|#) FIXME" last`) to prevent unclear classification of the match.

After acquiring the information 
- Enumerates matched expressions and inserts issue ID into source code
- Commits and pushes the changes made - if any, otherwise it pushes an empty commit
 
> [!NOTE]
> This allows to track the state of todos precisely via commit hashes submitted by the bot - making its actions transparent via git, even if the action is only updating all todo-issues to the current state.

## Synchronise 
---
- Creates a collection issue that contains a todo-list titled `Todos` with relative links to all other auto-generated issues
- Creates an issue for each todo in the repo
  - With a permalink to the correlated file, line and commit

> [!IMPORTANT]
> If nothing to do is found in the code base the todo-list-issue get's closed, as well as all issues mentioned in it.
 
### Request timing
--- 
By default, the bot is configured to send at most one request per second.
- This rate is optimized for running on free-tier GitHub Actions runners.
- Sending requests more frequently than once per second tends to trigger GitHub's secondary rate limits.
- While the bot is running, the Issues page of your GitHub repository may temporarily become unavailable.

> [!NOTE]
> This results in 3,600 requests per hour at maximum rate (should leave at minimum 1,400 API calls for other jobs on a free tier runner). 

> [!TIP] 
> Check out [actions limits](https://docs.github.com/en/actions/reference/actions-limits) for more information on this topic.

> [!IMPORTANT]
> Unservered API requests just print out error states - they are not throwing errors.

## Labels
---
Updates the permalink of the issued todo upon every of it's runs 
- Labels for the created issues are `placeholder`, `todo` and `disappeared-todo`
  - The default `documentation` label is used for the `Todos` titled issue
- Allows inverse checking of as `todo` labelled issues which didn't receive an update upon the current commit 
- Changing their label form `todo` to `disappeared-todo`

> [!CAUTION] 
> The labels are hard coded, their colors are not - renaming them prevents the bot from functioning correctly 

# Developer Notes
---
### How to create issues
---
*Is having to find problems to solve a problem?*

An incomprehensible guide - just for a change - i mean, who wants more issues… 

**First milestone**
- Crawl the repo, read in files filtered by name extensions.
- Check file with regex for todo's.
- Keep track of file paths and lines containing todo.
- Extract blocks of code around every todo.

**Second milestone**

Prompt your locally running AI code assistant (or unpaid Intern) to:
- Analyse unfinished code.
- Elaborate assumptions derived by implications.
- If possible suggest a plan to complete unfinished code. 

**Third milestone**
- Don't unpack and don't index into it, neither you go through getters - just typecast every codeblock including metadata to a string and pass it to the model.
- Generate 100+ complaints about weirdly formatted code and store them as tickets for later.

**Three "don't's"**
- Don't solve any problems - that would kill the vibe.
- Don't try to make it useful on first try - otherwise future you will grow bored again.
- Don't unpack code objects - just stringify.

**Three "todo's"**
- Unfinished code doesn't want to be finished - it just wants to be acknowledged.
- Point your LLM into the shadows - let it hallucinate clarity into chaos.
- Its not perfect - nothing ever is. 

### How to continuously create and integrate issues
---
*Is creating issues instead of resolving any an issue, a problem - neither?*

A comprehensible guide - because the first one turned out to be confusing…

**First milestone**
- Crawl the repo, read in files filtered by name extensions.
- Check the files contents with regexes for todo's - but not like last time - use named groups for your own sanities sake…
- Keep track of files path and line containing todo.

**Second milestone**
- Get all issues of the repo - via API calls.
- Continue the primary key pattern GitHub uses for issues - simply increment the highest "number" you can find in your pile of JSON responses…
- Insert your a-priori made-up issue-ID's into the code base - commit, push - trust in git and keep the commit hash close.

**Third milestone**
- Create placeholder issues right after pushing your commit.
- Generate a link to the file and line where something to do was found.
- Update the issues body - just overwrite the placeholders body with the link to your match.

**Fourth milestone**
- Change the label from "placeholder" to "todo".
- Backtrack which as "todo" labelled issues didn't receive an update upon the current commit - bookkeeping the way Dave from accounting likes - notice if and what is missing.
- Conclude they do not exist anymore - label them as "disappeared-todo", whatever that means - *There are only two kinds of people, those who can infer from missing data*

**Fifth milestone**
- Automatically create a todo-list-issue with relative links to the real issues - label it as "documentation".
- Reopen issues in case someone closed it, but left the todo comment in the source code…
- Automate the entire thing designed within constrains of GitHub workflows.

Making todo-inline-comments traceable - it's not as if they're syntax errors - but they *could* be. 

### How to avoid closure
---
*Unfinished code and the beauty of leaving things undone.*

An unnecessary guide - because completion is overrated, and ambiguity scales better than clarity.

**First milestone**
- Re-crawl the repo - yes, again - trust issues, remember?
- Re-collect all the TODOs, but this time compare the wording to previous commits. If it's been rephrased, congratulations: it's still unfinished, but now with a literary flourish.
- Tag these reworded TODOs as "evolved". Write poetry about them - Haikus in ANSI-C.

**Second milestone**
- Introduce a new label: "haunted" - this goes on every issue that has been opened, closed, re-opened, and closed again within 48 hours.
- Consider these "emotionally unstable tasks" and flag them for future interns to "learn from."
- Create a graph that maps TODOs to their issues using edges labeled: "lol no", "eh, maybe", and "who did this". The graph should be non-directional - like your roadmap.

**Third milestone**
- Begin labeling files - not just issues.
- If a file contains more than 5 TODOs, label it "manifesto".
- If it contains zero TODOs, label it "coward".
- If it contains a TODO written in all caps, label it "crisis".

**Fourth milestone**
- Introduce version-controlled optimism: every time a new TODO is found, record the timestamp and the ambient mood (inferred via commit message tone).
- Make a heatmap of developer regret.
- Publish a dashboard no one asked for - but everyone secretly checks - update it only during emotionally vulnerable hours.

**Fifth milestone**

Implement a sarcastic linter. 

If it finds multiple unresolved TODOs in a block, it leaves comments like:
- "Bold of you to leave this here."
- "This looks like a job for Future You - say hi to burnout."
- "This TODO has celebrated three birthdays. Cake soon?"
- Have the linter auto-comment in PR's: "I see we're still pretending this is going to be addressed."

**Three new "don't's"**
- Don't ever delete a TODO - just move it around until it's someone else's problem.
- Don't treat incomplete work as failure - treat it as potential - infinite potential.
- Don't comment TODOs without a date - that way, no one knows how long the shame has been festering.

**Three new "todo's"**
- Turn TODOs into fantasy - they're not bugs, they're paradoxical elven artefacts - try searching for "7f 45 4c 46" if you don't believe elf magic is a real thing…
- Feed your LLM a thousand TODOs - let it write a novel called "Abandoned futures & broken promises" - or did you already?
- When in doubt, just add another TODO - creates the illusion of progress without burdening your soul.

**Final milestone**
- Rebrand your project as conceptual art.
- Push to prod.
- Go outside.

# License
---
Currently [MIT](LICENSE.txt).
