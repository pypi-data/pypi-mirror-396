import shutil
import sys
import textwrap

import colorama

from . import PROJECT_SCRIPTS_ROOT, TAG_ERROR, TAG_SCRIPT, USER_SCRIPTS_ROOT
from .script import Script, discover_project_scripts, discover_user_scripts


def main() -> None:
    colorama.init(autoreset=True)

    # Discover scripts
    try:
        project_scripts = discover_project_scripts(PROJECT_SCRIPTS_ROOT)
        user_scripts = discover_user_scripts(USER_SCRIPTS_ROOT)
    except ValueError as e:
        print(colorama.Fore.RED + TAG_ERROR, str(e))
        sys.exit(1)

    # Print usage if no script name is provided
    if len(sys.argv) == 1:
        usage(project_scripts, user_scripts)
        return

    # Find target script in discovered scripts
    script_name = sys.argv[1]
    if script_name in project_scripts:
        script_info = project_scripts[script_name]
    elif script_name in user_scripts:
        script_info = user_scripts[script_name]
    else:
        usage(project_scripts, user_scripts)  # print usage if not found
        return

    # Print info and run script
    print(colorama.Fore.GREEN + TAG_SCRIPT, f"{script_name} ({script_info.path})")
    try:
        script_info.run(sys.argv[2:])
    except Exception as e:
        print(colorama.Fore.RED + TAG_ERROR, str(e))


def wrap_text(text: str, width: int, indent: int = 6) -> list[str]:
    """Wrap text to specified width with indentation, preserving paragraphs"""
    result = []
    paragraphs = text.strip().split("\n\n")
    for paragraph in paragraphs:
        lines = paragraph.strip().split("\n")
        cleaned_lines = []
        for line in lines:
            cleaned_line = " ".join(line.strip().split())
            if cleaned_line:
                cleaned_lines.append(cleaned_line)
        paragraph_text = " ".join(cleaned_lines)
        wrapped_lines = textwrap.wrap(paragraph_text, width=width - indent)
        for line in wrapped_lines:
            result.append(f"{' ' * indent}{line}")
        if paragraph != paragraphs[-1]:
            result.append("")
    return result


def usage(project_scripts: dict[str, Script], user_scripts: dict[str, Script]) -> None:
    print(colorama.Fore.RED + "Usage: pylon <script-name> [args...]")
    print("")
    print("Pylon is a script runner that searches for scripts in the following order:")
    print(f"  1. Current (project) directory ({PROJECT_SCRIPTS_ROOT})")
    print(f"  2. User scripts directory ({USER_SCRIPTS_ROOT})")
    print("and runs the first script with the following args.")
    print("")
    print("Available scripts:")

    terminal_width = shutil.get_terminal_size().columns

    for name, info in sorted(project_scripts.items()):
        location = "project" if info.project_dir is None else "project-dir"
        print("  -", colorama.Fore.CYAN + name, f"({location}, {info.path})")
        if info.docstring:
            # Wrap docstring to terminal width
            wrapped_lines = wrap_text(info.docstring, terminal_width)
            for line in wrapped_lines:
                print(line)

    for name, info in sorted(user_scripts.items()):
        location = "user" if info.project_dir is None else "user-dir"
        print("  -", colorama.Fore.CYAN + name, f"({location}, {info.path})")
        if info.docstring:
            # Wrap docstring to terminal width
            wrapped_lines = wrap_text(info.docstring, terminal_width)
            for line in wrapped_lines:
                print(line)

    if not project_scripts and not user_scripts:
        print("  No scripts found.")
    print("")


if __name__ == "__main__":
    main()
