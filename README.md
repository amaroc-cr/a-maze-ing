*This project has been created as part of the 42 curriculum by yuhma and lvan-win.*

# Description

A-Maze-ing is a configurable maze generating program written in Python. Given a plain-text configuration file, it builds a maze of the requested dimensions, computes the shortest path between the entry and the exit, and writes the result to a file using a hexadecimal wall encoding — one digit per cell, one line per row.

The generator supports two modes. In perfect mode it produces a maze with exactly one route between any two cells: this means there are no loops possible. In the default non-perfect mode it produces a board suitable for a Pac-Man-style game — fully connected and with no dead-ends, with several independent routes so a chased player always has an escape. Every maze also contains a "42" drawn in fully closed cells, provided the requested size leaves room for it.

Alongside the file output, the program renders the maze in the terminal, letting you regenerate, toggle the solution path, and change the wall colours. The generation logic itself lives in a standalone, pip-installable module so it can be reused in later projects.

# Instructions

(containing any relevant information about compilation, installation, and/or execution)

### Configuration file

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

A working example is included in the repository as `config.txt`.


(Optional keys: SEED for reproducible output, ...)

# Design choices

### Algorithm(s)

(• The maze generation algorithm you chose.
• Why you chose this algorithm.)

### Reusability

(What part of your code is reusable, and how.)

# Process and collaboration

(• Your team and project management with:
◦ The roles of each team member. (L: designing datastructure for maze and cells, generation of the perfect and imperfect maze, conversion to hexadecimal representation in file, algorithm for finding the shortest path) (Y: parsing of configuration file, visual representation in terminal)
◦ Your anticipated planning and how it evolved until the end (start, basic algorithm and structure, parsing and rendering was way faster than imagined. Options in input menu harder than expected? reusability?)
◦ What worked well and what could be improved (collaboration worked well, different tasks that were pretty well separable)
◦ Have you used any specific tools? Which ones? (???))

# Resources

* [`Wikipedia: Maze generation algorithm`](https://en.wikipedia.org/wiki/Maze_generation_algorithm)
* [`Geeks for geeks: how to convert binary to hexadecimal`](https://www.geeksforgeeks.org/maths/how-to-convert-binary-to-hexadecimal/)
* [`Geeks for geeks: breadth first search`](https://www.geeksforgeeks.org/dsa/breadth-first-search-or-bfs-for-a-graph/)

### AI usage

We only used AI while explicitly stating that we didn't want the right answer, but we just wanted a nudge in the right direction.

We used AI to brainstorm about pros and cons of different datastructures to use for the maze and cells and also for some help while debugging.
Some first drafts for paragraphs for this README were also written using AI.
