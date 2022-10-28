from math import sqrt
import tkinter
from time import gmtime, asctime

from Abalone.AbaloneGrid import AbaloneType, AbaloneGame, Position, TypeAction

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
    margin_int = 3
    margin_ext = 5

    def __init__(self):
        # The panel of game is constituted of a re-scaling grid
        # containing it-self a canvas. at each re-scaling of the
        # grid,we calculate the tallest size possible for the
        # cases (squared) of the grid, et the dimensions of the
        # canvas are adapted in consequence.
        super().__init__()
        self.mode = AbaloneType.NORMAL
        self.n_lig, self.n_col = 9, 9  # initial grid = 9 x 9
        self.game = AbaloneGame(self.mode)

        # Link of the event <resize> with an adapted manager :
        self.bind("<Configure>", self.rescale)
        # Canvas :
        self.can = tkinter.Canvas(
            self, bg="dark olive green", borderwidth=0,
            highlightthickness=1, highlightbackground="white")
        self.width, self.height = 2, 2
        self.cote = 0

        self._action = [[]]
        # Link of the event <click of the mouse> with its manager :

        self.can.bind("<Button-1>", self.click)
        self.can.bind("<Button1-Motion>", self.mouse_move)
        self.can.bind("<Button1-ButtonRelease>", self.mouse_up)
        self.can.pack(side=tkinter.LEFT)
        # self.side_panel = Label(text="player 1")
        # self.side_panel.pack(side=RIGHT)
        self.side_panel = tkinter.Canvas(self, bg="white", borderwidth=0,
                                         highlightthickness=1,
                                         highlightbackground="white")
        self.side_panel.pack(side=tkinter.RIGHT,
                             expand=tkinter.YES, fill=tkinter.BOTH)
        self.message = tkinter.Label(self.side_panel, text="White's\n turn",
                                     font="Helvetica 18 bold",
                                     bg="white",
                                     borderwidth=0)
        self.message.place(relx=0.5, rely=0.33, anchor="center")
        self.print_score = tkinter.Label(self.side_panel, text="0 / 0",
                                         font="Helvetica 18 bold",
                                         bg="white",
                                         borderwidth=0)
        self.print_score.place(relx=0.5, rely=0.2, anchor="center")

        _side_canvas = tkinter.Canvas(self.side_panel,
                                      bg="white", borderwidth=0,
                                      highlightthickness=0,
                                      width=80, height=80)
        _side_canvas.place(relx=0.5, rely=0.666, anchor="center")
        _circle = _side_canvas.create_oval(0, 0, 79, 79,
                                           outline="red",
                                           width=1, fill="white")

        def _config_circle(fill):
            _side_canvas.itemconfig(_circle, fill=fill)

        self._config_message_circle = _config_circle

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
        l_max = (self.width - 2 * self.margin_ext) / self.n_col
        h_max = (self.height - 2 * self.margin_ext) * 2 / (
                2 + sqrt(3) * (self.n_lig - 1))
        # the side of a case would be the smallest of the two dimensions :
        self.cote = min(l_max, h_max)
        # -> establishment of new dimensions for the canvas :
        wide, high = self.cote * self.n_col + 2*self.margin_ext,\
            self.cote * (1 + (self.n_lig - 1)*sqrt(3)/2) + 2*self.margin_ext
        self.can.configure(width=wide, height=high)
        # Layout of the grid:
        self.can.delete(tkinter.ALL)  # erasing of the past Layouts
        # Layout of all the pawns,
        #   white or black according to the state of the game :
        for lig in range(self.n_lig):
            x0 = (lig - 4) * 1 / 2 * self.cote + self.margin_ext
            y1 = self.margin_ext + lig * sqrt(3)/2 * self.cote + self.margin_int
            y2 = y1 + self.cote - 2 * self.margin_int
            for c in range(self.n_col):
                try:
                    x1 = c * self.cote + x0 + self.margin_int
                    x2 = x1 + self.cote - 2 * self.margin_int
                    color = [None, "white", "black"][
                        self.game.grid[lig, c]]
                    self.can.create_oval(x1, y1, x2, y2, outline="grey",
                                         width=1, fill=color)
                except IndexError:
                    continue
        n_b, n_w = self.game.marbles_down
        if self.game.player % 2 == 1:
            n_b, n_w = [n_b, n_w][::-1]
        self.print_score.config(text=f"{n_b} / {n_w}")
        if 6 in self.game.marbles_down:
            if self.game.marbles_down[0] == 6:
                nb = 1
            else:
                nb = 0
            self.message.config(text=["White", "Black"][nb] + " has won")
            return  # ?
        else:
            self.message.config(
                text=[None, "White", "Black"][self.game.player+1] + "'s\n turn")
        self._config_message_circle(
            ["red", "white", "black"][self.game.player+1])

    def get_space(self, event):
        """get the space linked to the event"""

        item, = self.can.find_closest(event.x, event.y)
        x0, y0, x1, y1 = self.can.coords(item)
        x = (x0 + x1) / 2 - self.margin_ext
        y = (y0 + y1) / 2 - self.margin_ext
        h = self.cote * sqrt(3) / 2
        lig = int(y / h + 1 - 2/sqrt(3))
        col = int(x / self.cote - (lig - 4) * 1 / 2)
        try:
            self.game.grid[lig, col]
        except IndexError:
            raise tools.InvalidActionError("Selected space not in grid")
        return item, lig, col

    def click(self, event):
        """Management of the mouse click : move the pawns"""
        # We start to determinate the line and the columns of the pawn touched:
        item, lig, col = self.get_space(event)
        pos = Position(lig, col)
        if not self._action:
            self._action.append([])
        if not self._action[0]:
            try:
                ok = self.game.check_selection([pos])
            except tools.InvalidActionError:  # ?
                self._action = [[]]
                self.trace_grille()
                return
            if ok:
                self._action[0].append(pos)
                self.can.itemconfig(item, width=3, outline='red')
        else:
            self.can.itemconfig(item, width=3, outline='yellow')
            self._action.append(pos)
            try:
                type_action, _ = self.game.check_action(*self._action)
            except tools.InvalidActionError:
                self._action = [[]]
                self.trace_grille()
                return
            if type_action != TypeAction.INVALID:
                self.move()
            else:
                self.trace_grille()
            self._action = [[]]

    def mouse_move(self, event):
        # We start to determinate the line and the columns of the pawn touched:
        if len(self._action[0]) == 3:
            return
        item, lig, col = self.get_space(event)
        pos = Position(lig, col)
        if len(self._action) != 1:
            return
        if self.game.check_selection(self._action[0] + [pos]):
            self._action[0].append(pos)
            self.can.itemconfig(item, width=3, outline='red')

    def mouse_up(self, event):
        pass

    def move(self):
        # todo : for the moment saving blindly, check if move is possible ?
        self.history.save_new(self.game.copy())
        _ = self.game.play(tuple(self._action))
        self.trace_grille()


class AbaloneGUI(tkinter.Tk):
    """corps principal du programme"""

    def __init__(self):
        super().__init__()
        self.geometry("950x750")
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
        self.jeu.game = AbaloneGame(self.jeu.mode)
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
        self.jeu.game = state
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
