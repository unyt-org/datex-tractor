import os
import sys

from datex_tractor import TodoContext
from datex_tractor import get_issues, close_issue, reopen_issue, update_issue, create_issue

def main():
    # Get issues
    token = os.environ["GITHUB_TOKEN"]
    repo = os.environ["GITHUB_REPOSITORY"]
    issues = get_issues(repo, token)

    # Setting start point for new indices
    max_issue_idx = max([issue["number"] for issue in issues])
    max_issue_idx += 1


    # Get paths 
    todo_paths = TodoContext.initialize_paths(".", max_issue_idx)

    # Insert issue numbers
    for path in todo_paths:
        with open(path.path) as f:
            reader = f.readlines()
            lines = [line for line in reader]

        for i, new_line in enumerate(path.lines):
            lines[path.line_numbers[i]] = new_line if new_line.endswith("\n") else new_line + "\n"

        with open(path.path, "w") as f:
            f.write("".join([line for line in lines]))

    # Create or Update issues
    for path in todo_paths:
        for i, line_number in enumerate(path.line_numbers):
            filename = path.path
            try:
                _, filename = path.path.rsplit("/")
            except Exception:
                pass

            title = f"{line_number}: {filename}"
            body = f"- {path.matched_lines[i]}\n- {path.author_comments[i]}\n",
            if int(path.issue_numbers[i]) in [issue["number"] for issue in issues]:
                print("Update issue: ", path.issue_numbers[i])

                update_issue(
                    repo, 
                    token, 
                    path.issue_numbers[i], 
                    {"title": title, "body": body},
                )
            else:
                print("Create issue: ", path.issue_numbers[i])
                create_issue(repo, token, title, body)

    # Returns int(1) if nothing to do
    desc = TodoContext.get_todo_listed_issues()
    if desc != 1:
        desc = "# Checking todos...\n" + desc
    print(desc)

    # Update readme
    print(f"readme_sentinel exit code: {TodoContext.readme_sentinel()}")

    # Create todo list issue
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
        print(f"Creating new todo list issue.")
        create_issue(repo, token, title="Todos", body=desc)

if __name__ == "__main__":
    main()
