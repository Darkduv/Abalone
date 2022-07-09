from math import sqrt
from tkinter import *

from Abalone.AbaloneGrid import *
from super_matrix import *


###########################################
#                                         #
#                                         #
#           Jeu de Abalone                #
#                                         #
#       Implementation in progress        #
#                                         #
#                                         #
#  Version du 12/03/2016 - Licence : ???  #
###########################################

# TODO  very awkward implementation of the moves ???

class MenuBar(Frame):
    """bar of menu rolling"""

    def __init__(self, boss=None):
        Frame.__init__(self, borderwidth=2, relief=GROOVE)
        # #### Menu <File> #####
        file_menu = Menubutton(self, text='File')
        file_menu.pack(side=LEFT, padx=5)
        me1 = Menu(file_menu)
        me1.add_command(label='Restart', underline=0,
                        command=boss.reset)
        me1.add_command(label='Quit', underline=0,
                        command=boss.quit)
        me1.add_command(label='Undo', underline=0,
                        command=boss.undo)
        file_menu.configure(menu=me1)

        # #### Menu <Help> #####
        help_menu = Menubutton(self, text='Help')
        help_menu.pack(side=LEFT, padx=5)
        me1 = Menu(help_menu)
        me1.add_command(label='Principe of the game', underline=0,
                        command=boss.principe)
        me1.add_command(label='By the way ...', underline=0,
                        command=boss.by_the_way)
        help_menu.configure(menu=me1)


class Panel(Frame):
    """Panel de jeu (grille de n x m cases)"""

    def __init__(self):
        # The panel of game is constituted of a re-scaling grid
        # containing it-self a canvas. at each re-scaling of the
        # grid,we calculate the tallest size possible for the
        # cases (squared) of the grid, et the dimensions of the
        # canvas are adapted in consequence.
        Frame.__init__(self)
        self.n_lig, self.n_col = 9, 9  # initial grid = 9 x 9
        self.state = AbaloneGrid()
        # Link of the event <resize> with an adapted manager :
        self.bind("<Configure>", self.rescale)
        # Canvas :
        self.can = Canvas(self, bg="dark olive green", borderwidth=0,
                          highlightthickness=1, highlightbackground="white")
        self.width, self.height = 2, 2
        self.cote = 0

        # Link of the event <click of the mouse> with its manager :

        self.several_x_y = [[]]
        self.can.bind("<Button-1>", self.click)
        # self.can.bind("<Button1-Motion>", self.mouse_move)
        # self.can.bind("<Button1-ButtonRelease>", self.mouse_up)
        self.can.pack(side=LEFT)
        # self.can_bis = Label(text="player 1")
        # self.can_bis.pack(side=RIGHT)
        self.can_bis = Canvas(self, bg="white", borderwidth=0,
                              highlightthickness=1, highlightbackground="white")
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
        self.can_bis.pack(side=RIGHT)
        self.player = 1
        self.counter = [0, 0]
        self.direction = [None, None]
        self.tte_directions = [[-1, 0], [-1, 1], [-1, -1], [0, 1], [0, -1], [1, -1]]
        self.history = SuperList()
        self.history.append([self.state.copy(), self.counter])
        self.init_jeu()

    def init_jeu(self):
        self.trace_grille()

    def rescale(self, event):
        """Operations made at each rescaling"""
        # the properties which are linked to the event of reconfiguration
        # contain all the new sizes of the panel :
        self.width, self.height = event.width - 4, event.height - 4
        # The subtract of 4 pixels allowed to compensate the width
        # of the 'highlightbordure" rolling the canvas)
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
        self.can.delete(ALL)  # erasing of the past Layouts
        # Layout of all the pawns, white or black according to the sate of the game :
        for l in range(self.n_lig):
            x0 = (l - 4) * 1 / 2 * self.cote + 3
            for c in range(self.n_col):
                try:
                    y1 = l * sqrt(3)/2 * self.cote + 3  # size of pawns =
                    y2 = (l * sqrt(3)/2 + 1) * self.cote - 3  # size of the case -6
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

    def click(self, event):
        """Management of the mouse click : move the pawns"""
        # We start to determinate the line and the columns of the pawn touched:
        lig = int(2 * event.y / (self.cote * sqrt(3) + sqrt(3) / 2 + 1))
        col = int((event.x - (lig - 4) * 1 / 2 * self.cote) / self.cote)
        if len(self.several_x_y[0]) == 3:
            # if self.verify1(lig, col, pawn=0):
            self.can.itemconfig(self.can.find_closest(event.x, event.y), width=3, outline='yellow')
            self.several_x_y.append([lig, col])
            self.move()
            self.several_x_y = [[]]
            # else:
            # self.several_x_y = []
        else:
            if self.state[(lig, col)] == self.player:
                self.several_x_y[0].append([lig, col])
                self.can.itemconfig(self.can.find_closest(event.x, event.y), width=3, outline='red')

    def mouse_move(self, event):
        # We start to determinate the line and the columns of the pawn touched:
        # lig = int(2 * event.y / (self.cote * sqrt(3) + sqrt(3) / 2 + 1))
        # col = int((event.x - (lig - 4) * 1 / 2 * self.cote) / self.cote)

        # print('self.several=', self.several_x_y, "...", self.several_x_y[0])
        if len(self.several_x_y) != 2 and len(self.several_x_y) != 0:
            lig = int(2 * event.y / (self.cote * sqrt(3) + sqrt(3) / 2 + 1))
            col = int((event.x - (lig - 4) * 1 / 2 * self.cote) / self.cote)
            print(lig, col)
            if self.several_x_y[0] and [lig, col] not in self.several_x_y[0] and self.verify1(lig, col):
                self.several_x_y[0].append([lig, col])
                self.can.itemconfig(self.can.find_closest(event.x, event.y), width=3, outline='red')

    def mouse_up(self, event):
        self.trace_grille()
        if len(self.several_x_y) == 2:
            self.trace_grille()
            self.move()
            self.direction = [None, None]
        else:
            self.several_x_y = [[]]
            type(event)

    def move(self):
        self.history.append([self.state.copy(), self.counter.copy()])
        l2, c2 = self.several_x_y[1]
        l1, c1 = self.several_x_y[0][0]
        direction = l2-l1, c2-c1
        l, c = direction
        l3, c3 = self.several_x_y[0][2]
        if self.state[(l3 + l, c3 + c)] == (self.player % 2) + 1:
            self.state[(l1, c1)] = 0
            self.state[(l3 + l, c3 + c)] = self.player
            try:
                while self.state[(l3+l, c3+c)] != 0:
                    l3 += l
                    c3 += c
                self.state[(l3+l, c3+c)] = (self.player % 2) + 1
            except IndexError:
                print("Player "+["white", "black"][(self.player % 2)]+" has lost a marble")
                self.counter[self.player % 2] += 1
                print(self.counter)
            self.player %= 2
            self.player += 1
            self.trace_grille()
        else:
            l, c = direction
            for pawn in self.several_x_y[0][::-1]:
                i, j = pawn
                self.state[(i+l, j+c)] = self.player
                self.state[(i, j)] = 0
            self.player %= 2
            self.player += 1
            self.trace_grille()

        # print("not made", self.player)

    #  def verify_right(self, x1, y1, x2, y2):  # todo finish!
    #  if x1 == x2 and y1 == y2:

    def verify1(self, lig, col, pawn=-1):
        print("hello")
        [x, y] = self.several_x_y[0][pawn]
        if pawn == -1:
            if self.state[(lig, col)] == self.player:
                direction = [lig - x, col - y]
                if self.direction:
                    if self.direction == direction:
                        return True
                    return False
                elif direction in self.tte_directions:
                    self.direction = direction
                    return True
                return False
            return False
        else:
            direction = [lig - x, col - y]
            if self.direction:
                if self.direction != direction:
                    return True
                return False
            elif direction in self.tte_directions:
                self.direction = direction
                return True
            return False


