*This project has been created as part of the 42 curriculum by yuhma and lvan-win.*

# Description

A-Maze-ing is a configurable maze generating program written in Python. Given a plain-text configuration file, it builds a maze of the requested dimensions, computes the shortest path between the entry and the exit, and writes the result to a file using a hexadecimal wall encoding — one digit per cell, one line per row.

The generator supports two modes. In perfect mode it produces a maze with exactly one route between any two cells: this means there are no loops possible. In the default non-perfect mode it produces a board suitable for a Pac-Man-style game — fully connected and with no dead-ends, with several independent routes so a chased player always has an escape. Every maze also contains a "42" drawn in fully closed cells, provided the requested size leaves room for it.

Alongside the file output, the program renders the maze in the terminal, letting you regenerate, toggle the solution path, and change the wall colours. The generation logic itself lives in a standalone, pip-installable module so it can be reused in later projects.

# Instructions

## Configuration file

The generator is driven by a plain-text configuration file, passed as the only
argument. Each line holds a single `KEY=VALUE` pair; lines beginning with `#`
are treated as comments and ignored.

The following keys are required:

| Key | Description | Example |
|---|---|---|
| `WIDTH` | Maze width, in cells | `WIDTH=20` |
| `HEIGHT` | Maze height, in cells | `HEIGHT=15` |
| `ENTRY` | Entry coordinates, as `x,y` | `ENTRY=0,0` |
| `EXIT` | Exit coordinates, as `x,y` | `EXIT=19,14` |
| `OUTPUT_FILE` | Name of the file to write the maze to | `OUTPUT_FILE=maze.txt` |
| `PERFECT` | Generate a perfect maze rather than a playable board | `PERFECT=True` |

Coordinates are zero-based and count from the top-left cell, so the bottom-right
cell of a 20×15 maze is `19,14`. Entry and exit must be distinct and must both
lie inside the maze.

Additionally, there are also two optional keys you can add:

| Key | Description | Example |
|---|---|---|
| `ALGORITHM` | Algorithm used for maze generation | `ALGORITHM=prim` |
| `SEED` | Seed for reproducing a maze | `SEED=42` |

A working example is included in the repository as `config.txt`.


## Running the program

### Prerequisites

- Python 3.11 or later
- `make`

### Setup

```bash
make install
```

This creates a virtual environment (`venv/`) and installs all dependencies,
including the `mazegen` package itself (in editable mode).

### Run

```bash
make run
```

This runs `a_maze_ing.py` with `config.txt` as the configuration file. To use
a different configuration file, run the program directly instead:

```bash
venv/bin/python3 a_maze_ing.py <path-to-your-config-file>
```

The maze is generated and written to the file named by `OUTPUT_FILE` in the
configuration, then an interactive menu opens in the terminal:

```
1. Re-generate maze
2. Show/hide shortest path
3. Rotate wall colors
4. Quit
```

- **Re-generate maze** builds a new random maze from the same configuration
  and overwrites the output file.
- **Show/hide shortest path** toggles the highlighted solution path.
- **Rotate wall colors** cycles through the available color themes.
- **Quit** exits the program.

### Other commands

```bash
make lint    # run flake8 and mypy
make debug   # run the program under pdb
make build   # build the mazegen package (.whl and .tar.gz)
make clean   # remove caches and build artifacts
```


## mazegen — reusable maze generator module

`mazegen` is a standalone, pip-installable package that generates a maze
and computes its shortest path from entry to exit. It has no dependency
on the rest of this repository and can be reused in any future project.

### Installation

From a built wheel:
```bash
pip install mazegen-1.0.0-py3-none-any.whl
```

Or, for local development (editable install):
```bash
pip install -e .
```

### Basic usage

```python
from mazegen import Maze

maze = Maze(
    width=20,
    height=15,
    entry=(0, 0),
    exit=(19, 14),
    perfect=True,
)

print(maze.path)  # e.g. "EESSWWSSEE..."
```

### Custom parameters

| Parameter | Type              | Default | Description |
|-----------|-------------------|---------|-------------|
| `width`   | `int`             | —       | Maze width in cells (0-based, excludes the automatic outer border) |
| `height`  | `int`             | —       | Maze height in cells |
| `entry`   | `tuple[int, int]` | —       | Entry coordinate as `(x, y)`, zero-based |
| `exit`    | `tuple[int, int]` | —       | Exit coordinate as `(x, y)`, zero-based, must differ from `entry` |
| `perfect` | `bool`            | —       | `True` for exactly one path (no loops); `False` for loops and no dead ends |
| `algo`    | `str`             | `"dfs"` | `"dfs"` or `"prim"` — algorithm used to generate a perfect maze |
| `seed`    | `str \| None`     | `None`  | Pass the same seed to reproduce the same maze; omit for a random maze |

```python
maze = Maze(
    width=10,
    height=10,
    entry=(0, 0),
    exit=(9, 9),
    perfect=False,
    algo="prim",
    seed="my-seed-42",   # same seed -> same maze every time
)
```

### Accessing the generated structure

- `maze.maze` — a `list[list[Cell]]`, the 2D grid of `Cell` objects
  (indexed `[row][col]`). Each `Cell` has `.n`, `.e`, `.s`, `.w`
  (`1` = wall present, `0` = no wall), `.visited`, `.available`.
- `maze.width`, `maze.height` — the internal grid size, including the
  1-cell unavailable border automatically added around the maze
  (so this is your requested `width`/`height` + 2).
