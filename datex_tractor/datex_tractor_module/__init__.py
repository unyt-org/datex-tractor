from .todo_context import TodoContext
from .gethub import get_issues, get_discussions, close_issue, reopen_issue, update_issue, create_issue
import sys

if len(sys.argv) == 2 or len(sys.argv) != 3:
    __all__ = [
        "TodoContext",
        "get_discussions",
        "get_issues",
        "close_issue",
        "reopen_issue",
        "update_issue",
        "create_issue",
    ]
else:
    match sys.argv[2]:
        case "hrms":
            try:
                from .hrms import Prompt

            except Exception:
                raise NotImplementedError("Missing dependency")

            else:
                __all__ = [
                    "TodoContext",
                    "get_discussions",
                    "get_issues",
                    "close_issue",
                    "reopen_issue",
                    "update_issue",
                    "create_issue",
                    "Prompt",
                ]
        case "dpsk":
            try:
                from .dpsk import Prompt

            except Exception:
                raise NotImplementedError("Missing dependency")

            else:
                __all__ = [
                    "TodoContext",
                    "get_discussions",
                    "get_issues",
                    "close_issue",
                    "reopen_issue",
                    "update_issue",
                    "create_issue",
                    "Prompt",
                ]
        case _:
            sys.exit()
