import os
import sys
import time

from datex_tractor_module import TodoContext, get_issues, get_discussions
from datex_tractor_module import close_issue, reopen_issue, update_issue, create_issue


def main():
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        sys.exit("Unresolved CLA. (commit hash, model shorthand)")

    # Load in model
    try:
        from datex_tractor_module import Prompt
        from datex_tractor_module.datab import DBcrud
    except Exception:
        Prompt = None
        DBcrud = None
    else:
        llm, instruction = Prompt.load_model()
        db = DBcrud()
        db.create()

    # Get auth
    try:
        token = os.environ["GITHUB_TOKEN"]
        repo = os.environ["GITHUB_REPOSITORY"]
    except Exception:
        sys.exit("Unresolved environment variables for repo or token")

    # print("Fetching issues...")
    issues = get_issues(repo, token)
    discussions = get_discussions(repo, token)

    # Set initial index for enumerating issues in source code
    if len(issues) > 0:
        issue_counter = max(
            [issue["number"] for issue in issues] + [disc["number"] for disc in discussions]
        )
        issue_counter += 1
    else:
        issue_counter = 1

    # Returns int(1) if nothing to do
    desc = TodoContext.get_todo_listed_issues(".", issue_counter)
    if desc != 1:
        desc = "# Checking todos...\n" + desc

    todo_paths = list(TodoContext.extract_codeblocks(".", issue_counter))
    todo_paths.sort(key=lambda x: x.path)

    # Logic for todos list Filter by title, check state, set to open, and update either way
    found_todos = False
    todos_id = None

    for issue in issues:

        # Check todo list by title
        if issue["title"] == "Todos":
            found_todos = True
            todos_id = issue["number"]

            # If open list and something to do update
            if issue["state"] == "open" and desc != 1:
                update_issue(
                    repo,
                    token,
                    issue["number"],
                    fields={"body": desc}
                )

            # If open list but nothing to do close existing listed issues
            elif issue["state"] == "open" and desc == 1:
                lines = issue["body"].splitlines()
                issues_in_list = [line.removeprefix("- Id: #") for line in lines if line.startswith("- Id: #")]

                for id in issues_in_list:
                    time.sleep(1)
                    close_issue(repo, token, int(id))

            # If closed list and something to do reopen by updating
            elif issue["state"] == "closed" and desc != 1:
                update_issue(
                    repo,
                    token,
                    issue["number"],
                    fields={"state": "open", "body": desc}
                )

    # Create issues
    base_url = f"https://github.com/{repo}/blob/{sys.argv[1]}"
    issue_numbers = [int(issue["number"]) for issue in issues]

    for path in todo_paths:
        for i, line_number in enumerate(path.line_numbers):

            if int(path.issue_numbers[i]) not in issue_numbers:
                # print(f"Create placeholder issue: {path.issue_numbers[i]}")
                time.sleep(1)
                create_issue(
                    repo,
                    token,
                    f"[TODO] Placeholder",
                    f"To be replaced (Rerun datex-tractor workflow for update)."
                )
                # Insert into database...
                if Prompt:
                    code_block = "".join(path.code_blocks[i][2])
                    db.enter(
                        path.issue_numbers[i],
                        path.path,
                        code_block,
                    )

    # WIP: Generate answers here
    if Prompt:
        for path in todo_paths:
            for i, line_number in enumerate(path.line_numbers):
                code_block = "".join(path.code_blocks[i][2])
                text_output = Prompt.gen_advice(llm, instruction, code_block)
                db.enter_advice(
                    path.issue_numbers[i],
                    text_output,
                )

    # Checking issues after creation
    time.sleep(1)
    made_issues = get_issues(repo, token)

    # Preprocssing before updating
    todo_ids = [int(issue["number"]) for issue in made_issues if "todo" in issue["labels"]]
    new_issues = [int(issue["number"]) for issue in made_issues if int(issue["number"]) not in issue_numbers]
    all_issue_numbers = issue_numbers + new_issues

    for path in todo_paths:
        for i, line_number in enumerate(path.line_numbers):
            # Set permalink to specific commit, filepath and line number
            link = f"{base_url}/{path.path.removeprefix("./")}#L{line_number + 1}"

            if int(path.issue_numbers[i]) in all_issue_numbers:
                # print(f"Update issue: {path.issue_numbers[i]}")

                try:
                    todo_ids.remove(int(path.issue_numbers[i]))
                except ValueError:
                    pass

                # Generate advice
                # WIP: replace with retrieval from db
                if Prompt:
                    text_output = db.get_block(path.issue_numbers[i])

                    # Prepare body...
                    update_issue(
                        repo,
                        token,
                        path.issue_numbers[i],
                        {
                            "title": f"[TODO] '{path.path.removeprefix("./")}'",
                            "body": f"- {link}\n{str(text_output.response)}\n",
                            "state": "open",
                            "labels": ["todo"],
                        }
                    )
                else:
                    # Update without text_outupt if model not loaded
                    time.sleep(1)
                    update_issue(
                        repo,
                        token,
                        path.issue_numbers[i],
                        {
                            "title": f"[TODO] '{path.path.removeprefix("./")}'",
                            "body": f"- {link}\n",
                            "state": "open",
                            "labels": ["todo"],
                        }
                    )

    # Create or close to do list
    if found_todos == True and desc == 1:
        # Closing todo list if nothing to do
        close_issue(repo, token, todos_id)

    if not found_todos or found_todos == False:
        # Creating new todo-list issue
        create_issue(
            repo,
            token,
            title="Todos",
            body=desc,
            labels=["documentation"]
        )

    # After all paths are updated, check back if any todos remain not updated
    # Conclude not updated todo-issues have been removed from source code
    if len(todo_ids) <= 0:
        # print("No outdated todos")
        return 0
    else:
        for disappeared_todo in todo_ids:
            # print(f"Label issue {disappeared_todo} as disappeared-todo")
            time.sleep(1)
            update_issue(
                repo,
                token,
                disappeared_todo,
                {
                    "labels": ["disappeared-todo"],
                }
            )

    # print("Done labeling disappeared todos")
    return 0


if __name__ == "__main__":
    main()
