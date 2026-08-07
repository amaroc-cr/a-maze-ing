import random
from collections import deque
from conversions import bi_to_hd
from parsing import ConfigError


class Cell:

    def __init__(self, y: int, x: int,):
        self.x = x
        self.y = y
        self.n = self.e = self.s = self.w = 1
        self.visited = 0
        self.available = 1
        self.move_to_cell = ""

    def __str__(self) -> str:
        bi = str(self.w) + str(self.s) + str(self.e) + str(self.n)
        return bi_to_hd(bi)

    def dead_end(self) -> bool:
        walls = self.n + self.e + self.s + self.w
        return (walls == 3)


class Maze:

    def __init__(
            self,
            width: int,
            height: int,
            entry: tuple[int, int],  # (x,y)
            exit: tuple[int, int],  # (x,y)
            perfect: bool
    ):
        self._width = width + 2
        self._height = height + 2
        self._entry = (entry[1] + 1, entry[0] + 1)
        self._exit = (exit[1] + 1, exit[0] + 1)
        self._perfect = perfect
        self._maze = self.create_grid()
        self.gen_maze()
        self._path = self.find_path()

    def __str__(self) -> str:
        temp = []
        col_len = len(self._maze)
        for row in range(1, col_len - 1):
            for cell in self._maze[row][1:-1]:
                temp.append(str(cell))
            temp.append("\n")
        temp.append(f"\n{self._entry[1] - 1},{self._entry[0] - 1}\n")
        temp.append(f"{self._exit[1] - 1},{self._exit[0] - 1}\n")
        temp.append(f"{self._path}\n")
        s = "".join(temp)
        return s

    def create_grid(self) -> list[list[Cell]]:
        maze = []
        for i in range(self._height):
            row = []
            for j in range(self._width):
                row.append(Cell(i, j))
            maze.append(row)
        return maze

    def gen_maze(self) -> None:
        self.gen_outer_circle()
        if self._width >= 11 and self._height >= 9:
            self.gen_fourtytwo()
        if self._perfect:
            self.gen_perfect_maze()
        else:
            self.gen_imperfect_maze()

    def make_unavailable(self, current: tuple[int, int]) -> None:
        maze = self._maze
        maze[current[0]][current[1]].visited = 1
        maze[current[0]][current[1]].available = 0

    def gen_outer_circle(self) -> None:
        for i in range(self._height):
            self.make_unavailable((i, 0))
            self.make_unavailable((i, self._width - 1))
        for i in range(self._width):
            self.make_unavailable((0, i))
            self.make_unavailable((self._height - 1, i))

    def gen_fourtytwo(self) -> None:
        maze = self._maze
        middle = (int(self._height / 2), int(self._width / 2))
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
        d = {"Entry": self._entry, "Exit": self._exit}
        for key in d:
            if not maze[d[key][0]][d[key][1]].available:
                raise ConfigError(f"{key} cell inside of 42-logo")

    def check_neighbours(self, current: tuple[int, int]) -> list[str]:
        maze = self._maze
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

    def check_walls(self, current: tuple[int, int]) -> list[str]:
        maze = self._maze
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
        maze = self._maze
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

    def gen_perfect_maze(self) -> None:  # Algorithm: DFS with backtracking
        maze = self._maze
        current = self._entry
        maze[current[0]][current[1]].visited = 1
        stack = []
        while True:
            unvis_neighbours = self.check_neighbours(current)
            if unvis_neighbours:
                move = random.choice(unvis_neighbours)
                stack.append(current)
                current = self.move_to_next(current, move, 1)
                maze[current[0]][current[1]].visited = 1
            else:
                if stack:
                    current = stack.pop()
                else:
                    break

    def gen_imperfect_maze(self) -> None:
        maze = self._maze
        self.gen_perfect_maze()
        for i in range(1, self._height - 1):
            for j in range(1, self._width - 1):
                if maze[i][j].available and maze[i][j].dead_end():
                    walls = self.check_walls((i, j))
                    if walls:
                        move = random.choice(walls)
                        self.move_to_next((i, j), move, 1)

    def reset_maze(self) -> None:
        maze = self._maze
        for i in range(self._height):
            for j in range(self._width):
                maze[i][j].visited = 0

    def bfs_to_exit(self) -> None:
        maze = self._maze
        start = self._entry
        maze[start[0]][start[1]].visited = 1
        exit_found = False
        queue: deque[tuple[int, int]] = deque()
        queue.append(start)
        while queue:
            if exit_found:
                break
            current = queue.popleft()
            unvis_neighbours = self.check_neighbours(current)
            walls = self.check_walls(current)
            moves = set(unvis_neighbours).difference(walls)
            for move in moves:
                nxt = self.move_to_next(current, move)
                maze[nxt[0]][nxt[1]].visited = 1
                maze[nxt[0]][nxt[1]].move_to_cell = move
                if self._exit == nxt:
                    exit_found = True
                queue.append(nxt)

    def retrace_path_to_start(self) -> str:
        maze = self._maze
        current = self._exit
        path = []
        while current != self._entry:
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
        self.reset_maze()
        self.bfs_to_exit()
        res = self.retrace_path_to_start()
        return res
