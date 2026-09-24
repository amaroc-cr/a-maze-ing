import random
from collections import deque
from parsing import ConfigError


class Cell:
    """
    Represents a cell and its four walls in the maze.

    Attributes:
        x, y : int
            X-coordinate, Y-coordinate.
        n, e, s, w : int
            If there is a wall on the north, east, south, west side.
            (1 if there is a wall, 0 if there is no wall.)
        visited : int
            If the cell is visited by the maze generation algorithm.
            (1 if it is visited, 0 if it's not.)
        available : int
            If the cell is available to the maze generation algorithm.
            (Cells on outside border and inside 42 logo are unavailable.)
        move_to_cell : str
            Which way the pathfinder moves to reach this cell.
            (Either "", "N", "E", "S" or "W")

    Methods:
        __str__():
            Represents the four walls (n, e, s, w) as one hexadecimal digit.
        dead_end():
            Checks if this cell is a dead end by checking if it has 3 walls.
        bi_to_hd():
            Converts a four-digit binary number to hexadecimal.
    """

    def __init__(self, y: int, x: int,):
        self.x = x
        self.y = y
        self.n = self.e = self.s = self.w = 1
        self.visited = 0
        self.available = 1
        self.move_to_cell = ""

    def __str__(self) -> str:
        """
        Represents the existence of the four walls (n, e, s, w) in hexadecimal.
            Examples:
                wall at north = 0001 = 1
                wall at east = 0010 = 2
                wall at south = 0100 = 4
                wall at west = 1000 = 8
                walls at north and east = 0011 = 3
                walls at east and west = 1010 = A

        Returns:
            str: One hexadecimal digit that represents the four walls.
        """
        bi = str(self.w) + str(self.s) + str(self.e) + str(self.n)
        return Cell.bi_to_hd(bi)

    def dead_end(self) -> bool:
        """
        Checks if this cell is a dead end by checking if it has 3 walls.

        Returns:
            bool: True if the cell is a dead end, False if not.
        """
        walls = self.n + self.e + self.s + self.w
        return (walls == 3)

    @staticmethod
    def bi_to_hd(s: str) -> str:
        """"
        Converts a four-digit binary number to hexadecimal.

        Args:
            s (str): four-digit binary number.
        Returns:
            str: number in hexadecimal.
        """
        dec = (
            2 ** 3 * int(s[0])
            + 2 ** 2 * int(s[1])
            + 2 ** 1 * int(s[2])
            + 2 ** 0 * int(s[3])
        )
        if dec < 10:
            return chr(dec + 48)
        else:
            return chr(dec + 87)


