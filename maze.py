import random
from conversions import bi_to_hd

class Cell:

    def __init__(self, y: int, x: int,):
        self.x = x
        self.y = y
        self.n = self.e = self.s = self.w = 1
        self.visited = 0

    def __str__(self) -> str:
        bi = str(self.w) + str(self.s) + str(self.e) + str(self.n)
        return bi_to_hd(bi)


class Maze:

    def __init__(
            self,
            width: int,
            height: int,
            entry: tuple[int, int], # (y,x)
            exit: tuple[int, int], # (y,x)
            perfect: bool
    ):
        self._width = width + 2
        self._height = height + 2
        self._entry = (entry[0] + 1, entry[1] + 1)
        self._exit = (exit[0] + 1, exit[1] + 1)
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

    def check_unvis_neighbours(self, current: tuple[int, int]) -> list:
        maze = self._maze
        unvis_neighbours = []
        if not maze[current[0] - 1][current[1]].visited:
            unvis_neighbours.append("N")
        if not maze[current[0]][current[1] + 1].visited:
            unvis_neighbours.append("E")
        if not maze[current[0] + 1][current[1]].visited:
            unvis_neighbours.append("S")
        if not maze[current[0]][current[1] - 1].visited:
            unvis_neighbours.append("W")
        return unvis_neighbours

    def gen_perfect_maze(self) -> None:
        maze = self._maze
        current = self._entry
        stack = []
        moves = []
        maze[current[0]][current[1]].visited = 1
        while True:
            unvis_neighbours = self.check_unvis_neighbours(current)
            if unvis_neighbours:
                stack.append(current)
                move = random.choice(unvis_neighbours)
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
                moves.append(move)
                maze[current[0]][current[1]].visited = 1
                if self._exit[0] == current[0] and self._exit[1] == current[1]:
                    self._path = "".join(moves)
            else:
                if stack:
                    current = stack.pop()
                    moves.pop()
                else:
                    break

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
        for i in range(row_len):
            top = maze[0][i]
            bottom = maze[col_len - 1][i]
            top.n = top.e = top.w = 0
            bottom.e = bottom.s = bottom.w = 0
            top.visited = bottom.visited = 1

    def gen_fourtytwo(self) -> None:
        pass


if __name__ == "__main__":
    maze = Maze(3, 3, (0, 0), (2, 2), True) #input entry and exit is (y,x)
    print(maze)