class Ping(Frame):
    """corps principal du programme"""

    def __init__(self):
        Frame.__init__(self)
        self.master.geometry("900x750")
        self.master.title(" Game of abalone")

        self.m_bar = MenuBar(self)
        self.m_bar.pack(side=TOP, expand=NO, fill=X)

        self.jeu = Panel()
        self.jeu.pack(expand=YES, fill=BOTH, padx=8, pady=8)

        self.pack()

    def reset(self):
        """  french!  """
        self.jeu.history = SuperList()
        self.jeu.state = AbaloneGrid()
        self.jeu.counter = [0, 0]
        self.jeu.history.append([self.jeu.state, self.jeu.counter])
        self.jeu.player = 1
        self.jeu.init_jeu()

    def principe(self):
        """window-message containing the small description of the principe of this game"""
        msg = Toplevel(self)
        Message(msg, bg="navy", fg="ivory", width=400,
                font="Helvetica 10 bold",
                text="This is to do "
                     "de"
                     " grilles.\n A  !\n\n"
                     "Réf : revue 'Pour la Science' - August 2002") \
            .pack(padx=10, pady=10)

    def by_the_way(self):
        """window-message indicating the author and the type of licence"""
        msg = Toplevel(self)
        Message(msg, width=200, aspect=100, justify=CENTER,
                text="Jeu de Abalone\n\n(C) Gerard Swinnen, August 2002.\n"
                     "Licence = GPL").pack(padx=10, pady=10)

    def undo(self):
        state = self.jeu.history.pop()
        self.jeu.state = state[0]
        self.jeu.counter = state[1].copy()
        self.jeu.player %= 2
        self.jeu.player += 1
        self.jeu.trace_grille()


if __name__ == '__main__':
    Ping().mainloop()
