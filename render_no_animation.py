import sys
import select
import termios
import tty
#import random
import time

from maze import Maze

RGB = tuple[int, int, int]
Pixel = tuple[RGB, str]
Grid = list[list[Pixel]]

WALL_SEG = (194, 217, 111)
FLOOR = (25, 29, 105)
ENTRY = (217, 147, 35)
EXIT = (51, 122, 56)
PATH = (142, 222, 209)


RESET = "\033[0m"


def bg(rgb) -> str:
    r, g, b = rgb
    return f"\033[48;2;{r};{g};{b}m"


def block(rgb, text="  ") -> str:
    return f"{bg(rgb)}{text}{RESET}"


def print_grid(maze: Maze) -> tuple[Grid, int, int]:
    W = maze._width -2
    H = maze._height - 2
    grid = [[(FLOOR, "  ") for _ in range(W * 2 + 1)] for _ in range(H * 2 + 1)]

    for row in range(H):
        for col in range(W):
            cell = maze._maze[row + 1][col + 1]
            gr, gc = row * 2 + 1, col * 2 + 1

            #corners
            grid[gr - 1][gc - 1] = (WALL_SEG, "  ")
            grid[gr - 1][gc + 1] = (WALL_SEG, "  ")
            grid[gr + 1][gc - 1] = (WALL_SEG, "  ")
            grid[gr + 1][gc + 1] = (WALL_SEG, "  ")

            if cell.n:
                grid[gr - 1][gc] = (WALL_SEG, "  ")
            if cell.s:
                grid[gr + 1][gc] = (WALL_SEG, "  ")
            if cell.w:
                grid[gr][gc - 1] = (WALL_SEG, "  ")
            if cell.e:
                grid[gr][gc + 1] = (WALL_SEG, "  ")

    return grid, H, W


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


def grid_to_lines(grid: Grid) -> list[str]:
    return ["".join(block(rgb, text) for rgb, text in row) for row in grid]


def is_data() -> bool:
    return select


def render(maze: Maze) -> str:
    grid, H, W = print_grid(maze)

    entry_r, entry_c = maze._entry[0] - 1, maze._entry[1] - 1
    exit_r, exit_c = maze._exit[0] - 1, maze._exit[1] - 1

    for r, c in path_cells(maze):
        grid[r * 2 + 1][c * 2 + 1] = (PATH, "  ")
    
    grid[entry_r * 2 + 1][entry_c * 2 + 1] = (ENTRY, "  ")
    grid[exit_r * 2 + 1][exit_c * 2 + 1] = (EXIT, "  ")

    return "\n".join(grid_to_lines(grid)) + "\n"
