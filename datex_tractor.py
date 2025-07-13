import os
import sys
import time

from datex_tractor import TodoContext
from datex_tractor import get_issues, close_issue, reopen_issue, update_issue, create_issue

def main():
    if len(sys.argv) > 1:
        print("Commit hash")
        print(sys.argv[1])

    # Get issues
    token = os.environ["GITHUB_TOKEN"]
    repo = os.environ["GITHUB_REPOSITORY"]
    print("Fetching issues...")
    issues = get_issues(repo, token)

    if len(issues) > 0:
        issue_counter = max([issue["number"] for issue in issues])
        issue_counter += 1
    else:
        issue_counter = 2

    # Returns int(1) if nothing to do
    desc = TodoContext.get_todo_listed_issues(issue_counter)
    if desc != 1:
        desc = "# Checking todos...\n" + desc

    todo_paths = list(TodoContext.initialize_paths(".", issue_counter))
    todo_paths.sort(key=lambda x: x.path)

    print("Trying to manipulate todo-list issue...")

    # Logic for todo-list
    # Filter by title, check state, set to open, and update either way
    found_todos = False
    todos_id = None
    for issue in issues:

        if issue["title"] == "Todos":
            found_todos = True
            todos_id = issue["number"]

            # If open list and something to do
            if issue["state"] == "open" and desc != 1:
                update_issue(repo, token, issue["number"], fields={"body": desc})

            # If open list but nothing to do close existing listed issues
            elif issue["state"] == "open" and desc == 1:
                lines = issue["body"].splitlines()
                issues_in_list = [line.removeprefix("- Id: #") for line in lines if line.startswith("- Id: #")]

                for id in issues_in_list:
                    close_issue(repo, token, int(id))

            # If closed list and something to do reopen by updating
            elif issue["state"] == "closed" and desc != 1:
                update_issue(repo, token, issue["number"], fields={"state": "open", "body": desc})

    if found_todos == True and desc == 1:
        print("Found todo list but nothing to do, closing list.")
        # Closing todo list if nothing to do
        close_issue(repo, token, todos_id)

    if not found_todos or found_todos == False: 
        print(f"Creating new todo list issue.")
        create_issue(repo, token, title="Todos", body=desc)


    print("Starting creating and updating issues.")
    base_url = f"https://github.com/{repo}/blob/{sys.argv[1]}"
    # Create or Update issues
    for path in todo_paths:
        time.sleep(6)
        for i, line_number in enumerate(path.line_numbers):
            time.sleep(2)
            link = f"{base_url}/{path.path.removeprefix("./")}#L{line_number}"

            if int(path.issue_numbers[i]) in [int(issue["number"]) for issue in issues]:
                print(f"Update issue: {path.issue_numbers[i]}")
                update_issue(
                    repo, 
                    token, 
                    path.issue_numbers[i], 
                    {
                        "title": f"[TODO] '{path.path.removeprefix("./")}'",
                        "body": f"- {link}\n - '{path.author_comments[i]}'\n",
                        "state": "open",
                    }
                )
            else:
                print(f"Create issue: {path.issue_numbers[i]}")
                create_issue(repo, token, f"[TODO] '{path.path.removeprefix("./")}'", f"- {link}\n - {path.author_comments[i]}\n")

    print("Done updating issues.")

if __name__ == "__main__":
    main()
