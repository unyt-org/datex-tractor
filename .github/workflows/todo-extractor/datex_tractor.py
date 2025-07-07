import os
import sys

from datex_tractor import TodoContext
from datex_tractor import get_issues, close_issue, reopen_issue, update_issue, create_issue

def main():
    # Returns int(1) if nothing to do
    desc = TodoContext.get_todo_list_desc()
    if desc != 1:
        desc = "# Checking todos...\n" + desc

    print(desc)

    # Update readme
    print(f"readme_sentinel exit code: {TodoContext.readme_sentinel()}")

    # Get auth
    token = os.environ["GITHUB_TOKEN"]
    repo = os.environ["GITHUB_REPOSITORY"]

    # Get issues
    issues = get_issues(repo, token)

    # Filter by title, check state, set to open, and update either way
    found_todos = False
    todos_id = None
    for issue in issues:

        if issue["title"] == "Todos":
            found_todos = True
            todos_id = issue["number"]

            if issue["state"] == "open" and desc != 1:
                print(f"Update todo list issue #{issue["number"]}")
                
                update_issue(repo, token, issue["number"], fields={"body": desc})

            elif issue["state"] == "closed" and desc != 1:
                print(f"Reopen and update todo list issue #{issue["number"]}")
                
                update_issue(repo, token, issue["number"], fields={"state": "open", "body": desc})

    if found_todos == True and desc == 1:
        # Closing todo list if nothing to do
        close_issue(repo, token, todos_id)

    if found_todos == False: 
        print(f"Creating new Todos issue.")
        create_issue(repo, token, title="Todos", body=desc)

    # reopen_issue(repo, token, 1)
    # close_issue(repo, token, 1)

if __name__ == "__main__":
    main()
