from math import sqrt
import tkinter
from time import gmtime, asctime

from Abalone.AbaloneGrid import AbaloneGrid, AbaloneType

from game_tools import gui, tools
# see https://github.com/Darkduv/Games # game_tools


def my_print(*args, **kwargs):
    """for the moment critical information (when a bug occurs for example)

    It is displayed in the 'console' of your Python editor,
     with information on the date."""
    print("-", asctime(gmtime()), "GMT", ":", end="\n   ")
    print(*args, **kwargs)


# Todo : move's counter
# TODO = make a format for 'historic' and provide the option to save a game,
# TODO =        import a saved game and its historic.
###########################################
#                                         #
#                                         #
#           Game of Abalone 3.3           #
#                                         #
#       Implementation in progress        #
#                                         #
#                                         #
#  Version of 06/30/2018                  #
#  - Licence : ???                        #
###########################################


class Panel(tkinter.Frame):
    """Panel de jeu (grille de n x m cases)"""

    def __init__(self):
        # The panel of game is constituted of a re-scaling grid
        # containing it-self a canvas. at each re-scaling of the
        # grid,we calculate the tallest size possible for the
        # cases (squared) of the grid, et the dimensions of the
        # canvas are adapted in consequence.
        super().__init__()
        self.mode = AbaloneType.NORMAL
        self.n_lig, self.n_col = 9, 9  # initial grid = 9 x 9
        self.state = AbaloneGrid()

        # Link of the event <resize> with an adapted manager :
        self.bind("<Configure>", self.rescale)
        # Canvas :
        self.can = tkinter.Canvas(
            self, bg="dark olive green", borderwidth=0,
            highlightthickness=1, highlightbackground="white")
        self.width, self.height = 2, 2
        self.cote = 0

        # Link of the event <click of the mouse> with its manager :

        self.several_x_y = [[]]
        self.can.bind("<Button-1>", self.click)
        self.can.bind("<Button1-Motion>", self.mouse_move)
        self.can.bind("<Button1-ButtonRelease>", self.mouse_up)
        self.can.pack(side=tkinter.LEFT)
        # self.can_bis = Label(text="player 1")
        # self.can_bis.pack(side=RIGHT)
        self.can_bis = tkinter.Canvas(self, bg="white", borderwidth=0,
                                      highlightthickness=1,
                                      highlightbackground="white")
        self.turn = self.can_bis.create_text(self.can_bis.winfo_width() / 2, self.can_bis.winfo_height() / 3,
                                             text="White's\n turn", font="Helvetica 18 bold")
        self.print_score = self.can_bis.create_text(self.can_bis.winfo_width() / 2, self.can_bis.winfo_height() / 5,
                                                    text="0 / 0", font="Helvetica 18 bold")
        x1 = self.can_bis.winfo_width() / 3
        y = self.can_bis.winfo_height() * 2 / 3
        y1 = y - x1
        x2 = x1 * 2
        y2 = y + x1
        self.turn_bis = self.can_bis.create_oval(x1, y1, x2, y2, outline="red", width=1, fill="white")
        # self.can_bis = Label(text="Red's\n turn")
        self.can_bis.pack(side=tkinter.RIGHT)
        self.player = 1
        self.counter = [0, 0]
        self.direction = [None, None]
        self.tte_directions = [[-1, 0], [-1, 1], [1, -1], [0, 1], [0, -1], [1, 0]]
        self.history = tools.SimpleHistoric()
        self.init_jeu()

    def init_jeu(self):
        self.trace_grille()

    def rescale(self, event):
        """Operations made at each rescaling"""
        # the properties which are linked to the event of reconfiguration
        # contain all the new sizes of the panel :
        self.width, self.height = event.width - 4, event.height - 4
        # The subtraction of 4 pixels allowed to compensate the width
        # of the 'highlight bordure' rolling the canvas
        self.trace_grille()

    def trace_grille(self):
        """Layout of the grid, in function of dimensions and options"""
        # maximal width and height possibles for the cases :
        l_max = self.width / self.n_col
        h_max = self.height / (1 + sqrt(3) * 4)
        # the side of a case would be the smallest of the two dimensions :
        self.cote = min(l_max, h_max)
        # -> establishment of new dimensions for the canvas :
        wide, high = self.cote * self.n_col, self.cote * self.n_lig
        self.can.configure(width=wide, height=high)
        # Layout of the grid:
        self.can.delete(tkinter.ALL)  # erasing of the past Layouts
        # Layout of all the pawns,
        #   white or black according to the state of the game :
        for l in range(self.n_lig):
            x0 = (l - 4) * 1 / 2 * self.cote + 3
            for c in range(self.n_col):
                try:
                    y1 = l * sqrt(3) / 2 * self.cote + 3  # size of pawns =
                    # size of the case -6
                    y2 = (l * sqrt(3) / 2 + 1) * self.cote - 3
                    x1 = c * self.cote + x0
                    x2 = x1 + self.cote - 6
                    color = ["dark olive green", "white", "black"][self.state[(l, c)]]
                    self.can.create_oval(x1, y1, x2, y2, outline="grey",
                                         width=1, fill=color)
                except IndexError:
                    continue
        # self.can_bis.destroy()
        # self.can_bis = Label(text="Player{0}".format(["Big bug", "white", "black"][self.player]))
        self.can_bis.configure(width=self.width - wide, height=self.height)
        self.can_bis.delete(self.turn, self.turn_bis, self.print_score)
        if 6 in self.counter:
            if self.counter[0] == 6:
                nb = 1
            else:
                nb = 0
            self.turn = self.can_bis.create_text(self.can_bis.winfo_width() / 2, self.can_bis.winfo_height() / 3,
                                                 text=["White", "Black"][nb] + " has won",
                                                 font="Helvetica 18 bold")
            return  # ?
        else:
            self.turn = self.can_bis.create_text(self.can_bis.winfo_width() / 2, self.can_bis.winfo_height() / 3,
                                                 text=["Bug", "White", "Black"][self.player] + "'s\n turn",
                                                 font="Helvetica 18 bold")
        n_b, n_w = self.counter
        if self.player % 2 == 1:
            n_b, n_w = [n_b, n_w][::-1]
        self.print_score = self.can_bis.create_text(self.can_bis.winfo_width() / 2, self.can_bis.winfo_height() / 5,
                                                    text="{0} / {1}".format(n_b, n_w), font="Helvetica 18 bold")
        x = self.can_bis.winfo_width() / 3
        y = self.can_bis.winfo_height() / 3
        r = min([x, y, 40])
        y1 = y * 2 - r
        x1 = 3 * x / 2 - r
        x2 = 3 * x / 2 + r
        y2 = y * 2 + r
        self.turn_bis = self.can_bis.create_oval(x1, y1, x2, y2, outline="red",
                                                 width=1, fill=["red", "white", "black"][self.player])

    def get_space(self, event):
        """get the space linked to the event"""
        lig = int(2 * event.y / (self.cote * sqrt(3) + sqrt(3) / 2 + 1))
        col = int((event.x - (lig - 4) * 1 / 2 * self.cote) / self.cote)
        try:
            self.state[lig, col]
        except IndexError:
            raise tools.InvalidActionError("Selected space not in grid")
        return lig, col

    def click(self, event):
        """Management of the mouse click : move the pawns"""
        # We start to determinate the line and the columns of the pawn touched:
        lig, col = self.get_space(event)
        if not self.several_x_y[0]:
            if self.state[(lig, col)] == self.player:
                self.several_x_y[0].append([lig, col])
                self.can.itemconfig(self.can.find_closest(event.x, event.y), width=3, outline='red')
        else:

            self.can.itemconfig(self.can.find_closest(event.x, event.y), width=3, outline='yellow')
            self.several_x_y.append([lig, col])
            if self.verify2(lig, col):
                self.move()
            else:
                self.trace_grille()
            self.several_x_y = [[]]

    def mouse_move(self, event):
        # We start to determinate the line and the columns of the pawn touched:
        lig, col = self.get_space(event)
        if len(self.several_x_y) == 1:
            if [lig, col] not in self.several_x_y[0] and self.verify1(lig, col):
                self.several_x_y[0].append([lig, col])
                self.can.itemconfig(self.can.find_closest(event.x, event.y), width=3, outline='red')
        else:
            pass

    def mouse_up(self, event):
        pass

    def move(self):
        self.history.save_new([self.state.copy(), self.counter.copy()])
        l2, c2 = self.several_x_y[1]
        l1, c1 = self.several_x_y[0][0]
        direction = l2 - l1, c2 - c1
        l, c = direction
        if len(self.several_x_y[0]) == 1:
            if self.state[l2, c2] == 0:
                self.state[l2, c2] = self.player
                self.state[l1, c1] = 0
                self.player %= 2
                self.player += 1
                self.trace_grille()
            else:
                nb_marble = 1
                try:
                    while self.state[(l2, c2)] != 0:
                        nb_marble += 1
                        l2 += l
                        c2 += c
                    self.state[(l2, c2)] = self.state[l2-l, c2-c]
                except IndexError:
                    print("Player " + ["white", "black"][(self.player % 2)] + " has lost a marble")
                    self.counter[self.player % 2] += 1
                    print(self.counter)
                for i in range(nb_marble-1, 0, -1):
                    self.state[l2-l, c2-c] = self.state[l2-2*l, c2-2*c]
                    l2 -= l
                    c2 -= c
                self.state[l1, c1] = 0
                self.player %= 2
                self.player += 1
                self.trace_grille()
        else:
            for pawn in self.several_x_y[0][::-1]:
                i, j = pawn
                self.state[(i + l, j + c)] = self.player
                self.state[(i, j)] = 0
            self.player %= 2
            self.player += 1
            self.trace_grille()

    def verify2(self, lig, col):
        if len(self.several_x_y[0]) == 1:
            x, y = self.several_x_y[0][0]
            l, c = lig - x, col - y  # todo : here for legal move of one case ?
            if abs(l) > 1 or abs(c) > 1:
                my_print("Too long move")
                return False
            if self.state[lig, col] == 0 and [l, c] in self.tte_directions:
                return True
            else:
                if self.state[lig, col] != self.player:
                    return False
                else:
                    try:
                        nb_player = 1
                        while self.state[(x + l, y + c)] == self.player:
                            x += l
                            y += c
                            nb_player += 1
                            if nb_player > 3:
                                return False
                        if self.state[x+l, y+c] == 0:
                            return True
                        else:
                            try:
                                nb_enemy = 0
                                while nb_enemy < nb_player and self.state[x+l, y+c] == (self.player % 2 + 1):
                                    nb_enemy += 1
                                    x += l
                                    y += c
                                if nb_enemy >= nb_player:
                                        my_print("it's forbidden")
                                        return False
                                else:
                                    return True
                            except IndexError:
                                my_print("... ... ...")
                                return True
                    except IndexError:
                        return False
        else:
            x, y = self.several_x_y[0][0]
            d1, d2 = lig - x, col - y
            if abs(d1) > 1 or abs(d2) > 1:   # todo : here for legal move of one case ?
                my_print("Too long move")
                return False
            for [i, j] in self.several_x_y[0]:
                if self.state[i + d1, j + d2] != 0:
                    return False
            return True

    def verify1(self, lig, col):
        if self.state[lig, col] != self.player:
            return False
        else:
            x, y = self.several_x_y[0][-1]
            if not [lig - x, col - y] in self.tte_directions:
                return False
            else:
                if len(self.several_x_y[0]) >= 3:
                    return False
                elif len(self.several_x_y[0]) == 2:
                    d1, d2 = lig - x, col - y
                    x1, y1 = self.several_x_y[0][0]
                    if x - x1 == d1 and y - y1 == d2:
                        return True
                    else:
                        return True
                return True


