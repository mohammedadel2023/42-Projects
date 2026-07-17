from mlx import Mlx
from .MazeGenerator import Maze
from .parser import parser
from typing import Any
import random
import sys

key_bindings = {
    "1": 48 + 1,
    "2": 48 + 2,
    "3": 48 + 3,
    "4": 48 + 4
}

mouse_bindings = {
    "LC": 1,  # Left Click
    "MC": 2,  # Middle Click
    "RC": 3,  # Right Click
    "SU": 4,  # Scroll Up
    "SD": 5  # Scroll Down
}


class GUIError(Exception):
    """This exception is raised when the GUI couldn't be rendered

    Attributes:
        m -- explanation of the error
    """
    def __init__(self, m: str = "GUI Error") -> None:
        super().__init__(m)


class Controller:
    """This class is reponsible of showing rendering everthing on a window

    Attributes:
        mlx: An object reponsible of manipulating the all elements of GUI
        mlx_con: A pointer to an MLX connection
        win_con: A pointer to a windown connection
    """
    def __init__(self, mlx: Any, mlx_con: Any, win_con: Any) -> None:
        self.mlx: Mlx = mlx
        self.mlx_con = mlx_con
        self.win_con = win_con

    def close_win(self) -> None:
        """Close the window"""
        self.mlx.mlx_destroy_window(self.mlx_con, self.win_con)
        self.mlx.mlx_loop_exit(self.mlx_con)

    def vis_maze(self, params: dict[Any, Any]) -> None:
        """Generate a maze

        Args:
            params: A dictionary containing all data needed to visualize a maze
        """

        config = parser()
        if (not config):
            raise GUIError("config hasn't been generated")
        if (config):
            if config["SEED"]:
                random.seed(42)
            maze = Maze(
                config["HEIGHT"],
                config["WIDTH"],
                config["ENTRY"],
                config["EXIT"],
                config["PERFECT"],
            )
        if (not maze):
            raise GUIError("maze hasn't been generated")
        params["maze"] = maze
        params["path_visible"] = False
        controller: Controller = params["controller"]
        controller.mlx.mlx_do_sync(controller.mlx_con)
        maze.output(config["OUTPUT_FILE"])
        self.mlx.mlx_clear_window(self.mlx_con, self.win_con)
        self.vis_grid(params)

    def vis_grid(self, params: dict[Any, Any]) -> None:
        """Visualize the maze

        visulaize every cell in the grid, mark the entry and exit cells,
        and show all actions the user can invoke.

        Args:
            params: A dictionary containing all data needed to visualize a maze
        """
        maze = params["maze"]

        c = params["controller"]
        c.mlx.mlx_string_put(c.mlx_con, c.win_con, 20, 900, 0xffffffff,
                             "=== A-Maze-iing ===")
        c.mlx.mlx_string_put(c.mlx_con, c.win_con, 20, 920, 0xffffffff,
                             "1: Regenerate a new maze")
        c.mlx.mlx_string_put(c.mlx_con, c.win_con, 20, 940, 0xffffffff,
                             "2: Show/Hide path from entry to exit")
        c.mlx.mlx_string_put(c.mlx_con, c.win_con, 20, 960, 0xffffffff,
                             "3: Rotate maze colors")
        c.mlx.mlx_string_put(c.mlx_con, c.win_con, 20, 980, 0xffffffff,
                             "4: Quit")
        for row in maze.grid:
            for cell in row:
                if cell.is_42:
                    self.vis_cell(cell, params["ft"])
                else:
                    self.vis_cell(cell, params["wall"])
        for x in range(1, 15):
            for y in range(1, 15):
                self.mlx.mlx_pixel_put(self.mlx_con,
                                       self.win_con,
                                       100 + ((maze.entry[1]) * 16 + x),
                                       100 + ((maze.entry[0]) * 16 + y),
                                       params["entry"])
                self.mlx.mlx_pixel_put(self.mlx_con,
                                       self.win_con,
                                       100 + ((maze.exit[1]) * 16 + x),
                                       100 + ((maze.exit[0]) * 16 + y),
                                       params["exit"])

    def vis_cell(self, cell: Any, color: int) -> None:
        """Visualize an individual cell

        Args:
            cell: The cell to visualize
            color: The color of walls surrounding the cell
        """
        tile = 16
        anchor = (100, 100)

        if cell.north:
            for x in range(16):
                self.mlx.mlx_pixel_put(self.mlx_con, self.win_con,
                                       anchor[0] + cell.col * tile + x,
                                       anchor[1] + cell.row * tile, color)

        if cell.east:
            for y in range(16):
                self.mlx.mlx_pixel_put(self.mlx_con, self.win_con,
                                       anchor[0] + cell.col * tile + 15,
                                       anchor[1] + cell.row * tile + y,
                                       color)

        if cell.south:
            for x in range(16):
                self.mlx.mlx_pixel_put(self.mlx_con, self.win_con,
                                       anchor[0] + cell.col * tile + x,
                                       anchor[1] + cell.row * tile + 15,
                                       color)

        if cell.west:
            for y in range(16):
                self.mlx.mlx_pixel_put(self.mlx_con, self.win_con,
                                       anchor[0] + cell.col * tile,
                                       anchor[1] + cell.row * tile + y,
                                       color)

    def vis_path(self, params: dict[Any, Any]) -> None:
        """Visualize the path

        Visualize the path from entry to exit

        Args:
            params: a dictionary whose values are needed to show the path
        """
        maze = params["maze"]
        if (params["path_visible"]):
            params["path_visible"] = False
            color = params["back"]
            path: str = params["path"]
        else:
            path = maze.find_path()
            params["path"] = path
            color = params["path_color"]
            params["path_visible"] = True
        vertical = 0
        horizontal = 0

        for direction in path[:len(path) - 1]:
            x1 = 0
            x2 = 0
            y1 = 0
            y2 = 0
            if (direction == "N"):
                vertical -= 1
                y2 = 5
            elif (direction == "E"):
                horizontal += 1
                x1 = -5
            elif (direction == "S"):
                vertical += 1
                y1 = -5
            elif (direction == "W"):
                horizontal -= 1
                x2 = 5
            for y in range(5 + y1, 10 + y2):
                for x in range(5 + x1, 10 + x2):
                    self.mlx.mlx_pixel_put(self.mlx_con,
                                           self.win_con,
                                           100 + ((maze.entry[1] +
                                                   horizontal) * 16 + x),
                                           100 + ((maze.entry[0] +
                                                   vertical) * 16 + y),
                                           color)

    def change_color(self, params: dict[Any, Any]) -> None:
        """change the colors of maze walls

        Args:
            params: A dictionary whose values are needed to visualize the maze
        """

        controller: Controller = params["controller"]
        controller.mlx.mlx_clear_window(controller.mlx_con, controller.win_con)
        params["path_visible"] = False
        params["wall"] = random.randint(1, 4294967295)
        params["ft"] = random.randint(1, 4294967295)
        self.vis_grid(params)


