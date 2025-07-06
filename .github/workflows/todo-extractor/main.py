import os
import sys
import json
import urllib.request

from todo_context import TodoContext
from gethub import get_issues, close_issue, reopen_issue, update_issue

def get_todo_list_desc():
    src_path = "."
    todo_paths = list(TodoContext.initialize_paths(src_path))
    todo_paths.sort(key=lambda x: x.path)

    if len(todo_paths) == 0:
        print("Bot did not find anything to do")
        return 1

    total_count = sum([
        1
        for todo_path in todo_paths
        for line_number in todo_path.line_numbers
        ])

    # Create descrtiption
    desc = f"- {len(todo_paths)} files to do.\n"
    desc += f"- {total_count} expressions matched.\n\n"

    for todo_path in todo_paths:
        desc += f"## '{todo_path.path}'\n"
        for line_number, line in zip(todo_path.line_numbers, todo_path.matched_lines):
            desc += f"- {line_number}: '{line}'\n"

    desc += "\n"
    return desc

def readme_sentinel():
    todo_list_string = get_todo_list_desc()
    if todo_list_string == 1:
        print("Creation of todo list failed")
        return 1

    lines = []
    with open("README.md", mode="r", encoding="utf-8") as f:
        reader = f.readlines()
        lines = [line for line in reader]
    
    # Remember last line and increment it a priori
    try:
        last_line = int(lines[-1].strip()) + 1
    except Exception:
        print("Can't find number in last line of readme.")
        return 1

    # Match sentinel index
    todo_sentinel_start = "# Todo-section"
    matches = [(i, line) for i, line in enumerate(lines) if line.startswith(todo_sentinel_start)]

    if len(matches) != 1:
        print("Clear resolution of sentinel header failed")
        return 1

    # Unpack index
    header_line, _ = matches[0]

    # Cut off after sentinel index
    lines = lines[:header_line + 2]
    lines.append(todo_list_string)

    # Append incremted remembered last line
    lines.append(str(last_line))

    # Overwrite old sentinel
    with open("README.md", mode="w", encoding="utf-8") as f:
        f.write("".join([str(line) for line in lines]))

    return 0

def main():
    # If nothing to do just exit
    desc = get_todo_list_desc()
    if desc == 1:
        print("Exit on error, found nothing to do")
        sys.exit()
    else:
        print(desc)

    # Update readme
    print(f"readme_sentinel exit code: {readme_sentinel()}")

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
