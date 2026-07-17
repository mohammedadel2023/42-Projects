from typing import Any
import random
from queue import Queue
from .parser import parser


class MazeError(Exception):
    """This Exception is raised when some error in maze generation occur.

    Attributes:
        m -- explanation of the error
    """
    def __init__(self, m: str = "error generating maze"):
        super().__init__(m)


class Cell:
    """This is the main class that represent the cell in maze.

    Attributes:
        row -- The row index for the cell.
        col -- The col index for the cell.
        is_visited -- indicate if the cell is visited or not.
        is_42 -- ndicate if the cell is 42 cell or not.
        path -- The path from the entry cell to this cell.
        north -- True if there is a wall in the north.
        east -- True if there is a wall in the east.
        west -- True if there is a wall in the west.
        south -- True if there is a wall in the south.
    """
    def __init__(self, row: int, col: int) -> None:
        self.row = row
        self.col = col
        self.is_visited = False
        self.is_42 = False
        self.path = " "
        self.north = True
        self.east = True
        self.west = True
        self.south = True

    def has_unvisited_n(self, grid: list[list["Cell"]]) -> list["Cell"]:
        """
        Check if the neighbour cells are not visited yet
        and return them.

        Args:
            grid (list[lsit[Cell]]): the maze (grid of cells).

        Returns:
            list["Cell"]: list of unvisited neighboures of cell.
        """
        my_n = []
        if self.row - 1 >= 0:
            top = grid[self.row - 1][self.col]
            if (not top.is_visited):
                my_n.append(top)
        if self.row + 1 < len(grid):
            bottom = grid[self.row + 1][self.col]
            if (not bottom.is_visited):
                my_n.append(bottom)
        if self.col - 1 >= 0:
            left = grid[self.row][self.col - 1]
            if (not left.is_visited):
                my_n.append(left)
        if self.col + 1 < len(grid[0]):
            right = grid[self.row][self.col + 1]
            if (not right.is_visited):
                my_n.append(right)
        return my_n

    def open_path(c1: 'Cell', c2: 'Cell') -> bool:
        """Break the walls between two cells.
        Args:
            c1(Cell): The first cell.
            c2(Cell): The second cell.

        Returns:
            bool: True if a wall has been broken, False otherwise.
        """
        if (c1.is_42 or c2.is_42):
            return False
        broken = False
        if c1.col - c2.col == 1:
            if c1.west:
                broken = True
            c1.west = False
            c2.east = False
        elif c1.col - c2.col == -1:
            if c1.east:
                broken = True
            c2.west = False
            c1.east = False
        elif c1.row - c2.row == 1:
            if c1.north:
                broken = True
            c1.north = False
            c2.south = False
        elif c1.row - c2.row == -1:
            if c1.south:
                broken = True
            c2.north = False
            c1.south = False
        return broken

    def get_acc(self, grid: list[list["Cell"]]) -> list["Cell"]:
        """
        Return all open cells and modifies the path of each of them
        without including a cell previously visited.

        Args:
            grid (list[lsit[Cell]]): the maze (grid of cells)

        Returns:
            list["Cell"]: list of cell
        """
        open = []
        if (not self.north and self.path[-1] != "S"):
            new = grid[self.row - 1][self.col]
            new.path = self.path + "N"
            open.append(new)
        if (not self.south and self.path[-1] != "N"):
            new = grid[self.row + 1][self.col]
            new.path = self.path + "S"
            open.append(new)
        if (not self.east and self.path[-1] != "W"):
            new = grid[self.row][self.col + 1]
            new.path = self.path + "E"
            open.append(new)
        if (not self.west and self.path[-1] != "E"):
            new = grid[self.row][self.col - 1]
            new.path = self.path + "W"
            open.append(new)
        random.shuffle(open)
        return open

    def get_value(self) -> int:
        """Calculate a cumulative bitmask value representing closed walls.

        Use a binary-based mapping where each direction corresponds to a
        specific power of 2. The cumulative value is the sum of the active
        (True) wall states.

        Returns:
            int: cumulative bitmask
        """
        value = 0
        if self.north:
            value += 1
        if self.east:
            value += 2
        if self.south:
            value += 4
        if self.west:
            value += 8
        return value


