import os
import sys
import json
import urllib.request

from todo_context import TodoContext
from gethub import get_issues, close_issue, reopen_issue, update_issue

def main():
    # If nothing to do just exit
    desc = TodoContext.get_todo_list_desc()
    if desc == 1:
        print("Exit on error, found nothing to do")
        sys.exit()
    else:
        print(desc)

    # Update readme
    print(f"readme_sentinel exit code: {TodoContext.readme_sentinel()}")

    # Get auth
    token = os.environ["GITHUB_TOKEN"]
    repo = os.environ["GITHUB_REPOSITORY"]

    # Get issues
    issues = get_issues(repo, token)

    # Filter by title, check state, set to open, and update either way
    for issue in issues:
        print(issue)
        if issue["title"] == "Todos":
            if issue["state"] == "open":
                print(f"Update todo list issue #{issue["number"]}")
                update_issue(repo, token, issue["number"], fields={"body": desc})

            elif issue["state"] == "closed":
                print(f"Reopen and update todo list issue #{issue["number"]}")
                update_issue(repo, token, issue["number"], fields={"state": "open", "body": desc})

    # todo!("Add more inline comments.")
    # reopen_issue(repo, token, 1)
    # close_issue(repo, token, 1)

if __name__ == "__main__":
    main()
