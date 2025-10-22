import os
import sys
from datex_tractor_module import TodoContext, get_issues, get_discussions


def main():
    # Get issues
    token = os.environ["GITHUB_TOKEN"]
    repo = os.environ["GITHUB_REPOSITORY"]
    print("Fetching issues...")
    issues = get_issues(repo, token)
    discussions = get_discussions(repo, token)

    if len(issues) > 0:
        issue_counter = max(
            [issue["number"] for issue in issues] + [disc["number"] for disc in discussions]
        )
        issue_counter += 1
    else:
        issue_counter = 1

    # Get paths
    todo_paths = list(TodoContext.initialize_paths(".", issue_counter))
    todo_paths.sort(key=lambda x: x.path)

    print("Editing files...")
    # Insert issue numbers into source code
    for path in todo_paths:
        with open(path.path) as f:
            reader = f.readlines()
            lines = [line for line in reader]

        for i, new_line in enumerate(path.lines):
            lines[path.line_numbers[i]] = new_line if new_line.endswith("\n") else new_line + "\n"

        with open(path.path, "w") as f:
            f.write("".join([line for line in lines]))

    return 0


def finish_project():
    """Removes todo-comments including rusts todo-makros"""
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
        issue_counter = 1

    if 0 == TodoContext.remove_todos(issue_counter):
        return 0
    else:
        # print("Failed to remove issue ID's")
        return 1


if __name__ == "__main__":
    if len(sys.argv) < 2:
        main()
    elif len(sys.argv) == 2:
        finish_project()
