import pygame
from typing import Optional
import sys
from enum import Enum
from mazegenerator.mazegenerator import MazeGenerator
from .parser import Jsonparser
import random
from queue import Queue


class Dir(Enum):
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3


def dec_to_bin(dec: int, digs: int) -> str:
    """converts a decimal integer to a binary string.

    Args:
        dec: the decimal number.
        digs: the number of digits of the binary result.
    Returns:
        str: the number in binary.

    """
    res = ""
    while digs > 0:
        res = str(dec & 1) + res
        dec >>= 1
        digs -= 1
    return res


def collidePoint(rect: pygame.Rect, point: tuple[int, int]) -> bool:
    """check whether a point collides with a Rect.

        Args:
            rect
            point
        Returns:
            bool: True if there's a collision, False otherwise.
    """
    if rect.right >= point[0] >= rect.left:
        if rect.bottom >= point[1] >= rect.top:
            return True
    return False


def collideRect(rect1: pygame.Rect, rect2: pygame.Rect) -> bool:
    """check whether the two Rectangles collide

        Args:
            rect1
            rect2
        Returns:
            bool: True if the Rect's collide, False otherwise.
    """
    if (rect1.left <= rect2.right and rect2.left <= rect1.right and
            rect1.top <= rect2.bottom and rect2.top <= rect1.bottom):
        return True
    return False


