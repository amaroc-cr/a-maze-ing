import random
from conversions import bi_to_hd

class Cell:

    def __init__(self, y: int, x: int,):
        self.x = x
        self.y = y
        self.n = self.e = self.s = self.w = 1
        self.visited = 0
        self.available = 1

    def __str__(self) -> str:
        bi = str(self.w) + str(self.s) + str(self.e) + str(self.n)
        return bi_to_hd(bi)

    def check_walls(self) -> list[str]: #do i actually use this?
        walls = []
        if self.n:
            walls.append("N")
        if self.e:
            walls.append("E")
        if self.s:
            walls.append("S")
        if self.w:
            walls.append("W")
        return walls


class Maze:

    def __init__(
            self,
            width: int,
            height: int,
            entry: tuple[int, int], # (x,y)
            exit: tuple[int, int], # (x,y)
            perfect: bool
    ):
        self._width = width + 2
        self._height = height + 2
        self._entry = (entry[1] + 1, entry[0] + 1)
        self._exit = (exit[1] + 1, exit[0] + 1)
        self._perfect = perfect
        self._maze = self.create_grid()
        self._path = ""
        self.gen_maze()

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

    def create_grid(self) -> list:
            maze = []
            for i in range(self._height):
                row = []
                for j in range(self._width):
                    row.append(Cell(i, j))
                maze.append(row)
            return maze

    def gen_maze(self) -> None:
        self.gen_outer_circle()
        # self.gen_fourtytwo()
        if self._perfect:
            self.gen_perfect_maze()
        # else:
        #     self.gen_imperfect_maze()

    def check_neighbours(self, current: tuple[int, int]) -> list[str]:
        maze = self._maze
        unvis_neighbours = []
        if not maze[current[0] - 1][current[1]].visited and maze[current[0] - 1][current[1]].available:
            unvis_neighbours.append("N")
        if not maze[current[0]][current[1] + 1].visited and maze[current[0]][current[1] + 1].available:
            unvis_neighbours.append("E")
        if not maze[current[0] + 1][current[1]].visited and maze[current[0] + 1][current[1]].available:
            unvis_neighbours.append("S")
        if not maze[current[0]][current[1] - 1].visited and maze[current[0]][current[1] - 1].available:
            unvis_neighbours.append("W")
        return unvis_neighbours

    def check_walls(self, current: tuple[int, int]) -> list[str|int]:
        maze = self._maze
        walls = []
        number = 0
        if maze[current[0]][current[1]].n:
            number += 1
            if maze[current[0] - 1][current[1]].available:
                walls.append("N")
        if maze[current[0]][current[1]].e:
            number += 1
            if maze[current[0]][current[1] + 1].available:
                walls.append("E")
        if maze[current[0]][current[1]].s:
            number += 1
            if maze[current[0] + 1][current[1]].available:
                walls.append("S")
        if maze[current[0]][current[1]].w:
            number += 1
            if maze[current[0]][current[1] - 1].available:
                walls.append("W")
        walls.append(number)
        return walls

    def move_to_next(self, current: tuple[int, int], move: str) -> tuple[int, int]:
        maze = self._maze
        if move == "N":
            maze[current[0]][current[1]].n = 0
            current = (current[0] - 1, current[1])
            maze[current[0]][current[1]].s = 0
        if move == "E":
            maze[current[0]][current[1]].e = 0
            current = (current[0], current[1] + 1)
            maze[current[0]][current[1]].w = 0
        if move == "S":
            maze[current[0]][current[1]].s = 0
            current = (current[0] + 1, current[1])
            maze[current[0]][current[1]].n = 0
        if move == "W":
            maze[current[0]][current[1]].w = 0
            current = (current[0], current[1] - 1)
            maze[current[0]][current[1]].e = 0
        maze[current[0]][current[1]].visited = 1
        return current

    def gen_perfect_maze(self) -> None:
        maze = self._maze
        current = self._entry
        maze[current[0]][current[1]].visited = 1
        stack = []
        moves = []
        while True:
            unvis_neighbours = self.check_neighbours(current)
            if unvis_neighbours:
                move = random.choice(unvis_neighbours)
                moves.append(move)
                stack.append(current)
                current = self.move_to_next(current, move)
                if self._exit[0] == current[0] and self._exit[1] == current[1]:
                    self._path = "".join(moves)
            else:
                if stack:
                    current = stack.pop()
                    moves.pop()
                else:
                    break

    def gen_imperfect_maze(self) -> None:
        maze = self._maze
        self.gen_perfect_maze()
        for i in range(self._height):
            for j in range(self._width):
                if maze[i][j].available:
                    walls = self.check_walls((i, j))
                    number = walls.pop()
                    if number == 3 and walls:
                        move = random.choice(walls)
                        self.move_to_next((i, j), move)
        self._path = self.find_path()

    def find_path(self) -> str:
        maze = self._maze
        for i in range(self._height):
            for j in range(self._width):
                maze[i][j].visited = 0
        current = self._entry
        maze[current[0]][current[1]].visited = 1
        queue = [current]
        while queue:
            if self._exit[0] == current[0] and self._exit[1] == current[1]:
                break
            unvis_neighbours = self.check_neighbours(current)
            walls = self.check_walls(current)
            moves = unvis_neighbours.difference(walls)

    def gen_outer_circle(self) -> None:
        maze = self._maze
        row_len = len(maze[0])
        col_len = len(maze)
        for i in range(col_len):
            left = maze[i][0]
            right = maze[i][row_len - 1]
            left. n = left.s = left.w = 0
            right.n = right.e = right.s = 0
            left.visited = right.visited = 1
            left.available = right.available = 0
        for i in range(row_len):
            top = maze[0][i]
            bottom = maze[col_len - 1][i]
            top.n = top.e = top.w = 0
            bottom.e = bottom.s = bottom.w = 0
            top.visited = bottom.visited = 1
            top.available = right.available = 0 #kan dit misschien nog in een losse functie? Die ik ook gebruik voor de 42

    def gen_fourtytwo(self) -> None:
        pass