class AbaloneGUI(tkinter.Tk):
    """corps principal du programme"""

    def __init__(self):
        super().__init__()
        self.geometry("900x750")
        self.title(" Game of abalone")

        menu_config = [
            ('File', [('Restart', self.reset),
                      ('Quit', self.destroy),
                      ('Undo', self.undo)]),
            ('Help', [('Principle of the game', self.principle),
                      ('About...', self.about)]),
            ('Options', [('Normal', self.normal_mode),
                         ('Split', self.split_mode)])
        ]
        # add options borderwidth=2, relief=GROOVE to Menu ?
        self.m_bar = gui.RecursiveMenuBar(self)
        self.m_bar.config_menu(menu_config)

        self.jeu = Panel()
        self.jeu.pack(expand=tkinter.YES, fill=tkinter.BOTH, padx=8, pady=8)

        self.bind("<Command-z>", self.undo)
        self.bind("<Command-r>", self.reset)

    def reset(self, event=None):
        """  french!  """
        self.jeu.history = tools.SimpleHistoric()
        self.jeu.state = AbaloneGrid(self.jeu.mode)
        self.jeu.counter = [0, 0]
        self.jeu.player = 1
        self.jeu.init_jeu()

    def principle(self):
        """Small description of the principle of this game"""
        msg = tkinter.Toplevel(self)
        tkinter.Message(msg, bg="navy", fg="ivory", width=400,
                        font="Helvetica 10 bold",
                        text="Put six marbles of the adversary "
                             "out of the grid\n\n"
                             "Réf : MAXIMIN PUISSANT") \
            .pack(padx=10, pady=10)

    def about(self):
        """About the development : author and type of licence"""
        msg = tkinter.Toplevel(self)
        tkinter.Message(msg, width=200, aspect=100, justify=tkinter.CENTER,
                        text="Jeu de Abalone 3.3\n\n Maximin Duvillard"
                        "\n Last update : 30/06/2018"
                        "\n Licence = None").pack(padx=10, pady=10)

    def undo(self, event=None):
        state = self.jeu.history.undo()
        self.jeu.state = state[0]
        self.jeu.counter = state[1].copy()
        self.jeu.player %= 2
        self.jeu.player += 1
        self.jeu.trace_grille()

    def mode(self):
        pass

    def normal_mode(self):
        self.jeu.mode = AbaloneType.NORMAL

    def split_mode(self):
        self.jeu.mode = AbaloneType.SPLIT


if __name__ == '__main__':
    Ab = AbaloneGUI()
    Ab.mainloop()