class Game:
    """The game engine which starts and ends the game.

    Attributes:
        x_size: the width of the window in pixels.
        y_size: the height of the window in pixels.
        screen: the window on which everything will be displayed.
        pressed_btn: the color when no mouse is hovering on a button.
        pressed_btn: the color when a mouse is hovering on a button.
        white_col: white color
        smallfont
        btnfont
        title_font
        parser: used for getting game configurations from a file.
        score
    """

    def __init__(self, config_file: str) -> None:
        pygame.init()
        self.x_size = 1920
        self.y_size = 1080
        self.screen = pygame.display.set_mode((self.x_size, self.y_size))

        self.pressed_btn = (253, 216, 53)
        self.unpressed_btn = (251, 192, 45)
        self.white_col = (255, 255, 255)
        self.smallfont = pygame.font.SysFont(None, 30)
        self.btnfont = pygame.font.SysFont(None, 60)
        self.title_font = pygame.font.SysFont(None, 200)
        self.parser = Jsonparser(config_file)
        self.score = 0

    def main_menu(self) -> None:
        """
            Draw the main menu and wait for user input.

            From this screen, the user can start the game,
            show the scoreboard, or show the controls of the game.
        """

        self.parser = Jsonparser("config.json")
        btn_Xstart = int(self.x_size * 0.45)
        btn_Ystart = int(self.y_size * 0.4)

        play_button = pygame.Rect(btn_Xstart, btn_Ystart, 300, 75)
        score_button = pygame.Rect(btn_Xstart, btn_Ystart + 120, 300, 75)
        cont_button = pygame.Rect(btn_Xstart, btn_Ystart + 240, 300, 75)

        pac_image = (pygame.image.load("resources/Pacman_HD.png")
                     .convert_alpha()
                     )
        pac_image = pygame.transform.scale(pac_image, (200, 200))
        pac_rect = pac_image.get_rect(topleft=(500, 50))

        red_ghost = pygame.image.load("resources/redgb.png").convert_alpha()
        blue_ghost = pygame.image.load("resources/bluegb.jpeg").convert_alpha()
        resized_redG = pygame.transform.scale(red_ghost, (175, 175))
        resized_blueG = pygame.transform.scale(blue_ghost, (175, 175))

        top_player_rect = pygame.Rect(50, 350, 100, 50)
        while True:
            mouse = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if collidePoint(play_button, mouse):
                        for lev in range(1, 11):
                            self.pacman(lev)
                    elif collidePoint(pac_rect, mouse):
                        for lev in range(1, 11):
                            self.pacman(lev, True)
                    elif collidePoint(cont_button, mouse):
                        self.controls()
                    elif collidePoint(score_button, mouse):
                        self.score_board()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_4:
                        pygame.quit()
                        sys.exit()

            self.screen.fill("#000000")

            pygame.draw.rect(
                self.screen,
                (self.unpressed_btn if collidePoint(play_button, mouse)
                 else self.pressed_btn),
                play_button)
            pygame.draw.rect(
                self.screen,
                (self.unpressed_btn if collidePoint(score_button, mouse)
                 else self.pressed_btn),
                score_button)
            pygame.draw.rect(
                self.screen,
                (self.unpressed_btn if collidePoint(cont_button, mouse)
                 else self.pressed_btn),
                cont_button)

            play_text = self.btnfont.render("Start Game", True,
                                            self.white_col)
            score_text = self.btnfont.render("Scoreboard", True,
                                             self.white_col)
            cont_text = self.btnfont.render("Controls", True,
                                            self.white_col)

            self.screen.blit(play_text, (btn_Xstart + 30, btn_Ystart + 25))
            self.screen.blit(score_text, (btn_Xstart + 30, btn_Ystart + 145))
            self.screen.blit(cont_text, (btn_Xstart + 50, btn_Ystart + 265))

            self.blit_logo(pac_image, resized_redG, resized_blueG)
            self.show_top_players(rect=top_player_rect)
            pygame.display.flip()

    def blit_logo(self, pac_image: pygame.Surface,
                  resized_redG: pygame.Surface,
                  resized_blueG: pygame.Surface) -> None:
        """
            Draw the logo at the main menu.

            Args:
                pac_image: the surface of pacman image.
                resized_redG: resized surface of the red ghost image.
                resized_blueG: resized surface of the blue ghost image.
        """
        pac_rect = pac_image.get_rect(topleft=(500, 50))
        title_1 = self.title_font.render("Pac", True, "yellow")
        title_2 = self.title_font.render("an", True, "yellow")
        tit1_h, _ = title_1.get_size()
        start = 500
        self.screen.blit(pac_image, pac_rect)
        start += 201
        self.screen.blit(title_1, (start, 50))
        start += tit1_h + 2
        self.screen.blit(resized_redG, (start, 50))
        start += 176
        self.screen.blit(resized_blueG, (start, 50))
        start += 176
        self.screen.blit(title_2, (start, 50))

    def get_acc(self, grid: list[list[str]], dir_grid: list[list[str]],
                cell: tuple[int, int]) -> list[tuple[int, int]]:
        """
            Return a list of all accessable neighbors of a specified cell

            Args:
                grid: informs which walls are open in every maze cell.
                dir_grid: contains all paths from an entry cell to every
                          other cell.
                cell: the cell of which we return the neighbors.
            Returns:
                list[tuple[int, int]]: all neighboring cells.
        """
        acc = []
        if (grid[cell[1]][cell[0]][0] == "0"
                and dir_grid[cell[1]][cell[0]][-1] != "E"):  # West
            new = (cell[0] - 1, cell[1])
            acc.append(new)
            dir_grid[new[1]][new[0]] = dir_grid[cell[1]][cell[0]] + "W"
        if (grid[cell[1]][cell[0]][1] == "0"
                and dir_grid[cell[1]][cell[0]][-1] != "N"):  # South
            new = (cell[0], cell[1] + 1)
            acc.append(new)
            dir_grid[new[1]][new[0]] = dir_grid[cell[1]][cell[0]] + "S"
        if (grid[cell[1]][cell[0]][2] == "0"
                and dir_grid[cell[1]][cell[0]][-1] != "W"):  # East
            new = (cell[0] + 1, cell[1])
            acc.append(new)
            dir_grid[new[1]][new[0]] = dir_grid[cell[1]][cell[0]] + "E"
        if (grid[cell[1]][cell[0]][3] == "0"
                and dir_grid[cell[1]][cell[0]][-1] != "S"):  # North
            new = (cell[0], cell[1] - 1)
            acc.append(new)
            dir_grid[new[1]][new[0]] = dir_grid[cell[1]][cell[0]] + "N"
        return acc

    def bfs(self, grid: list[list[str]], entry: tuple[int, int],
            exit: tuple[int, int]) -> str:
        """
            Find the shortest path from entry to exit using BFS.

            Args:
                grid: informs which walls are open in every maze cell.
                entry: the cell from which the path begins
                exit: the cell at which the path ends
            Returns:
                str: the path from entry to exit.
        """
        dir_grid: list[list[str]] = []
        for row in range(15):
            dir_grid.append([])
            for _ in range(15):
                dir_grid[row].append(" ")
        q: Queue[tuple[int, int]] = Queue(0)
        visited = set()
        q.put(entry)
        while not q.empty():
            cur: tuple[int, int] = q.get()
            if (cur == exit):
                return dir_grid[exit[1]][exit[0]][1:]
            for n in self.get_acc(grid, dir_grid, cur):
                if n not in visited:
                    q.put(n)
                    visited.add(n)
        return "exit not found"

    def compute_dist(self, c1: tuple[int, int],
                     c2: tuple[int, int]) -> float:
        """
            Find the euclidean distance between two cells.

            Args:
                c1: the first cell
                c2: the second cell
            Returns:
                float: distance.
        """

        return float(((c1[0] - c2[0]) ** 2 + (c1[1] - c2[1]) ** 2) ** 0.5)

    def ghost_dir(
            self,
            grid: list[list[str]], anchor: tuple[int, int],
            ghost_rect: list[pygame.Rect | None],
            pac_pos: tuple[int, int],
            superpac: bool = False) -> list[tuple[int, int]]:
        """
            Determine the direction of each ghost.

            Args:
                grid: informs which walls are open in every maze cell.
                ghost_rect: a list of ghosts' rectangles.
                pac_pos: position of Pacman in the format: (x, y)
                superpac: the state of the player.
            Returns:
                list[tuple[int, int]]: list of ghosts' speeds
        """

        speeds = []
        for idx, ghost in enumerate(ghost_rect):
            if ghost:
                x_cell = (ghost.x - anchor[0]) // 32
                y_cell = (ghost.y - anchor[1]) // 32
                if idx == 0 and not superpac:  # For chase behavior.
                    path = self.bfs(grid, (x_cell, y_cell), pac_pos)
                    match "X" if not path else path[0]:
                        case "N":
                            speeds.append((0, -1))
                        case "E":
                            speeds.append((1, 0))
                        case "S":
                            speeds.append((0, 1))
                        case "W":
                            speeds.append((-1, 0))
                        case _:
                            speeds.append((0, 0))

                # The running away behavior
                elif (superpac and
                        self.compute_dist(pac_pos, (x_cell, y_cell)) <= 4):

                    # Determine all open directions for each ghost based
                    # on its position.
                    cell = grid[y_cell][x_cell]
                    open_paths = []
                    if cell[0] == "0":
                        open_paths.append(Dir.LEFT)
                    if cell[1] == "0":
                        open_paths.append(Dir.DOWN)
                    if cell[2] == "0":
                        open_paths.append(Dir.RIGHT)
                    if cell[3] == "0":
                        open_paths.append(Dir.UP)
                    dirs = []
                    for dir in open_paths:
                        if dir == Dir.UP:
                            dirs.append((x_cell, y_cell - 1))
                        elif dir == Dir.DOWN:
                            dirs.append((x_cell, y_cell + 1))
                        elif dir == Dir.RIGHT:
                            dirs.append((x_cell + 1, y_cell))
                        elif dir == Dir.LEFT:
                            dirs.append((x_cell - 1, y_cell))
                    next_cell = max(dirs,
                                    key=lambda m: self.compute_dist(m,
                                                                    pac_pos))
                    next_path = open_paths[dirs.index(next_cell)]
                    # Determine the speed of each ghost based on its direction.
                    if next_path == Dir.UP:
                        speeds.append((0, -1))
                    elif next_path == Dir.DOWN:
                        speeds.append((0, 1))
                    elif next_path == Dir.RIGHT:
                        speeds.append((1, 0))
                    elif next_path == Dir.LEFT:
                        speeds.append((-1, 0))
                # regular behavior
                else:
                    rand_x = random.randint(0, 14)
                    rand_y = random.randint(0, 14)
                    path = self.bfs(grid, (x_cell, y_cell), (rand_x, rand_y))
                    match "X" if not path else path[0]:
                        case "N":
                            speeds.append((0, -1))
                        case "E":
                            speeds.append((1, 0))
                        case "S":
                            speeds.append((0, 1))
                        case "W":
                            speeds.append((-1, 0))
                        case _:
                            speeds.append((0, 0))
            else:
                speeds.append((0, 0))
        return speeds

    def ghost(self, ghost_rect: list[pygame.Rect | None],
              ghost_surf: list[pygame.Surface],
              speeds: list[tuple[int, int]]) -> None:
        """
            Move all ghosts in the specified directions and display them.

            Args:
                ghost_rect: contains rectangles of all ghosts
                ghost_surf: contains surfaces of all ghosts
                speeds: contains each ghosts movement direction.
        """

        for index, ghost in enumerate(ghost_rect):
            if ghost:
                speed = speeds[index]
                x_speed, y_speed = speed
                ghost.topleft = (ghost.x + x_speed, ghost.y + y_speed)
                self.screen.blit(ghost_surf[index], ghost)

    def pacgum(self, grid: list[list[str]]) -> list[list[bool]]:
        """
            Determine the distribution of all pacgums in the maze.

            Args:
                grid: informs which walls are open in every maze cell.
            Returns:
                list[list[bool]]: informs which cells contain a pacgum.
        """

        num = self.parser.json_dict["pacgum"]
        gum_grid: list[list[bool]] = []
        for x in range(15):
            gum_grid.append([])
            for y in range(15):
                gum_grid[x].append(False)

        cells = []
        # Deteremine all cells that can accommodate pacgums.
        for x in range(15):
            for y in range(15):
                if (x == 0 and y == 14):
                    gum_grid[y][x] = True
                    continue
                elif (x == 0 and y == 0):
                    gum_grid[y][x] = True
                    continue
                elif (x == 14 and y == 0):
                    gum_grid[y][x] = True
                    continue
                elif (x == 14 and y == 14):
                    gum_grid[y][x] = True
                    continue
                if grid[y][x] == "1111":
                    continue
                cells.append((x, y))

        # Pick a random set out all of valid cells to put pacgums.
        gum_pos = random.sample(cells, k=num)
        for gum in gum_pos:
            gum_grid[gum[1]][gum[0]] = True
        return gum_grid

    def draw_pacgum(self, anchor: tuple[int, int],
                    gum_grid: list[list[bool]]) -> None:
        """
            Draw all pacgums and super pacgums accross the maze.

            Args:
                anchor: a tuple indicating the topleft position of the maze.
                gum_grid: a list showing the distribution of pacgums
                    accross the maze.
        """

        pacgum_surf = (pygame.image
                       .load("pacman-art/other/dot.png").convert_alpha())
        pacgum_rect = pacgum_surf.get_rect()

        app_surf = (pygame.image
                    .load("pacman-art/other/apple.png").convert_alpha())

        for y, row in enumerate(gum_grid):
            for x, cell in enumerate(row):
                if cell:
                    pos = (anchor[0] + x * 32 + 8, anchor[1] + y * 32 + 8)
                    pacgum_rect.topleft = pos
                    if ((x == 0 and y == 0) or (x == 0 and y == 14)
                            or (x == 14 and y == 0) or (x == 14 and y == 14)):
                        self.screen.blit(app_surf, pacgum_rect)
                    else:
                        self.screen.blit(pacgum_surf, pacgum_rect)

    def gameover(self, win: bool) -> None:
        """
            Display the gameover screen.

            The screen contains the ability to save your score, and to return
            to the main menu.

            Args:
                win: defines the message to be displayed.
        """

        if win:
            pass
        else:
            pygame.mixer.music.load("audio/get-out.mp3")
            pygame.mixer.music.set_volume(0.7)
            pygame.mixer.music.play()

        username = ""
        highlight = "white"
        no_highlight = "gray"
        key_input = False
        clock = pygame.time.Clock()
        error_font = pygame.font.SysFont(None, 20)
        error_msg = error_font.render("", True, "#EF4444")

        txt_box = pygame.Rect(800, 250, 280, 60)

        menu_btn = pygame.Rect(1920 // 2 - 150, 1080 - 600, 240, 60)
        menu_btn_txt = self.btnfont.render("main menu", True,
                                           "white")

        save_btn = pygame.Rect(1100, 250, 120, 50)
        save_btn_txt = self.btnfont.render("Save", True,
                                           "white")
        save_btn_txt_rect = save_btn_txt.get_rect(topleft=(1110, 255))
        save_btn_is_clicked = False

        msg1 = ("Enter your username: ")
        msg1_surf = self.btnfont.render(msg1, True, "#94A3B8")

        box_color = no_highlight

        while True:
            self.screen.fill("#0F172A")

            if (win):
                msg = self.btnfont.render("Congratulations!", False, "yellow")
            else:
                msg = self.btnfont.render("You lost", False, "#EF4444")

            mouse = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_4:
                        pygame.quit()
                        sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if collidePoint(txt_box, mouse):
                        box_color = highlight
                        key_input = True
                    elif collidePoint(menu_btn, mouse):
                        self.score = 0
                        self.main_menu()
                    elif (collidePoint(save_btn, mouse)
                          and not save_btn_is_clicked):
                        if (username.count(" ") == len(username)):
                            error_msg = (error_font
                                         .render("Usernames should " +
                                                 "contain at least one " +
                                                 "alphanumeric character",
                                                 1, "#EF4444"))
                        else:
                            if self.parser.check_names(username):
                                error_msg = (error_font
                                             .render("The name does exist",
                                                     1, "#EF4444"))
                            else:
                                self.parser.update_board([username,
                                                          self.score])
                                error_msg = (error_font
                                             .render("Result Saved!",
                                                     1, "white"))
                                save_btn_is_clicked = True
                    else:
                        box_color = no_highlight
                        key_input = False

                if event.type == pygame.KEYDOWN and key_input:
                    if ((str(event.unicode).isalnum() or
                            str(event.unicode) == " ") and
                            len(username) < 10):
                        username += str(event.unicode)
                        error_msg = error_font.render("", True, "#EF4444")
                    elif event.key == pygame.K_BACKSPACE:
                        username = username[: -1]
                        error_msg = error_font.render("", True, "#EF4444")
                    elif len(username) == 10:
                        error_msg = error_font.render("Usernames cannot " +
                                                      "exceed 10 characters",
                                                      True,
                                                      "#EF4444")

            pygame.draw.rect(
                self.screen,
                (self.unpressed_btn if collidePoint(menu_btn, mouse)
                 else self.pressed_btn),
                menu_btn)
            self.screen.blit(menu_btn_txt, (menu_btn.x + 10, menu_btn.y + 10))

            pygame.draw.rect(
                self.screen,
                box_color,
                txt_box
            )

            pygame.draw.rect(
                self.screen,
                (self.unpressed_btn if collidePoint(save_btn, mouse)
                 else self.pressed_btn),
                save_btn)

            self.screen.blit(save_btn_txt, save_btn_txt_rect)

            msg_rect = msg.get_rect(center=(960, 120))
            self.screen.blit(msg, msg_rect)
            pygame.draw.line(self.screen, "#EF4444", (800, 150), (1100, 150))

            msg1_rect = msg1_surf.get_rect(topleft=(340, 250))
            self.screen.blit(msg1_surf, msg1_rect)

            score = self.btnfont.render(f"Score: {self.score}", False,
                                        self.pressed_btn)
            score_rect = score.get_rect(topleft=(1920 // 2 - 100, 200))
            self.screen.blit(score, score_rect)

            username_surf = self.btnfont.render(username, True, "#282424")
            self.screen.blit(username_surf, (txt_box.x, txt_box.y + 15))

            self.screen.blit(error_msg, (800, 310))

            clock.tick(60)
            pygame.display.flip()

    def pause(self) -> Optional[int]:
        """
            Pause the game.

            It enables the user to stop the game and gives him the ability
            to return back to the main menu or to resume the game.

            Returns:
                Optional[int]: number of milleseconds the game was paused for.
        """
        time1 = pygame.time.get_ticks()
        while True:
            mouse_pos = pygame.mouse.get_pos()

            frame = pygame.Rect(0, 0, 600, 200)
            frame.center = (1920 // 2, 400)
            pygame.draw.rect(self.screen, "#0F172A", frame)
            pygame.draw.rect(self.screen, "white", frame, 1)

            txt1 = self.btnfont.render("Paused", True, "#94A3B8")
            txt1_rect = txt1.get_rect(center=(frame.midtop[0], frame.top + 30))
            self.screen.blit(txt1, txt1_rect)

            menu_btn = pygame.Rect(frame.left + 30,
                                   frame.bottom - 100,
                                   120, 40)
            menu_txt = self.smallfont.render("Main Menu", True, "white")
            pygame.draw.rect(self.screen,
                             self.pressed_btn
                             if collidePoint(menu_btn, mouse_pos)
                             else self.unpressed_btn, menu_btn)
            self.screen.blit(menu_txt, (menu_btn.left + 5,
                                        menu_btn.bottom - 30))

            resume_btn = pygame.Rect(frame.right - 200,
                                     frame.bottom - 100,
                                     93, 40)

            resume_txt = self.smallfont.render("Resume", True, "white")
            pygame.draw.rect(self.screen,
                             self.pressed_btn
                             if collidePoint(resume_btn, mouse_pos)
                             else self.unpressed_btn, resume_btn)
            self.screen.blit(resume_txt, (resume_btn.left + 5,
                                          resume_btn.bottom - 30))

            pygame.display.flip()
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_4:
                        pygame.quit()
                        sys.exit()
                if e.type == pygame.MOUSEBUTTONDOWN:
                    if e.button == 1 and collidePoint(menu_btn, mouse_pos):
                        self.score = 0
                        self.main_menu()
                    if e.button == 1 and collidePoint(resume_btn,
                                                      mouse_pos):
                        time2 = pygame.time.get_ticks()
                        return time2 - time1

    def controls(self) -> None:
        """
            Show the controls of the game.

            It displays a lsit of all actions each with its
            corresponding key binding
        """

        frame = pygame.Rect(0, 0, 600, 400)
        frame.center = (self.x_size // 2, self.y_size // 2)

        title = self.btnfont.render("Controls", True, "#94A3B8")
        title_rect = title.get_rect(center=(frame.midtop[0],
                                            frame.top + 30))

        inst = ["Move Up: Up Arrow", "Move Down: Down Arrow",
                "Move Left: Left Arrow", "Move Right: Right Arrown",
                "Pause: Esc", "Level Skip: l"]
        inst_txt = self.smallfont.render("", True, "#94A3B8")
        inst_rect = inst_txt.get_rect(topleft=(title_rect.x,
                                               title_rect.y + 200))

        x1 = pygame.image.load("resources/x1.png").convert_alpha()
        x_rect = x1.get_rect(topright=frame.topright)

        x2 = pygame.image.load("resources/x2.png").convert_alpha()

        while True:
            inst_rect.y = title_rect.bottom + 20
            mouse_pos = pygame.mouse.get_pos()

            pygame.draw.rect(self.screen, "#0F172A", frame)
            pygame.draw.rect(self.screen, "white", frame, 1)
            self.screen.blit(title, title_rect)

            if (collidePoint(x_rect, mouse_pos)):
                self.screen.blit(x2, x_rect)
            else:
                self.screen.blit(x1, x_rect)

            for i in inst:
                inst_txt = self.smallfont.render(i, True, "#94A3B8")
                inst_rect.y += 40
                self.screen.blit(inst_txt, inst_rect)
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_4:
                        pygame.quit()
                        sys.exit()
                if e.type == pygame.MOUSEBUTTONDOWN:
                    if (collidePoint(x_rect, mouse_pos)):
                        self.main_menu()
            pygame.display.flip()

    def show_top_players(self, rect: pygame.Rect, top_n: int = 3) -> None:
        """
            Show the top n playes.

            Args:
                rect: the rect on which we will display the scoreboard.
                top_n: specifies the number of names to display.
        """

        if top_n > 10:
            top_n = 10
        top_palyers = list(self.parser.sorted_board.items())

        title_rect = rect
        m_font = pygame.font.SysFont(None, 50)
        tilte = self.btnfont.render("Top player score", False, "white")
        y_start = title_rect.y + 75
        self.screen.blit(tilte, title_rect)
        index = 1
        x_size, y_size = title_rect.size
        for name, score in top_palyers[:top_n]:
            text_msg = f"{index}. {name} - {score}"
            text = m_font.render(text_msg, False, "red")
            index += 1
            record_rect = pygame.Rect(rect.x + 30, y_start, x_size - 25,
                                      y_size - 25)
            self.screen.blit(text, record_rect)
            y_start += 45
        pygame.display.flip()

    def score_board(self) -> None:
        """
            Display the scoreboard screen.
        """

        pac_image = (pygame.image.load("resources/Pacman_HD.png")
                     .convert_alpha())
        pac_image = pygame.transform.scale(pac_image, (200, 200))
        red_ghost = pygame.image.load("resources/redgb.png").convert_alpha()
        blue_ghost = pygame.image.load("resources/bluegb.jpeg").convert_alpha()
        resized_redG = pygame.transform.scale(red_ghost, (175, 175))
        resized_blueG = pygame.transform.scale(blue_ghost, (175, 175))
        top_players_rect = pygame.Rect(850, 300, 150, 75)
        menu_btn = pygame.Rect(900, 875, 240, 60)
        menu_btn_txt = self.btnfont.render("main menu", True,
                                           "white")
        self.screen.fill("black")
        while True:
            mouse = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if collidePoint(menu_btn, mouse):
                        self.main_menu()
            self.blit_logo(pac_image, resized_redG, resized_blueG)
            self.show_top_players(rect=top_players_rect, top_n=10)
            pygame.draw.rect(
                self.screen,
                (self.unpressed_btn if collidePoint(menu_btn, mouse)
                 else self.pressed_btn),
                menu_btn)
            self.screen.blit(menu_btn_txt, (menu_btn.x + 10, menu_btn.y + 10))

    def pacman(self, lev_no: int = 1, cheat_mode: bool = False) -> None:
        """
            Draw Pacman and all ghosts and control their movement.

            Pacman's movement is determined by user keyboard input, whilst
            ghosts movement is determined randomly.

            Args:
                lev_no: Level's number from 1 to 10.
                cheat_mode: if True, the player will have special abilities.
        """
        if lev_no == 1:
            maze = MazeGenerator(seed=self.parser.json_dict["seed"])
        else:
            maze = MazeGenerator()
        grid = [[dec_to_bin(y, 4) for y in x] for x in maze.maze]

        x_spd = 0
        y_spd = 0
        x_pac = 8
        y_pac = 8
        pac_state = 0
        ghost_c = 0
        pac_dir_img = None
        pac_dir = Dir.RIGHT
        speeds = []

        x = (1920 - maze._width * 32) // 2
        y = (1080 - maze._height * 32) // 2
        anchor = (x, y)
        spawn = (x + 32 * 7, y + 32 * 6)
        mov_dir = None

        ghst_1surf = (pygame.image.load("pacman-art/ghosts/blinky.png")
                      .convert_alpha()
                      )
        ghst_2surf = (pygame.image.load("pacman-art/ghosts/clyde.png")
                      .convert_alpha()
                      )
        ghst_3surf = (pygame.image.load("pacman-art/ghosts/inky.png")
                      .convert_alpha()
                      )
        ghst_4surf = (pygame.image.load("pacman-art/ghosts/pinky.png")
                      .convert_alpha()
                      )
        ghst_5surf = (pygame.image.load("pacman-art/ghosts/blue_ghost.png")
                      .convert_alpha()
                      )
        # respawn points
        ghst1_res = (anchor[0] + 8, anchor[1] + 8)
        ghst2_res = (anchor[0] + (32 * (maze._width - 1)) + 8, anchor[1] + 8)
        ghst3_res = (anchor[0] + 8, anchor[1] + 32 * (maze._height - 1) + 8)
        ghst4_res = (anchor[0] + (32 * (maze._width - 1)) + 8,
                     anchor[1] + (32 * (maze._height - 1)) + 8
                     )
        ghost_res = [ghst1_res, ghst2_res, ghst3_res, ghst4_res]

        ghst_1rect = ghst_1surf.get_rect(topleft=ghst1_res)
        ghst_2rect = ghst_2surf.get_rect(topleft=ghst2_res)
        ghst_3rect = ghst_3surf.get_rect(topleft=ghst3_res)
        ghst_4rect = ghst_4surf.get_rect(topleft=ghst4_res)

        ghost_surf = [ghst_1surf, ghst_2surf, ghst_3surf, ghst_4surf]
        ghost_rect: list[pygame.Rect | None] = [ghst_1rect, ghst_2rect,
                                                ghst_3rect, ghst_4rect]
        ghost_time: list[None | int] = [None, None, None, None]

        super_pac = False
        super_time = 0

        gum_grid = self.pacgum(grid)

        clock = pygame.time.Clock()
        rem_time = pygame.time.get_ticks()
        max_time = self.parser.json_dict["level_max_time"] * 1000

        lives = self.parser.json_dict["lives"]

        time_txt = self.smallfont.render("", True, "white")
        while True:
            lives_txt = self.btnfont.render(f"Lives: {lives}", True, "white")
            self.level(anchor, grid)
            self.draw_pacgum(anchor, gum_grid)

            # Displays the level number
            level_txt = self.btnfont.render(f"Level {lev_no}/10", True,
                                            "white")
            level_rect = level_txt.get_rect(topleft=(0, 200))
            self.screen.blit(level_txt, level_rect)

            # Ensures that pacman doesn't move unless the corresponding
            # direction is open
            if (((spawn[0] + x_pac - anchor[0]) % 32 == 8) and
                    (spawn[1] + y_pac - anchor[1]) % 32 == 8):
                x_cell = (spawn[1] + y_pac - anchor[1]) // 32
                y_cell = (spawn[0] + x_pac - anchor[0]) // 32
                if mov_dir == Dir.LEFT and grid[x_cell][y_cell][0] == "0":
                    pac_dir = Dir.LEFT
                    x_spd = -1
                    y_spd = 0
                    if (cheat_mode):
                        x_spd *= 2
                        y_spd *= 2
                elif mov_dir == Dir.DOWN and grid[x_cell][y_cell][1] == "0":
                    pac_dir = Dir.DOWN
                    x_spd = 0
                    y_spd = 1
                    if (cheat_mode):
                        x_spd *= 2
                        y_spd *= 2
                elif mov_dir == Dir.RIGHT and grid[x_cell][y_cell][2] == "0":
                    pac_dir = Dir.RIGHT
                    x_spd = 1
                    y_spd = 0
                    if (cheat_mode):
                        x_spd *= 2
                        y_spd *= 2
                elif mov_dir == Dir.UP and grid[x_cell][y_cell][3] == "0":
                    pac_dir = Dir.UP
                    x_spd = 0
                    y_spd = -1
                    if (cheat_mode):
                        x_spd *= 2
                        y_spd *= 2

            # Determine to where Pacman's face is pointed
            match pac_dir:
                case Dir.UP:
                    pac_dir_img = "up"
                case Dir.DOWN:
                    pac_dir_img = "down"
                case Dir.RIGHT:
                    pac_dir_img = "right"
                case Dir.LEFT:
                    pac_dir_img = "left"

            # Creating Pacman's Animation
            match pac_state:
                case 0:
                    pacman_surf = (pygame.image.load
                                   (f"pacman-art/pacman-{pac_dir_img}/1.png")
                                   .convert_alpha())
                case 6:
                    pacman_surf = (pygame.image.load
                                   (f"pacman-art/pacman-{pac_dir_img}/2.png")
                                   .convert_alpha())
                case 12:
                    pacman_surf = (pygame.image.load
                                   (f"pacman-art/pacman-{pac_dir_img}/3.png")
                                   .convert_alpha())
            pac_state = (pac_state + 1) % 13
            pacman_rect = pacman_surf.get_rect()

            # Check whether or not pacman has came across a pacgum
            # or a super pacgum and increases score accordingly
            if (((spawn[0] + x_pac - anchor[0]) % 32 == 8) and
                    (spawn[1] + y_pac - anchor[1]) % 32 == 8):

                x_cell = (spawn[1] + y_pac - anchor[1]) // 32
                y_cell = (spawn[0] + x_pac - anchor[0]) // 32
                if gum_grid[x_cell][y_cell]:
                    gum_grid[x_cell][y_cell] = False
                    if ((x_cell == 0 and y_cell == 0) or
                       (x_cell == 0 and y_cell == 14)
                       or (x_cell == 14 and y_cell == 0)
                       or (x_cell == 14 and y_cell == 14)):
                        self.score += (self.parser
                                       .json_dict["points_per_super_pacgum"])

                        super_time = pygame.time.get_ticks()
                        super_pac = True
                        ghost_surf = [ghst_5surf] * 4
                    else:
                        self.score += (self.parser
                                       .json_dict["points_per_pacgum"])
                        pygame.mixer.music.load("audio/munch.mp3")
                        pygame.mixer.music.set_volume(0.7)
                        pygame.mixer.music.play()

                # Prevent pacman from advancing if the path is closed
                # in the movement direction
                if pac_dir == Dir.LEFT and grid[x_cell][y_cell][0] == "1":
                    x_spd = 0
                    y_spd = 0
                elif pac_dir == Dir.DOWN and grid[x_cell][y_cell][1] == "1":
                    x_spd = 0
                    y_spd = 0
                elif pac_dir == Dir.RIGHT and grid[x_cell][y_cell][2] == "1":
                    x_spd = 0
                    y_spd = 0
                elif pac_dir == Dir.UP and grid[x_cell][y_cell][3] == "1":
                    x_spd = 0
                    y_spd = 0

            # Move to next level of all pacgums have been collected.
            pacgum_num = 0
            for row in gum_grid:
                pacgum_num += sum(row)
            if pacgum_num <= 0:
                if lev_no >= 10:
                    self.gameover(True)
                if 1 <= lev_no < 10:
                    break

            # Update the position of Pacman
            x_pac += x_spd
            y_pac += y_spd
            pacman_rect.topleft = (spawn[0] + x_pac,
                                   spawn[1] + y_pac)

            # Display the remaning time
            cur_time = pygame.time.get_ticks()
            time_txt = (self.btnfont
                        .render("Time: " +
                                f"{(max_time - cur_time + rem_time) // 1000}s",
                                True,
                                "white"))
            self.screen.blit(time_txt, (0, level_rect.bottom + 100))

            # Check whether time of the level has ended.
            if (cur_time - rem_time >= max_time):
                if (cheat_mode):
                    rem_time = pygame.time.get_ticks()
                else:
                    self.gameover(False)

            self.screen.blit(lives_txt, (0, level_rect.bottom + 200))
            # Check whether time of the super state has ended.
            if (cur_time - super_time) > 10000:
                super_pac = False
                ghost_surf = [ghst_1surf, ghst_2surf, ghst_3surf, ghst_4surf]

            # Changes direction of ghosts every 32 frames.
            if not (ghost_c % 32):
                speeds = self.ghost_dir(grid, anchor, ghost_rect,
                                        (y_cell, x_cell), super_pac)
            ghost_c = (ghost_c + 1) % 32

            # Upon Pacman's collision with a ghost, the score increases if
            # super state was active, if otherwise, the player loses a life.
            for index, ghost in enumerate(ghost_rect):
                if ghost:
                    if collideRect(pacman_rect, ghost):
                        if super_pac:
                            ghost_rect[index] = None
                            self.score += (self.parser
                                           .json_dict["points_per_ghost"])
                            ghost_time[index] = pygame.time.get_ticks()
                            pygame.mixer.music.load("audio/numnum.mp3")
                            pygame.mixer.music.set_volume(0.7)
                            pygame.mixer.music.play()
                        elif not cheat_mode:
                            self.parser.json_dict["lives"] -= 1
                            lives -= 1
                            for idx, rect in enumerate(ghost_rect):
                                if rect is not None:
                                    rect.topleft = ghost_res[idx]
                            speeds = [(0, 0), (0, 0), (0, 0), (0, 0)]

                            if self.parser.json_dict["lives"] <= 0:
                                self.gameover(False)
                            else:  # If pacman got remaining lives
                                x_pac = 8
                                y_pac = 8
                                mov_dir = None
                                x_spd = 0
                                y_spd = 0
                                pygame.mixer.music.load("audio/ack.mp3")
                                pygame.mixer.music.set_volume(0.7)
                                pygame.mixer.music.play()

            # Revert back every ghost that spent over 5 seconds
            # in the fearful state.
            for index, time in enumerate(ghost_time):
                if time:
                    if (cur_time - time) > 5000:
                        ghost_time[index] = None
                        ghost_rect[index] = (ghost_surf[index].
                                             get_rect(topleft=ghost_res[index])
                                             )

            # Display ghosts and Pacman on the screen.
            self.ghost(ghost_rect, ghost_surf, speeds)
            self.screen.blit(pacman_surf, pacman_rect)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_4:
                        pygame.quit()
                        sys.exit()
                    if event.key == pygame.K_ESCAPE:
                        time = self.pause()
                        if (super_time):
                            if time:
                                super_time += time
                        for t in ghost_time:
                            if t:
                                if time:
                                    t += time
                        if time:
                            rem_time += time
                    # To determine the direction of pacman's movement
                    if event.key == pygame.K_UP:
                        mov_dir = Dir.UP
                    elif event.key == pygame.K_DOWN:
                        mov_dir = Dir.DOWN
                    elif event.key == pygame.K_RIGHT:
                        mov_dir = Dir.RIGHT
                    elif event.key == pygame.K_LEFT:
                        mov_dir = Dir.LEFT
                    elif event.key == pygame.K_l and cheat_mode:
                        if lev_no >= 10:
                            self.gameover(True)
                        return

            clock.tick(60)
            pygame.display.flip()

    def level(self, anchor: tuple[int, int], grid: list[list[str]]) -> None:
        """
            Draw the maze represented in the grid.

            Args:
                anchor: a tuple representing the topleft position
                    of the maze.
                grid: a list of lists representing the open and closed walls.
        """
        score = self.title_font.render(str(self.score), True, "yellow")
        self.screen.fill("#003049")
        self.screen.blit(score, score.get_rect(topleft=(0, 0)))
        tile = 32
        y = 0
        for row in grid:
            x = 0
            for cell in row:
                if cell[0] == "1":  # West
                    pygame.draw.line(
                        self.screen,
                        "white",
                        (anchor[0] + x * tile, anchor[1] + y * tile),
                        (anchor[0] + x * tile, anchor[1] + y * tile + tile),
                        2
                    )
                if cell[1] == "1":  # South
                    pygame.draw.line(
                        self.screen,
                        "white",
                        (anchor[0] + x * tile, anchor[1] + y * tile + tile),
                        (anchor[0] + x * tile + tile,
                            anchor[1] + y * tile + tile),
                        2
                    )
                if cell[2] == "1":  # East
                    pygame.draw.line(
                        self.screen,
                        "white",
                        (anchor[0] + x * tile + tile, anchor[1] + y * tile),
                        (anchor[0] + x * tile + tile,
                            anchor[1] + y * tile + tile),
                        2
                    )
                if cell[3] == "1":  # North
                    pygame.draw.line(
                        self.screen,
                        "white",
                        (anchor[0] + x * tile, anchor[1] + y * tile),
                        (anchor[0] + x * tile + tile, anchor[1] + y * tile),
                        2
                    )
                x += 1
            y += 1


def main(config_file: str) -> None:
    """Start the game

        Args:
            config_file: the name of the file where all configurations are.
    """
    try:
        game = Game(config_file)
        pygame.mixer.init()
        game.main_menu()
    except Exception as e:
        print("Error: ", e)


if __name__ == "__main__":
    main("config.json")
