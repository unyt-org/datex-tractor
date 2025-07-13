import os
import time

from datex_tractor import TodoContext
from datex_tractor import get_issues, close_issue, reopen_issue, update_issue, create_issue

def main():
    # Get issues
    token = os.environ["GITHUB_TOKEN"]
    repo = os.environ["GITHUB_REPOSITORY"]
    print("Fetching issues...")
    issues = get_issues(repo, token)

    if len(issues) > 0:
        issue_counter = max([issue["number"] for issue in issues])
        issue_counter += 1
    else:
        # If no issues yet, leave first one for todo-list-issue
        issue_counter = 2

    # Get paths 
    todo_paths = TodoContext.initialize_paths(".", issue_counter)
    todo_paths.sort(key=lambda x: x.path)

    # Update readme if applicable
    print(f"Readme_sentinel exit code: {TodoContext.readme_sentinel(issue_counter)}")

    print("Editing files...")
    # Insert issue numbers
    for path in todo_paths:
        with open(path.path) as f:
            reader = f.readlines()
            lines = [line for line in reader]

        for i, new_line in enumerate(path.lines):
            lines[path.line_numbers[i]] = new_line if new_line.endswith("\n") else new_line + "\n"

        with open(path.path, "w") as f:
            f.write("".join([line for line in lines]))

if __name__ == "__main__":
    main()
