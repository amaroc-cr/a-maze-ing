import sys
import parsing
from maze import Maze

def main() -> None:
    if len(sys.argv) < 2 or len(sys.argv) >= 3:
        print("Usage: a_maze_ing.py <file>")
    else:
        config_file = sys.argv[1]
        try:
            maze_specs = parsing.parse_config(config_file)
        except parsing.ConfigError as e:
            print(e)
        maze = Maze(
            maze_specs["WIDTH"],
            maze_specs["HEIGHT"],
            maze_specs["ENTRY"],
            maze_specs["EXIT"],
            maze_specs["PERFECT"]
        )
        output_file = maze_specs["OUTPUT_FILE"]
        f = open(output_file, "w")
        f.write(str(maze))

if __name__ == "__main__":
    main()
