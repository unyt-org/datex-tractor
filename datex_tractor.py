import os
import sys

from datex_tractor import TodoContext
from datex_tractor import get_issues, close_issue, reopen_issue, update_issue, create_issue

def main():
    # If nothing to do just exit
    desc = TodoContext.get_todo_list_desc()
    if desc == 1:
        print("Exit - found nothing to do")
        sys.exit()
    else:
        desc = "# Todo check...\n" + desc
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
    for issue in issues:
        print(issue)
        
        if issue["title"] == "Todos":
            found_todos = True
            if issue["state"] == "open":
                print(f"Update todo list issue #{issue["number"]}")
                
                update_issue(repo, token, issue["number"], fields={"body": desc})

            elif issue["state"] == "closed":
                print(f"Reopen and update todo list issue #{issue["number"]}")
                
                update_issue(repo, token, issue["number"], fields={"state": "open", "body": desc})

    if found_todos == False: 
        print(f"Creating new Todos issue.")
        create_issue(repo, token, title="Todos", body=desc)

    # todo!("Delete this testing comment.")

if __name__ == "__main__":
    main()
