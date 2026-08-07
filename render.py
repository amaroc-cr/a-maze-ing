import sys
import time

from maze import Maze

RGB = tuple[int, int, int]
Pixel = tuple[RGB, str]
Grid = list[list[Pixel]]
Theme = dict[str, RGB]

THEMES: dict[str, Theme] ={
    "grass": {
        "wall": (125, 140, 72),
        "floor": (255, 247, 224),
        "entry": (165, 214, 167),
        "exit": (255, 171, 145),
        "path": (255, 224, 130),
    },
    "grass night": {
        "wall": (166, 186, 93),
        "floor": (25, 29, 105),
        "entry": (217, 147, 35),
        "exit": (51, 122, 56),
        "path": (142, 222, 209),
    }
}


RESET = "\033[0m"
CLEAR = "\033[2J\033[H"
HOME = "\033[H"
HIDE_CURSOR = "\033[?251"
SHOW_CURSOR = "\033[?25h"


def bg(rgb) -> str:
    r, g, b = rgb
    return f"\033[48;2;{r};{g};{b}m"


def block(rgb, text="  ") -> str:
    return f"{bg(rgb)}{text}{RESET}"


def draw_grid(maze: Maze, theme: Theme) -> Grid:
    W = maze._width -2
    H = maze._height - 2
    grid = [[(theme["floor"], "  ") for _ in range(W * 2 + 1)] for _ in range(H * 2 + 1)]

    for row in range(H):
        for col in range(W):
            cell = maze._maze[row + 1][col + 1]
            gr, gc = row * 2 + 1, col * 2 + 1

            #corners
            grid[gr - 1][gc - 1] = (them["wall"], "  ")
            grid[gr - 1][gc + 1] = (them["wall"], "  ")
            grid[gr + 1][gc - 1] = (them["wall"], "  ")
            grid[gr + 1][gc + 1] = (them["wall"], "  ")

            #walls
            if cell.n:
                grid[gr - 1][gc] = (them["wall"], "  ")
            if cell.s:
                grid[gr + 1][gc] = (them["wall"], "  ")
            if cell.w:
                grid[gr][gc - 1] = (them["wall"], "  ")
            if cell.e:
                grid[gr][gc + 1] = (them["wall"], "  ")

    #entry and exit
    entry_r, entry_c = maze._entry[0] - 1, maze._entry[1] - 1
    exit_r, exit_c = maze._exit[0] - 1, maze._exit[1] - 1

    grid[entry_r * 2 + 1][entry_c * 2 + 1] = (theme["entry"], "  ")
    grid[exit_r * 2 + 1][exit_c * 2 + 1] = (theme["exit"], "  ")

    return grid


def path_cells(maze: Maze) -> list[tuple[int, int]]:
    if not maze._path:
        return []
    
    row, col = maze._entry
    cells = [(row - 1, col - 1)]
    for move in maze._path:
        if move == "N":
            row -= 1
        elif move == "S":
            row += 1
        elif move == "E":
            col += 1
        elif move == "W":
            col -= 1
        cells.append((row - 1, col - 1))
    return cells


def grid_to_strings(grid: Grid) -> list[str]:
    return ["".join(block(rgb, text) for rgb, text in row) for row in grid]


def render(maze: Maze, theme_name: str = "grass", show_path: bool = False) -> str:
    theme = THEMES[theme_name]
    grid = draw_grid(maze)

    if show_path:
        for r, c in path_cells(maze):
            grid[r * 2 + 1][c * 2 + 1] = (theme["path"], " +")

    return "\n".join(grid_to_strings(grid)) + "\n"


def render_anima(maze: Maze, theme_name: str = "grass", delay: float = 0.04) -> None:
    theme = THEMES[theme_name]
    grid = draw_grid(maze)

    sys.stdout.write(HIDE_CURSOR)
    sys.stdout.write(grid_to_strings(grid))
    sys.stdout.flush()

    for r, c in path_cells(maze):
        grid[r * 2 + 1][c * 2 + 1] = (theme["path"], " +")
        sys.stdout.write(HOME + grid_to_strings(grid))
        sys.stdout.flush()
        time.sleep(delay)

    sys.stdout.write("\n" + SHOW_CURSOR)
    sys.stdout.flush()


def new_maze(width: int, height: int, entry: tuple[int, int],
    exit: tuple, perfect: bool) -> Maze:
    return Maze(width, height, entry, exit, perfect)