- `maze.entry`, `maze.exit` — the entry/exit coordinates as stored
  internally, in `(row, col)` order and offset by the outer border.
  These are not the same tuple you passed in.

### Accessing the solution

- `maze.path` — a `str`, the shortest path from entry to exit as a
  sequence of `"N"`/`"E"`/`"S"`/`"W"` moves, e.g. `"EESSWWSSEE"`.
- `str(maze)` — the full maze in the project's output file format
  (hexadecimal wall encoding, one row per line, followed by entry,
  exit and the solution path).

### Error handling

```python
from mazegen import Maze, MazeGenError

try:
    maze = Maze(width=5, height=5, entry=(0, 0), exit=(0, 0), perfect=True)
except MazeGenError as e:
    print(f"Could not generate maze: {e}")
```

`MazeGenError` is raised for invalid parameters (bad size, out-of-bounds
or identical entry/exit, unknown algorithm, wrong types) and for
unsolvable layouts (e.g. entry/exit landing inside the "42" logo).


# Design choices

### Algorithms

#### Depth-First Search with backtracking

As our main algorithm, we chose a Depth-First Search algorithm with backtracking. Starting from the entry cell, it repeatedly picks a random unvisited neighbour, opens the wall between the two cells and moves there, carving a corridor as it goes. Every cell it moves away from is pushed onto a stack. When it reaches a cell with no unvisited neighbours left, it pops cells off that stack until it finds one that still has an unvisited neighbour, and continues from there. The maze is finished once the stack is empty, which means every reachable cell has been visited exactly once. Because no cell is ever entered twice, there is exactly one route between any two cells.

We chose DFS because it creates the most varied and best looking maze. The paths are long and winding, which makes for a good maze. Also, the algorithm also doesn't have a bias towards a certain direction.

#### Sidewinder's (not implemented)

As our second algorithm, we first tried to implement the Sidewinder algorithm, because we thought it would be interesting to also use an algorithm that is completely different than DFS. Unfortunately, the Sidewinder algorithm turned out to be incompatible with the 42-logo in the middle of the maze, because there are cells that have no valid northern neighbour to connect to. In addition, one of the cells in the '2' doesn't have a valid eastern neighbour.

#### Prim's

In the end we chose to implement Prim's algorithm as our second algorithm. It keeps a list of frontier cells: the unvisited cells that border the part of the maze built so far. Starting from the entry, it adds that cell's unvisited neighbours to the frontier, then picks one frontier cell at random, and connects it to a randomly chosen neighbour that is already part of the maze by opening the wall between them. The new cell is then marked as visited and its own unvisited neighbours join the frontier. This repeats until the frontier is empty. Because every cell is attached to the maze exactly once, by a single wall, the result is again a maze with exactly one route between any two cells.

We chose Prim's, because the maze it creates looks different than a DFS maze, but it's also very usable as a maze and doesn't have a bias towards a certain direction.

### Reusability

(What part of your code is reusable, and how.)

# Process and collaboration

◦ The roles of each team member.
- **lvan-der**: Designed the data structure for the maze and its cells; implemented
  generation of both perfect and imperfect mazes; implemented conversion to
  the hexadecimal wall-encoding file format; implemented the shortest-path
  algorithm.
- **yuhma**: Implemented configuration file parsing and validation; implemented
  the terminal visual representation (rendering, color themes, path
  animation); packaged the maze generator as the standalone, pip-installable
  `mazegen` module (parameter validation, module documentation, build
  configuration, and license).

◦ Your anticipated planning and how it evolved until the end 
- start, basic algorithm and structure, parsing and rendering was way faster than imagined. Options in input menu harder than expected. Reusable worked smoothly as it fitted our design process

◦ What worked well and what could be improved
- collaboration worked well, different tasks that were pretty well separable and we were both interested in doing our parts!
- time frame could have been planned better

◦ Have you used any specific tools? Which ones?
### Tools used

- **Git & GitHub** — version control, feature branches, pull requests for
  code review before merging into `main`.
- **flake8** — enforces PEP 8 style and catches common code issues.
- **mypy** — static type checking, using type hints throughout the codebase.
- **Pylance** — in-editor type checking and autocomplete (VS Code).
- **pytest** — unit testing.
- **Make** — automates environment setup (`make install`), running the
  program (`make run`), linting (`make lint`), and building the `mazegen`
  package (`make build`).
- **setuptools / build** — builds the `mazegen` package into a distributable
  wheel (`.whl`) and source distribution (`.tar.gz`).

# Resources

* [`Wikipedia: Maze generation algorithm`](https://en.wikipedia.org/wiki/Maze_generation_algorithm)
* [`Geeks for geeks: how to convert binary to hexadecimal`](https://www.geeksforgeeks.org/maths/how-to-convert-binary-to-hexadecimal/)
* [`Geeks for geeks: breadth first search`](https://www.geeksforgeeks.org/dsa/breadth-first-search-or-bfs-for-a-graph/)
* [`Maze Generation: Prim's Algorithm`](https://weblog.jamisbuck.org/2011/1/10/maze-generation-prim-s-algorithm)

### AI usage

We only used AI while explicitly stating that we didn't want the right answer, but we just wanted a nudge in the right direction.

We used AI to brainstorm about pros and cons of different datastructures to use for the maze and cells and also for some help while debugging and for git advice.
The first drafts of some paragraphs of this README were also written using AI.