def key_listener(keycode: int, params: dict[Any, Any]) -> None:
    """wait for keyboard input and perform actions accordingly

    This function is called whenever a keycap is pressed and performs an
    action for each key pressed.

    Args:
        keycode: The code of the key pressed
        params: A dictionary whose values are needed to visualize the maze
    """
    controller: Controller = params["controller"]

    if keycode == key_bindings["1"]:
        controller.vis_maze(params)
    elif keycode == key_bindings["2"]:
        controller.vis_path(params)
    elif keycode == key_bindings["3"]:
        controller.change_color(params)
    elif keycode == key_bindings["4"]:
        controller.close_win()


def main() -> None:
    """Here the execution of the program starts"""
    try:
        #  MLX Initialization
        mlx = Mlx()
        mlx_con = mlx.mlx_init()
        if not mlx_con:
            raise GUIError("Error establishing the Graphics Connection")

        win_con = mlx.mlx_new_window(mlx_con, 1920, 1080, "A_meow_ing")
        if not win_con:
            raise GUIError("Error creating the window")
        mlx.mlx_sync(mlx_con, 3, win_con)
        controller = Controller(mlx, mlx_con, win_con)

        params = {
            "controller": controller,
            "wall": 0xffffffff,
            "entry": 0xff432dff,
            "exit": 0xffff00ff,
            "path_color": 0xff22ddff,
            "back": 0xff000000,
            "ft": 0xff00ffff,
            "path_visible": False
        }

        mlx.mlx_key_hook(win_con, key_listener, params)

        controller.vis_maze(params)
        mlx.mlx_loop(mlx_con)

        # to end the program, release all resources
        mlx.mlx_release(mlx_con)
    except Exception as e:
        print("Error: ", e)
        sys.exit()


if __name__ == "__main__":
    main()
