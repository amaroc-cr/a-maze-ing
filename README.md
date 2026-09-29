*This project has been created as part of the 42 curriculum by yuhma and lvan-win.*

# Description

A-Maze-ing is a configurable maze generating program written in Python. Given a plain-text configuration file, it builds a maze of the requested dimensions, computes the shortest path between the entry and the exit, and writes the result to a file using a hexadecimal wall encoding — one digit per cell, one line per row.

The generator supports two modes. In perfect mode it produces a maze with exactly one route between any two cells: this means there are no loops possible. In the default non-perfect mode it produces a board suitable for a Pac-Man-style game — fully connected and with no dead-ends, with several independent routes so a chased player always has an escape. Every maze also contains a "42" drawn in fully closed cells, provided the requested size leaves room for it.

Alongside the file output, the program renders the maze in the terminal, letting you regenerate, toggle the solution path, and change the wall colours. The generation logic itself lives in a standalone, pip-installable module so it can be reused in later projects.

# Instructions

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

Additionally, there are also two optional keys you can add:

| Key | Description | Example |
|---|---|---|
| `ALGORITHM` | Algorithm used for maze generation | `ALGORITHM=prim` |
| `SEED` | Seed for reproducing a maze | `SEED=42` |

A working example is included in the repository as `config.txt`.

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

(• Your team and project management with:
◦ The roles of each team member. (L: designing datastructure for maze and cells, generation of the perfect and imperfect maze, conversion to hexadecimal representation in file, algorithm for finding the shortest path) (Y: parsing of configuration file, visual representation in terminal)
◦ Your anticipated planning and how it evolved until the end (start, basic algorithm and structure, parsing and rendering was way faster than imagined. Options in input menu harder than expected? reusability?)
◦ What worked well and what could be improved (collaboration worked well, different tasks that were pretty well separable)
◦ Have you used any specific tools? Which ones? (???))

# Resources

* [`Wikipedia: Maze generation algorithm`](https://en.wikipedia.org/wiki/Maze_generation_algorithm)
* [`Geeks for geeks: how to convert binary to hexadecimal`](https://www.geeksforgeeks.org/maths/how-to-convert-binary-to-hexadecimal/)
* [`Geeks for geeks: breadth first search`](https://www.geeksforgeeks.org/dsa/breadth-first-search-or-bfs-for-a-graph/)
* [`Maze Generation: Prim's Algorithm`](https://weblog.jamisbuck.org/2011/1/10/maze-generation-prim-s-algorithm)

### AI usage

We only used AI while explicitly stating that we didn't want the right answer, but we just wanted a nudge in the right direction.

We used AI to brainstorm about pros and cons of different datastructures to use for the maze and cells and also for some help while debugging and for git advice.
The first drafts of some paragraphs of this README were also written using AI.
