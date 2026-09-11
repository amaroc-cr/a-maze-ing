import sys
import parsing

from maze import Maze
from render import THEMES
from menu import run_menu


def main() -> None:
    if len(sys.argv) < 2 or len(sys.argv) >= 3:
        print("Usage: a_maze_ing.py <file>")
    else:
        config_file = sys.argv[1]
        try:
            maze_specs = parsing.parse_config(config_file)
            maze = Maze(
                        maze_specs["WIDTH"],
                        maze_specs["HEIGHT"],
                        maze_specs["ENTRY"],
                        maze_specs["EXIT"],
                        maze_specs["PERFECT"]
                    )
        except parsing.ConfigError as e:
            print(e)
            sys.exit(1)
        output_file = maze_specs["OUTPUT_FILE"]
        f = open(output_file, "w")
        f.write(str(maze))
        f.close()
        run_menu(maze, maze_specs, list(THEMES.keys()))


if __name__ == "__main__":
    main()