class Maze:
    """
    This is the main Mzae class that has a functionality to create a maze
    and find a path for it.

    Attributes:
        height -- The height of maze.
        width -- The width of maze.
        entry -- The entry cell to start finding a path from.
        exit -- The exit cell to leave the maz.
        perfect -- Define if the maze is perfect or not.
        grid -- The maze(grid of cells).
    """
    def __init__(self, height: int, width: int, ENTRY: tuple[int, int],
                 EXIT: tuple[int, int], PERFECT: bool):
        self.height = height
        self.width = width
        self.entry = ENTRY
        self.exit = EXIT
        self.perfect = PERFECT
        self.grid = self.grid_build(height, width)

        if (self.grid[ENTRY[0]][ENTRY[1]].is_visited):
            raise MazeError("entry is a 42 point")
        elif (self.grid[EXIT[0]][EXIT[1]].is_visited):
            raise MazeError("exit is a 42 point")

    def grid_build(self, height: int, width: int) -> list[list[Cell]]:
        """build an initial grid with all cell as unvisited.

        Args:
            height (int): The height of the grid
            width (int): The width of the grid

        Returns:
            list[list["Cell"]]: Initial grid
        """
        grid = []
        for i in range(height):
            row = []
            for j in range(width):
                row.append(Cell(i, j))
            grid.append(row)
        return grid

    def reserve_42(self) -> None:
        """Mark 42 cells as visited."""
        height = self.height // 2
        width = self.width // 2
        cell42 = [
            self.grid[height][width + 1],
            self.grid[height][width + 2],
            self.grid[height][width + 3],
            self.grid[height][width - 1],
            self.grid[height][width - 2],
            self.grid[height][width - 3],
            self.grid[height + 1][width + 1],
            self.grid[height + 1][width - 1],
            self.grid[height + 2][width - 1],
            self.grid[height + 2][width + 1],
            self.grid[height + 2][width + 2],
            self.grid[height + 2][width + 3],
            self.grid[height - 1][width + 3],
            self.grid[height - 1][width - 3],
            self.grid[height - 2][width + 1],
            self.grid[height - 2][width + 2],
            self.grid[height - 2][width + 3],
            self.grid[height - 2][width - 3]
        ]
        for cell in cell42:
            cell.is_42 = True
            cell.is_visited = True
        if self.grid[self.entry[0]][self.entry[1]].is_42 is True:
            raise MazeError("The entry point is 42cell please change it")
        if self.grid[self.exit[0]][self.exit[1]].is_42 is True:
            raise MazeError("The exit point is 42cell please change it")

    def open_loops(self) -> int:
        """
        Create loop in the grid by break a walls in the sent
        cell, ensuring that the broken walls does not belong to 42 cell

        Returns:
            bool: True if break a walls , False if the cell is not proper.
        """
        lp = 0
        if (self.width <= 1 or self.height <= 1):
            return lp
        while not lp:
            for y in range(0, self.width, 3):
                for x in range(0, self.height, 3):
                    if y >= self.width - 1 or x >= self.height - 1:
                        continue
                    cell_no = random.randint(0, 3)
                    match cell_no:
                        case 0:
                            lp += self.grid[x][y].open_path(
                                self.grid[x][y + 1])
                        case 1:
                            lp += self.grid[x][y].open_path(
                                self.grid[x + 1][y])
                        case 2:
                            lp += self.grid[x + 1][y + 1].open_path(
                                self.grid[x + 1][y])
                        case 3:
                            lp += self.grid[x + 1][y + 1].open_path(
                                self.grid[x][y + 1])
        return lp

    def gen_Maze(self) -> None:
        """
        Use the recursive implementation of DFS to generate a
        perfect maze.
        """
        if self.height <= 5 or self.width <= 8:
            print("Error: Maze size cannot accommodate the 42 sign")
        else:
            self.reserve_42()
        st_row = self.entry[0]
        st_col = self.entry[1]
        stack = []
        stack.append(self.grid[st_row][st_col])
        while len(stack):
            cur = stack[-1]
            cur.is_visited = True
            n = cur.has_unvisited_n(self.grid)
            if len(n) == 0:
                stack.pop()
                continue
            rand_cell = random.choice(n)
            cur.open_path(rand_cell)
            stack.append(rand_cell)
        if not self.perfect:
            self.open_loops()

    def find_path(self) -> str:
        """Use a DFS to find the path

        Retruns:
            str: The path or (exit not found) if not found.
        """
        q: Queue[Any] = Queue()
        entry = self.grid[self.entry[0]][self.entry[1]]
        entry.path = " "
        exit = self.grid[self.exit[0]][self.exit[1]]
        visited = set()
        q.put(entry)
        while not q.empty():
            cur: Cell = q.get()
            if (cur == exit):
                return cur.path[1:]
            for x in cur.get_acc(self.grid):
                if x not in visited:
                    q.put(x)
                    visited.add(x)
        return "exit not found"

    def to_hex(self) -> str:
        """
        Convert the cumulative bitmask values representing
        closed walls for each cells to hexa

        Retruns:
            str: grid of hex number as string
        """
        hexa = ""
        for row in self.grid:
            for cell in row:
                hexa += hex(cell.get_value())[2:].upper()
            hexa += "\n"
        return hexa

    def output(self, file_name: str) -> None:
        """
        Generate a maze using gen_Maze() and find a path
        using find_path then write the result in the output file
        Args:config["OUTPUT_FI
            file_name (str): The name of the output file.
        """
        self.gen_Maze()
        with open(file_name, "w") as f:
            f.write(self.to_hex())
            f.write("\n")
            f.write(str(self.entry[0]) + "," + str(self.entry[1]) + "\n")
            f.write(str(self.exit[0]) + "," + str(self.exit[1]) + "\n")
            f.write(self.find_path() + "\n")


def main() -> None:
    config = parser()
    if (config):
        if config["SEED"]:
            random.seed(42)
        maze = Maze(
            config["HEIGHT"],
            config["WIDTH"],
            config["ENTRY"],
            config["EXIT"],
            config["PERFECT"]
        )
        maze.output(config["OUTPUT_FILE"])


if __name__ == "__main__":
    main()
