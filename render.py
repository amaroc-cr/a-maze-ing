import sys
import time
import shutil

from maze import Maze

RGB = tuple[int, int, int]
Pixel = tuple[RGB, str]
Grid = list[list[Pixel]]
Theme = dict[str, RGB]

THEMES: dict[str, Theme] = {
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
HIDE_CURSOR = "\033[?25l"
SHOW_CURSOR = "\033[?25h"


def rendered_size(maze: Maze) -> tuple[int, int]:
    """Compute the terminal size needed to render a maze.

    Each interior maze cell becomes a 2x2 block of terminal cells (with
    shared walls), and width is doubled again since each rendered pixel
    is drawn as two characters wide.

    Args:
        maze: The maze to measure.

    Returns:
        A (rows, cols) tuple of the terminal size required to render
        the maze without clipping.
    """
    height = (maze.height - 2) * 2 + 1
    width = ((maze.width - 2) * 2 + 1) * 2
    return height, width


def fits_terminal(maze: Maze) -> bool:
    """Check whether the rendered maze fits within the current terminal window.

    Args:
        maze: The maze to check.

    Returns:
        True if the terminal is large enough to display the maze
        without clipping, False otherwise.
    """
    term_cols, term_rows = shutil.get_terminal_size()
    needed_rows, needed_cols = rendered_size(maze)
    return needed_rows <= term_rows and needed_cols <= term_cols


def coloring(rgb: RGB) -> str:
    """Build an ANSI escape code that sets the maze tile to an RGB color.

    Args:
        rgb: An (r, g, b) tuple with each component in 0-255.

    Returns:
        The ANSI truecolor background escape sequence for that color.
    """
    r, g, b = rgb
    return f"\033[48;2;{r};{g};{b}m"


def block(rgb: RGB, text: str = "  ") -> str:
    """Wrap text in an ANSI background color, resetting styling afterward.

    Args:
        rgb: An (r, g, b) tuple giving the background color.
        text: The text to color (defaults to two spaces, i.e. a solid
            colored block).

    Returns:
        The text wrapped with the background color escape code and a
        trailing reset code.
    """
    return f"{coloring(rgb)}{text}{RESET}"


def draw_grid(maze: Maze, theme: Theme) -> Grid:
    """Build a pixel grid representing a maze's walls, floor, entry, and exit.

    Each maze cell is expanded into a 2x2 region of pixels so walls can
    be drawn between cells; corners default to wall color. The grid
    excludes the maze's outer border (row/col 0) since that is assumed
    to be the boundary wall.

    Args:
        maze: The maze to draw.
        theme: Color theme providing "wall", "floor", "entry", and
            "exit" RGB colors.

    Returns:
        A 2D grid of (rgb, text) pixels ready to be turned into strings.
    """
    W = maze.width - 2
    H = maze.height - 2
    grid = (
        [[(theme["floor"], "  ") for _ in range(W * 2 + 1)]
         for _ in range(H * 2 + 1)]
         )

    for row in range(H):
        for col in range(W):
            cell = maze.maze[row + 1][col + 1]
            gr, gc = row * 2 + 1, col * 2 + 1

            # corners
            grid[gr - 1][gc - 1] = (theme["wall"], "  ")
            grid[gr - 1][gc + 1] = (theme["wall"], "  ")
            grid[gr + 1][gc - 1] = (theme["wall"], "  ")
            grid[gr + 1][gc + 1] = (theme["wall"], "  ")

            # walls
            if cell.n:
                grid[gr - 1][gc] = (theme["wall"], "  ")
            if cell.s:
                grid[gr + 1][gc] = (theme["wall"], "  ")
            if cell.w:
                grid[gr][gc - 1] = (theme["wall"], "  ")
            if cell.e:
                grid[gr][gc + 1] = (theme["wall"], "  ")

    # entry and exit
    entry_r, entry_c = maze.entry[0] - 1, maze.entry[1] - 1
    exit_r, exit_c = maze.exit[0] - 1, maze.exit[1] - 1

    grid[entry_r * 2 + 1][entry_c * 2 + 1] = (theme["entry"], "  ")
    grid[exit_r * 2 + 1][exit_c * 2 + 1] = (theme["exit"], "  ")

    return grid


def path_cells(maze: Maze) -> list[tuple[int, int]]:
    """Compute the interior (row, col) cells along the maze's solution path.

    Walks maze.path (a sequence of "N"/"S"/"E"/"W" moves) starting from
    the entry cell, converting each visited cell to 0-based coordinates
    relative to the maze interior (i.e. excluding the outer border).
    The entry and exit cells themselves are excluded from the result.

    Args:
        maze: The maze whose solution path to trace. If it has no
            path set, an empty list is returned.

    Returns:
        A list of (row, col) interior coordinates for each cell on the
        path between (but not including) entry and exit.
    """
    if not maze.path:
        return []

    row, col = maze.entry
    cells = [(row - 1, col - 1)]
    for move in maze.path:
        if move == "N":
            row -= 1
        elif move == "S":
            row += 1
        elif move == "E":
            col += 1
        elif move == "W":
            col -= 1
        cells.append((row - 1, col - 1))

    return cells[1:-1]


def grid_to_strings(grid: Grid) -> list[str]:
    """Convert a pixel grid into printable, colored terminal lines.

    Args:
        grid: A 2D grid of (rgb, text) pixels, as produced by draw_grid.

    Returns:
        A list of strings, one per grid row, each containing the ANSI
        color codes needed to render that row's pixels.
    """
    return ["".join(block(rgb, text) for rgb, text in row) for row in grid]


def render(maze: Maze, theme_name: str = "grass",
           show_path: bool = False) -> str:
    """Render a maze as a single colored string ready to print.

    Args:
        maze: The maze to render.
        theme_name: Key into THEMES selecting the color palette to use.
        show_path: If True, overlay the maze's solution path in the
            theme's "path" color.

    Returns:
        A multi-line string (terminating in a newline) containing the
        maze rendered with ANSI background-color escape codes.
    """
    theme = THEMES[theme_name]
    grid = draw_grid(maze, theme)

    if show_path:
        for r, c in path_cells(maze):
            grid[r * 2 + 1][c * 2 + 1] = (theme["path"], "  ")

    return "\n".join(grid_to_strings(grid)) + "\n"


def render_anima(maze: Maze, theme_name: str = "grass",
                 delay: float = 0.04) -> None:
    """Render a maze to the terminal, animate solution path being drawn.

    Draws the maze once, then reveals the solution path one cell at a
    time by redrawing the grid in place (using cursor-home, not a full
    clear) with a short delay between frames. Hides the cursor during
    the animation and shows it again afterward. Writes directly to
    stdout rather than returning a string.

    Args:
        maze: The maze to render and animate.
        theme_name: Key into THEMES selecting the color palette to use.
        delay: Seconds to pause between revealing each path cell.
    """
    theme = THEMES[theme_name]
    grid = draw_grid(maze, theme)

    sys.stdout.write(CLEAR + HIDE_CURSOR)
    sys.stdout.write('\n'.join(grid_to_strings(grid)))
    sys.stdout.flush()

    for r, c in path_cells(maze):
        grid[r * 2 + 1][c * 2 + 1] = (theme["path"], "  ")
        sys.stdout.write(HOME + '\n'.join(grid_to_strings(grid)))
        sys.stdout.flush()
        time.sleep(delay)

    sys.stdout.write("\n" + SHOW_CURSOR)
    sys.stdout.flush()


def new_maze(width: int, height: int, entry: tuple[int, int],
             exit: tuple[int, int], perfect: bool) -> Maze:
    """Construct a new Maze with the given dimensions and options.

    Args:
        width: Maze width in cells (including border).
        height: Maze height in cells (including border).
        entry: (x, y) coordinate of the maze entrance.
        exit: (x, y) coordinate of the maze exit.
        perfect: If True, generate a "perfect" maze (exactly one path
            between any two cells, no loops).

    Returns:
        A newly generated Maze instance.
    """
    return Maze(width, height, entry, exit, perfect)
