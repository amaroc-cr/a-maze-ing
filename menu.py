import sys

from maze import Maze
from render import THEMES, fits_terminal, render, render_anima, CLEAR, HIDE_CURSOR, SHOW_CURSOR


MENU_TEXT = """
1. Re-generate maze
2. Show/hide shortest path
3. Rotate wall colors
4. Quit
"""


def print_menu() -> None:
    """Print the interactive menu options to stdout."""
    print(MENU_TEXT)


def get_choice() -> int:
    """Prompt the user until a valid menu choice (1-4) is entered.
 
    Returns:
        The chosen option as an integer between 1 and 4.
    """
    while True:
        raw = input("Choose an option (1-4): ").strip()
        if raw in ("1", "2", "3", "4"):
            return int(raw)
        print("Invalid choice, please enter a number between 1 and 4.")


def run_menu(maze: Maze, maze_specs: dict, theme_names: list[str]) -> None:
    """Run the interactive terminal loop for viewing and manipulating a maze.
 
    Renders the current maze (animating the solution path on
    first display), shows the menu, and dispatches the user's choice:
    regenerating the maze, toggling the shortest-path display, cycling
    through wall color themes, or quitting. The cursor is hidden while
    the menu is active and always restored on exit, even if an exception
    occurs.
 
    Args:
        maze: The Maze instance currently being displayed.
        maze_specs: Config dict (as produced by parse_config) used to
            regenerate a new maze and to know where to write it
            (must contain WIDTH, HEIGHT, ENTRY, EXIT, PERFECT, OUTPUT_FILE).
        theme_names: Ordered list of theme names to cycle through, each
            of which must be a key in render.THEMES.
    """
    theme_nbr = 0
    show_path = True
    animate_new = True

    try:
        while True:
            theme_name = theme_names[theme_nbr]
            sys.stdout.write(HIDE_CURSOR)
            sys.stdout.write(CLEAR)
            if not fits_terminal(maze):
                print("Terminal window is too small to display this maze.")
                print("Resize/maximize terminal, or use a smaller WIDTH/HEIGHT in config.")
            elif animate_new and show_path:
                render_anima(maze, theme_name)
            else:
                print(render(maze, theme_name, show_path))
            if maze._width < 11 or maze._height < 9:
                print("\n(Maze too small for 42 logo)")     
            print_menu()
            sys.stdout.write(SHOW_CURSOR)
            choice = get_choice()
            animate_new = False

            if choice == 1:
                maze = Maze(
                    maze_specs["WIDTH"],
                    maze_specs["HEIGHT"],
                    maze_specs["ENTRY"],
                    maze_specs["EXIT"],
                    maze_specs["PERFECT"]
                )
                with open(maze_specs["OUTPUT_FILE"], "w") as f:
                    f.write(str(maze))
                animate_new = True
            elif choice == 2:
                show_path = not show_path
            elif choice == 3:
                theme_nbr = (theme_nbr + 1) % len(theme_names)
            elif choice == 4:
                break
    finally:
        sys.stdout.write(SHOW_CURSOR)