class Maze:
    """
    Represents the maze, its rows and columns of cells and other properties.

    Attributes:
        width, height : int
            Width and height of maze in number of cells,
            including extra outer circle of unavailable cells.
        entry, exit : tuple[int, int]
            The entry and exit of the maze.
            Format: (y, x)
        _perfect : bool
            True if the maze is perfect (exactly one path possible).
            False if the maze is imperfect (at least two paths, no dead-ends).
        _algo : str
            "dfs" for using the Depth First Search algorithm (default).
            "prim" for using Prim's algorithm.
        _rng : Random
            Random number generator that uses the seed, if specified.
            If no seed, it is an unreproducable random number generator.
        maze : list[list[Cell]]
            Every list in the list contains the cells of a row in the maze.
        path : str
            The shortest path from entry to exit, as a sequence of directions.
            Example: "EEEESEENESEEEEENESENESSSSESSSSSESEESSWSESSSSSS".

    Methods:
        __str__():
            Represents the whole maze in the output file format.
        create_grid():
            Builds the grid of cells, row by row.
        gen_maze():
            Generates the complete maze, in the requested mode.
        make_unavailable():
            Marks a cell as unavailable to the generation algorithms.
        gen_outer_circle():
            Makes the cells on the outer border unavailable.
        gen_fourtytwo():
            Makes the cells that draw the "42" logo unavailable.
        check_unvis_neighbours():
            Lists the directions of the available, unvisited neighbours.
        check_vis_neighbours():
            Lists the directions of the available, visited neighbours.
        check_walls():
            Lists the directions in which this cell has a breakable wall.
        move_to_next():
            Returns the neighbouring cell in a direction, optionally
            breaking the wall in between.
        gen_perfect_maze():
            Generates a perfect maze with the requested algorithm.
        dfs_maze_gen():
            Generates a perfect maze with Depth First Search.
        prim_maze_gen():
            Generates a perfect maze with Prim's algorithm.
        gen_imperfect_maze():
            Generates a maze with loops and without dead ends.
        reset_maze():
            Sets every cell back to unvisited.
        bfs_to_exit():
            Searches the maze from entry to exit with Breadth First Search.
        retrace_path_to_start():
            Reconstructs the path by walking back from exit to entry.
        find_path():
            Finds the shortest path from entry to exit.
    """

    def __init__(
            self,
            width: int,
            height: int,
            entry: tuple[int, int],  # (x,y)
            exit: tuple[int, int],  # (x,y)
            perfect: bool,
            algo: str = "dfs",
            seed: str | None = None
    ):
        self.width = width + 2
        self.height = height + 2
        self.entry = (entry[1] + 1, entry[0] + 1)
        self.exit = (exit[1] + 1, exit[0] + 1)
        self._perfect = perfect
        self._algo = algo
        self._rng = random.Random(seed)
        self.maze = self.create_grid()
        self.gen_maze()
        self.path = self.find_path()

    def __str__(self) -> str:
        """
        Represents the whole maze in the output file format.
        Every row of cells is one line of hexadecimal digits. After an
        empty line follow the entry, the exit and the shortest path.
        The unavailable outer border is left out.

        Returns:
            str: The maze, entry, exit and path, as written to the file.
        """
        temp = []
        col_len = len(self.maze)
        for row in range(1, col_len - 1):
            for cell in self.maze[row][1:-1]:
                temp.append(str(cell))
            temp.append("\n")
        temp.append(f"\n{self.entry[1] - 1},{self.entry[0] - 1}\n")
        temp.append(f"{self.exit[1] - 1},{self.exit[0] - 1}\n")
        temp.append(f"{self.path}\n")
        s = "".join(temp)
        return s

    def create_grid(self) -> list[list[Cell]]:
        """
        Builds the grid of cells, row by row.

        Returns:
            list[list[Cell]]: Every list contains the cells of one row.
        """
        maze = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(Cell(i, j))
            maze.append(row)
        return maze

    def gen_maze(self) -> None:
        """
        Generates the complete maze, in the requested mode.
        First the outer border and the "42" logo are made unavailable,
        then the maze is generated around them.
        """
        self.gen_outer_circle()
        if self.width >= 11 and self.height >= 9:
            self.gen_fourtytwo()
        if self._perfect:
            self.gen_perfect_maze()
        else:
            self.gen_imperfect_maze()

    def make_unavailable(self, current: tuple[int, int]) -> None:
        """
        Marks a cell as unavailable to the generation algorithms.
        The cell is also marked as visited, so no algorithm moves into it.

        Args:
            current (tuple[int, int]): Coordinates of the cell. Format: (y, x)
        """
        maze = self.maze
        maze[current[0]][current[1]].visited = 1
        maze[current[0]][current[1]].available = 0

    def gen_outer_circle(self) -> None:
        """
        Makes the cells on the outer border unavailable.
        This border is not part of the maze itself. It exists so that every
        cell of the maze has four neighbours to look at.
        """
        for i in range(self.height):
            self.make_unavailable((i, 0))
            self.make_unavailable((i, self.width - 1))
        for i in range(self.width):
            self.make_unavailable((0, i))
            self.make_unavailable((self.height - 1, i))

    def gen_fourtytwo(self) -> None:
        """
        Makes the cells that draw the "42" logo unavailable.
        The logo is centred in the middle of the maze and is drawn as two
        sequences of moves, one for each digit.

        Raises:
            ConfigError: If the entry or the exit lies inside the logo.
        """
        maze = self.maze
        middle = (int(self.height / 2), int(self.width / 2))
        start_4 = (middle[0] - 2, middle[1] - 3)
        path_4 = "SSEESS"
        start_2 = (middle[0] - 2, middle[1] + 1)
        path_2 = "EESSWWSSEE"
        for number in [(start_4, path_4), (start_2, path_2)]:
            current = number[0]
            self.make_unavailable(current)
            for move in number[1]:
                current = self.move_to_next(current, move)
                self.make_unavailable(current)
        d = {"Entry": self.entry, "Exit": self.exit}
        for key in d:
            if not maze[d[key][0]][d[key][1]].available:
                raise ConfigError(f"{key} cell inside of 42-logo")

    def check_unvis_neighbours(self, current: tuple[int, int]) -> list[str]:
        """
        Lists the directions of the available, unvisited neighbours.

        Args:
            current (tuple[int, int]): Coordinates of the cell. Format: (y, x)
        Returns:
            list[str]: The directions, as "N", "E", "S" and/or "W".
        """
        maze = self.maze
        unvis_neighbours = []
        if (
            not maze[current[0] - 1][current[1]].visited
            and maze[current[0] - 1][current[1]].available
        ):
            unvis_neighbours.append("N")
        if (
            not maze[current[0]][current[1] + 1].visited
            and maze[current[0]][current[1] + 1].available
        ):
            unvis_neighbours.append("E")
        if (
            not maze[current[0] + 1][current[1]].visited
            and maze[current[0] + 1][current[1]].available
        ):
            unvis_neighbours.append("S")
        if (
            not maze[current[0]][current[1] - 1].visited
            and maze[current[0]][current[1] - 1].available
        ):
            unvis_neighbours.append("W")
        return unvis_neighbours

    def check_vis_neighbours(self, current: tuple[int, int]) -> list[str]:
        """
        Lists the directions of the available, visited neighbours.

        Args:
            current (tuple[int, int]): Coordinates of the cell. Format: (y, x)
        Returns:
            list[str]: The directions, as "N", "E", "S" and/or "W".
        """
        maze = self.maze
        vis_neighbours = []
        if (
            maze[current[0] - 1][current[1]].visited
            and maze[current[0] - 1][current[1]].available
        ):
            vis_neighbours.append("N")
        if (
            maze[current[0]][current[1] + 1].visited
            and maze[current[0]][current[1] + 1].available
        ):
            vis_neighbours.append("E")
        if (
            maze[current[0] + 1][current[1]].visited
            and maze[current[0] + 1][current[1]].available
        ):
            vis_neighbours.append("S")
        if (
            maze[current[0]][current[1] - 1].visited
            and maze[current[0]][current[1] - 1].available
        ):
            vis_neighbours.append("W")
        return vis_neighbours

    def check_walls(self, current: tuple[int, int]) -> list[str]:
        """
        Lists the directions in which this cell has a breakable wall.
        A wall is breakable if the cell behind it is available, so walls
        against the outer border or the "42" logo are left out.

        Args:
            current (tuple[int, int]): Coordinates of the cell. Format: (y, x)
        Returns:
            list[str]: The directions, as "N", "E", "S" and/or "W".
        """
        maze = self.maze
        walls = []
        if (
            maze[current[0]][current[1]].n
            and maze[current[0] - 1][current[1]].available
        ):
            walls.append("N")
        if (
            maze[current[0]][current[1]].e
            and maze[current[0]][current[1] + 1].available
        ):
            walls.append("E")
        if (
            maze[current[0]][current[1]].s
            and maze[current[0] + 1][current[1]].available
        ):
            walls.append("S")
        if (
            maze[current[0]][current[1]].w
            and maze[current[0]][current[1] - 1].available
        ):
            walls.append("W")
        return walls

    def move_to_next(
            self,
            current: tuple[int, int],
            move: str,
            break_wall: int = 0
    ) -> tuple[int, int]:
        """
        Returns the neighbouring cell in the given direction.
        Both sides of the shared wall are opened if break_wall is set,
        so that the two cells keep describing that wall in the same way.

        Args:
            current (tuple[int, int]): Coordinates of the cell. Format: (y, x)
            move (str): The direction: "N", "E", "S" or "W".
            break_wall (int): 1 to open the wall in between, 0 to leave it.
        Returns:
            tuple[int, int]: Coordinates of the neighbour. Format: (y, x)
        """
        maze = self.maze
        if move == "N":
            if break_wall:
                maze[current[0]][current[1]].n = 0
                maze[current[0] - 1][current[1]].s = 0
            current = (current[0] - 1, current[1])
        if move == "E":
            if break_wall:
                maze[current[0]][current[1]].e = 0
                maze[current[0]][current[1] + 1].w = 0
            current = (current[0], current[1] + 1)
        if move == "S":
            if break_wall:
                maze[current[0]][current[1]].s = 0
                maze[current[0] + 1][current[1]].n = 0
            current = (current[0] + 1, current[1])
        if move == "W":
            if break_wall:
                maze[current[0]][current[1]].w = 0
                maze[current[0]][current[1] - 1].e = 0
            current = (current[0], current[1] - 1)
        return current

    def gen_perfect_maze(self) -> None:
        """
        Generates a perfect maze with the requested algorithm.
        Both algorithms give exactly one path between any two cells.
        """
        if self._algo == "prim":
            self.prim_maze_gen()
        else:
            self.dfs_maze_gen()

    def dfs_maze_gen(self) -> None:
        """
        Generates a perfect maze with a Depth First Search algorithm with
        backtracking. From the entry, the algorithm moves to a random
        unvisited neighbour and opens the wall in between. At a dead end
        it backtracks over the stack of earlier visited cells until it
        finds one with unvisited neighbours.
        """
        maze = self.maze
        current = self.entry
        maze[current[0]][current[1]].visited = 1
        stack = []
        while True:
            unvis_neighbours = self.check_unvis_neighbours(current)
            if unvis_neighbours:
                move = self._rng.choice(unvis_neighbours)
                stack.append(current)
                current = self.move_to_next(current, move, 1)
                maze[current[0]][current[1]].visited = 1
            else:
                if stack:
                    current = stack.pop()
                else:
                    break

    def prim_maze_gen(self) -> None:
        """
        Generates a perfect maze with Prim's algorithm.
        The frontiers list holds the unvisited cells next to the maze so far.
        Starting from the entry, a random frontier cell is picked randomly
        and connects it to one of its neighbours that is already in the maze.
        """
        maze = self.maze
        frontiers = []
        current = self.entry
        while True:
            maze[current[0]][current[1]].visited = 1
            unvis_neighbours = self.check_unvis_neighbours(current)
            for move in unvis_neighbours:
                new = self.move_to_next(current, move)
                if new not in frontiers:
                    frontiers.append(new)
            if not frontiers:
                break
            current = self._rng.choice(frontiers)
            frontiers.remove(current)
            vis_neighbours = self.check_vis_neighbours(current)
            move = self._rng.choice(vis_neighbours)
            self.move_to_next(current, move, 1)

    def gen_imperfect_maze(self) -> None:
        """
        Generates an 'imperfect' maze: with loops and without dead ends.
        First a perfect maze is generated. Then at every dead end one wall
        is opened, which removes the dead end and adds a loop.
        """
        maze = self.maze
        self.gen_perfect_maze()
        for i in range(1, self.height - 1):
            for j in range(1, self.width - 1):
                if maze[i][j].available and maze[i][j].dead_end():
                    walls = self.check_walls((i, j))
                    if walls:
                        move = self._rng.choice(walls)
                        self.move_to_next((i, j), move, 1)

    def reset_maze(self) -> None:
        """
        Sets every cell back to unvisited, so the maze can be searched again
        after it has been generated.
        """
        maze = self.maze
        for i in range(self.height):
            for j in range(self.width):
                maze[i][j].visited = 0

    def bfs_to_exit(self) -> None:
        """
        Searches the maze from entry to exit with Breadth First Search.
        Every reachable cell is visited in order of its distance to the entry.
        Each cell stores the direction it was reached from in move_to_cell,
        so the path can be retraced afterwards.
        """
        maze = self.maze
        start = self.entry
        maze[start[0]][start[1]].visited = 1
        exit_found = False
        queue: deque[tuple[int, int]] = deque()
        queue.append(start)
        while queue:
            if exit_found:
                break
            current = queue.popleft()
            unvis_neighbours = self.check_unvis_neighbours(current)
            walls = self.check_walls(current)
            moves = set(unvis_neighbours).difference(walls)
            for move in moves:
                nxt = self.move_to_next(current, move)
                maze[nxt[0]][nxt[1]].visited = 1
                maze[nxt[0]][nxt[1]].move_to_cell = move
                if self.exit == nxt:
                    exit_found = True
                queue.append(nxt)

    def retrace_path_to_start(self) -> str:
        """
        Reconstructs the path by walking back from exit to entry.
        Every cell holds the direction it was reached from, so walking that
        direction in reverse leads back to the entry. The moves are collected
        and then reversed, to get the path from entry to exit.

        Returns:
            str: The path, as a sequence of "N", "E", "S" and "W".
        """
        maze = self.maze
        current = self.exit
        path = []
        while current != self.entry:
            move = maze[current[0]][current[1]].move_to_cell
            path.append(move)
            if move == "N":
                current = self.move_to_next(current, "S")
            if move == "E":
                current = self.move_to_next(current, "W")
            if move == "S":
                current = self.move_to_next(current, "N")
            if move == "W":
                current = self.move_to_next(current, "E")
        path.reverse()
        return "".join(path)

    def find_path(self) -> str:
        """
        Finds the shortest path from entry to exit.
        Because Breadth First Search reaches every cell by the shortest
        route, the retraced path is the shortest one.

        Returns:
            str: The path, as a sequence of "N", "E", "S" and "W".
        """
        self.reset_maze()
        self.bfs_to_exit()
        res = self.retrace_path_to_start()
        return res
