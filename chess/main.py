from board import Board
from math import sqrt
from copy import deepcopy
import pygame as pg
from threading import Thread

class Figures:
    def __init__(self, color, board, position=[0, 0]):
        self.position = position
        self.color = color
        self.directions = []
        self.board = board
        self.name = ""  # consists of "bn" -> Black kNight, "bk" -> Black King
        self.is_enemy = lambda figure: figure[0] != self.name[0]
        self.value = 0
        self.image = None
        self.moved = False

    def possible_moves(self, board, position=None, last_pos=None):  # board is in lists of text form
        # exclude is list of positions, those will be interpreted as None
        if not position:
            position = self.position
        a = []
        for i in self.directions:
            for j in i:
                k = [position[0] + j[0], position[1] + j[1]]
                if -1 in k or 8 in k or 9 in k or -2 in k:
                    break
                if board[k[0]][k[1]]:
                    if self.is_enemy(board[k[0]][k[1]]):
                        a.append(k)
                    break
                a.append(k)
        return a

    def legal_moves(self, board, position=None, king=None, last_pos = None, move=False):
        own_king = self.find_figure(board, "wk")[0] if self.name[0] == "w" else self.find_figure(board, "bk")[0]
        if not king:
            king = self.board.b_class[own_king[0]][own_king[1]]
        possible_moves = self.possible_moves(board, position, last_pos=last_pos)
        if not position:
            position = self.position
        legal_moves = []
        for i in possible_moves:
            # position is the original position
            # i is the destination
            temp_board = deepcopy(board.b)
            temp_board[i[0]][i[1]] = temp_board[position[0]][position[1]]
            temp_board[position[0]][position[1]] = None
            if not king.is_attacked(temp_board):
                legal_moves.append(i)
        return legal_moves

    def find_figure(self, board, name):
        finds = []
        for i in range(8):
            if name in board[i]:
                finds.append([i, board[i].index(name)])
        return finds

    def __repr__(self):
        return f"'{self.name}'"

    def __eq__(self, other):
        return self.value == other.value

    def __lt__(self, other):
        return self.value < other.value

    def __le__(self, other):
        return self.value <= other.value

    def move_to(self, position, last_pos=None, possible=None):
        if possible=="temp" or position in possible:
            if self.board[position[0]][position[1]]:
                self.board.b_class[position[0]][position[1]].kill_self()
            self.board.b_class[position[0]][position[1]] = self
            x, y = self.position
            self.board[x, y] = None
            self.board.b_class[x][y] = None
            self.board[position[0], position[1]] = self.name
            self.board.last_pos = [self.position, position]
            self.position = position
            self.moved = True
            f_king = "wk" if self.name[0] == "b" else "bk"
            king = self.find_figure(self.board, f_king)[0]
            if self.board.b_class[king[0]][king[1]].is_checkmate(self.board):
                return "checkmate"
            return True
        return False

    def kill_self(self):
        del self

    def draw(self, screen, position):
        screen.blit(self.image, [position[0] * 100, position[1] * 100])

class Pawn(Figures):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "bp" if self.color == "black" else "wp"
        self.image = pg.transform.scale(pg.image.load(f"figures/{self.color[0]}pawn.png"), (100, 100))
    
    def possible_moves(self, board:Board, position=None, last_pos=None)->list:
        if not last_pos:
            last_pos = self.board.last_pos  # [[0, 0], [0, 1]] -> only moves of pawns

        if not position:
            position = self.position

        direction = 1 if self.color == "black" else -1
        original = 1 if self.color == "black" else 6
        return_moves = []

        if position[0] == original and not board[position[0] + direction][position[1]] and not board[position[0] + direction * 2][position[1]]:
            return_moves.append([position[0] + direction, position[1]])
            return_moves.append([position[0] + direction * 2, position[1]])
        elif not board[position[0] + direction][position[1]]:
            return_moves.append([position[0] + direction, position[1]])

        if position[1] > 0 and board[position[0] + direction][position[1] - 1]:
            if board[position[0] + direction][position[1] - 1][0] != self.color[0]:
                return_moves.append([position[0] + direction, position[1] - 1])

        if position[1] < 7 and board[position[0] + direction][position[1] + 1]:
            if board[position[0] + direction][position[1] + 1][0] != self.color[0]:
                return_moves.append([position[0] + direction, position[1] + 1])

        if last_pos:
            if position[0] == original + 3 * direction and abs(last_pos[0][0] - last_pos[1][0]) == 2 and last_pos[0][1] in [position[1] + 1, position[1] - 1]:
                return_moves.append([position[0] + direction, last_pos[0][1]])

        return return_moves
    
    def move_to(self, position, last_pos=None, possible=None):
        if possible=="temp" or position in possible:
            if self.board[position[0]][position[1]]:
                self.board.b_class[position[0]][position[1]].kill_self()
            self.board.b_class[position[0]][position[1]] = self
            x, y = self.position
            self.board[x, y] = None
            self.board.b_class[x][y] = None
            self.board[position[0], position[1]] = self.name
            self.board.last_pos = [self.position, position]
            self.position = position
            direction = 1 if self.color[0] == "b" else -1
            if self.board.b_class[self.position[0]-direction][self.position[1]]:
                self.board.b_class[self.position[0]-direction][self.position[1]] = None
                self.board.b[self.position[0]-direction][self.position[1]] = None
            
            f_king = "wk" if self.name[0] == "b" else "bk"
            king = self.find_figure(self.board, f_king)[0]
            if self.board.b_class[king[0]][king[1]].is_checkmate(self.board):
                return "checkmate"
            return True
        return False


class Rook(Figures):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.directions = [
            [
                [0, 1],
                [0, 2], 
                [0, 3], 
                [0, 4], 
                [0, 5], 
                [0, 6], 
                [0, 7]
            ], 
            [
                [0, -1], 
                [0, -2], 
                [0, -3], 
                [0, -4], 
                [0, -5], 
                [0, -6], 
                [0, -7]
            ], 
            [
                [-1, 0], 
                [-2, 0], 
                [-3, 0], 
                [-4, 0], 
                [-5, 0], 
                [-6, 0], 
                [-7, 0]
            ], 
            [
                [1, 0], 
                [2, 0], 
                [3, 0], 
                [4, 0], 
                [5, 0], 
                [6, 0], 
                [7, 0]
            ]
        ]
        self.name = "br" if self.color == "black" else "wr"
        self.image = pg.transform.scale(pg.image.load(f"figures/{self.color[0]}rook.png"), (100, 100))


class Bishop(Figures):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.directions = [
            [
                [1, 1], 
                [2, 2], 
                [3, 3], 
                [4, 4], 
                [5, 5], 
                [6, 6], 
                [7, 7]
            ], 
            [
                [1, -1], 
                [2, -2], 
                [3, -3], 
                [4, -4], 
                [5, -5], 
                [6, -6], 
                [7, -7]
            ],
            [
                [-1, 1], 
                [-2, 2], 
                [-3, 3], 
                [-4, 4], 
                [-5, 5], 
                [-6, 6], 
                [-7, 7]
            ], 
            [
                [-1, -1], 
                [-2, -2], 
                [-3, -3], 
                [-4, -4], 
                [-5, -5], 
                [-6, -6], 
                [-7, -7]
            ]
        ]
        self.name = "bb" if self.color == "black" else "wb"
        self.image = pg.transform.scale(pg.image.load(f"figures/{self.color[0]}bishop.png"), (100, 100))


class Knight(Figures):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.directions = [
            [
                [1, 2]
            ], 
            [
                [1, -2]
            ], 
            [
                [-1, 2]
            ],
            [
                [-1, -2]
            ], 
            [
                [2, 1]
            ], 
            [
                [2, -1]
            ], 
            [
                [-2, 1]
            ], 
            [
                [-2, -1]
            ]
        ]
        self.name = "bn" if self.color == "black" else "wn"
        self.image = pg.transform.scale(pg.image.load(f"figures/{self.color[0]}knight.png"), (100, 100))


class King(Figures):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.directions = [
            [
                [-1, -1]
            ], 
            [
                [-1, 0]
            ], 
            [
                [0, -1]
            ],
            [
                [-1, 1]
            ], 
            [
                [1, -1]
            ], 
            [
                [0, 1]
            ], 
            [
                [1, 0]
            ], 
            [
                [1, 1]
            ]
        ]

        self.attacks = {
            "diagonal": 
            [
            [
                [1, 1], 
                [2, 2], 
                [3, 3], 
                [4, 4], 
                [5, 5], 
                [6, 6], 
                [7, 7]
            ], 
            [
                [1, -1], 
                [2, -2], 
                [3, -3], 
                [4, -4], 
                [5, -5], 
                [6, -6], 
                [7, -7]
            ],
            [
                [-1, 1], 
                [-2, 2], 
                [-3, 3], 
                [-4, 4], 
                [-5, 5], 
                [-6, 6], 
                [-7, 7]
            ], 
            [
                [-1, -1], 
                [-2, -2], 
                [-3, -3], 
                [-4, -4], 
                [-5, -5], 
                [-6, -6], 
                [-7, -7]
            ]
            ],
            "horizontal_vertical": 
            [
            [
                [0, 1],
                [0, 2], 
                [0, 3], 
                [0, 4], 
                [0, 5], 
                [0, 6], 
                [0, 7]
            ], 
            [
                [0, -1], 
                [0, -2], 
                [0, -3], 
                [0, -4], 
                [0, -5], 
                [0, -6], 
                [0, -7]
            ], 
            [
                [-1, 0], 
                [-2, 0], 
                [-3, 0], 
                [-4, 0], 
                [-5, 0], 
                [-6, 0], 
                [-7, 0]
            ], 
            [
                [1, 0], 
                [2, 0], 
                [3, 0], 
                [4, 0], 
                [5, 0], 
                [6, 0], 
                [7, 0]
            ]
            ],
            "knight": [
            [
                [1, 2]
            ], 
            [
                [1, -2]
            ], 
            [
                [-1, 2]
            ],
            [
                [-1, -2]
            ], 
            [
                [2, 1]
            ], 
            [
                [2, -1]
            ], 
            [
                [-2, 1]
            ], 
            [
                [-2, -1]
            ]
            ]
        }

        self.name = "wk" if self.color == "white" else "bk"
        self.image = pg.transform.scale(pg.image.load(f"figures/{self.color[0]}king.png"), (100, 100))

    def get_directions(self, board, directions, position=None):
        if not position:
            position = self.position
        a = []
        for i in directions:
            for j in i:
                k = [position[0] + j[1], position[1] + j[0]]
                if -1 in k or 8 in k or 9 in k or -2 in k:
                    break
                if board[k[0]][k[1]]:
                    if self.is_enemy(board[k[0]][k[1]]):
                        a.append(k)
                    break
        return a

    def is_attacked(self, board, position=None):
        if not position:
            position = self.position
        
        for i in self.attacks:
            temp_directions = self.get_directions(board, self.attacks[i], position)
            for j in temp_directions:
                if i == "diagonal" and board[j[0]][j[1]][1] in ["q", "b"] or i == "horizontal_vertical" and board[j[0]][j[1]][1] in ["r", "q"] or i == "knight" and board[j[0]][j[1]][1] in ["n"]:
                    return True
        if self.color == "white":
            if position[1] < 7 and board[position[0] - 1][position[1] + 1] == "bp":
                return True
            if position[1] > 0 and board[position[0] - 1][position[1] - 1] == "bp":
                return True
        if self.color == "black":
            if position[1] < 7 and board[position[0] + 1][position[1] + 1] == "wp":
                return True
            if position[1] > 0 and board[position[0] + 1][position[1] - 1] == "wp":
                return True
        
        return False

    def rochade(self, board, position=None):
        possible_moves = []
        if not position:
            position = self.position
        if not self.moved:
            if board[position[0]][position[1] + 3] and board[position[0]][position[1] + 3][0] == self.name[0] and board[position[0]][position[1] + 3][1] == "r":
                if not board.b_class[position[0]][position[1] + 3].moved and not self.is_attacked(board):
                    possible = True
                    for i in range(1, 3):
                        temp_board = deepcopy(board.b)
                        temp_board[position[0]][position[1]+i] = temp_board[position[0]][position[1]]
                        temp_board[position[0]][position[1]] = None
                        if self.is_attacked(temp_board, position=[position[0], position[1] + i]) or board[position[0]][position[1] + i]:
                            possible=False
                    if possible:
                        possible_moves.append([position[0], position[1] + 2])
            if board[position[0]][position[1] - 4] and board[position[0]][position[1] - 4][0] == self.name[0] and board[position[0]][position[1] - 4][1] == "r":
                if not board.b_class[position[0]][position[1] - 4].moved and not self.is_attacked(board):
                    possible = True
                    for i in range(1, 4):
                        temp_board = deepcopy(board.b)
                        temp_board[position[0]][position[1]-i] = temp_board[position[0]][position[1]]
                        temp_board[position[0]][position[1]] = None
                        if self.is_attacked(temp_board, position=[position[0], position[1] - i]) or board[position[0]][position[1] - i]:
                            possible=False
                    if possible:
                        possible_moves.append([position[0], position[1] - 3])
        return possible_moves

    def legal_moves(self, board, position=None, king=None, last_pos = None):
        if not position:
            position = self.position
        possible_moves = self.possible_moves(board, position, last_pos=last_pos) + self.rochade(board, position)
        # return possible_moves
        legal_moves_ = []
        for i in possible_moves:
            # position is the original position
            # i is the destination
            temp_board = deepcopy(board.b)
            temp_board[i[0]][i[1]] = temp_board[position[0]][position[1]]
            temp_board[position[0]][position[1]] = None
            attacked = self.is_attacked(temp_board, i)
            if not self.is_attacked(temp_board, i):
                legal_moves_.append(i)
        return legal_moves_

    def is_checkmate(self, board, position=None):
        if not position:
            position = self.position
        if not self.is_attacked(board, position=position):
            return False
        for i in self.board.b_class:
            for j in i:
                if j and j.name[0] == self.name[0]:
                    if j.legal_moves(board):
                        return False
        return True

    def move_to(self, position, last_pos=None, possible=None):
        if possible=="temp" or position in possible:
            if self.board[position[0]][position[1]]:
                self.board.b_class[position[0]][position[1]].kill_self()
            self.board.b_class[position[0]][position[1]] = self
            x, y = self.position
            self.board[x, y] = None
            self.board.b_class[x][y] = None
            self.board[position[0], position[1]] = self.name
            self.board.last_pos = [self.position, position]
            if position[1] > self.position[1] + 1:
                self.board.b_class[self.position[0]][self.position[1] + 3].move_to([self.position[0], self.position[1] + 1], "temp")
            if position[1] < self.position[1] - 1:
                self.board.b_class[self.position[0]][self.position[1] - 4].move_to([self.position[0], self.position[1] - 2], "temp")
            self.position = position
            self.moved = True
            if self.is_checkmate(self.board):
                return "checkmate"
            return True
        return False

class Queen(Figures):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.directions = [
            [
                [1, 1], 
                [2, 2], 
                [3, 3], 
                [4, 4], 
                [5, 5], 
                [6, 6], 
                [7, 7]
            ], 
            [
                [1, -1], 
                [2, -2], 
                [3, -3], 
                [4, -4], 
                [5, -5], 
                [6, -6], 
                [7, -7]
            ],
            [
                [-1, 1], 
                [-2, 2], 
                [-3, 3], 
                [-4, 4], 
                [-5, 5], 
                [-6, 6], 
                [-7, 7]
            ], 
            [
                [-1, -1], 
                [-2, -2], 
                [-3, -3], 
                [-4, -4], 
                [-5, -5], 
                [-6, -6], 
                [-7, -7]
            ],
            [
                [0, 1],
                [0, 2], 
                [0, 3], 
                [0, 4], 
                [0, 5], 
                [0, 6], 
                [0, 7]
            ], 
            [
                [0, -1], 
                [0, -2], 
                [0, -3], 
                [0, -4], 
                [0, -5], 
                [0, -6], 
                [0, -7]
            ], 
            [
                [-1, 0], 
                [-2, 0], 
                [-3, 0], 
                [-4, 0], 
                [-5, 0], 
                [-6, 0], 
                [-7, 0]
            ], 
            [
                [1, 0], 
                [2, 0], 
                [3, 0], 
                [4, 0], 
                [5, 0], 
                [6, 0], 
                [7, 0]
            ]
        ]
        self.name = "bq" if self.color == "black" else "wq"
        self.image = pg.transform.scale(pg.image.load(f"figures/{self.color[0]}queen.png"), (100, 100))

class Game:

    def __init__(self):
        self.original_board = [
            ["br", "bn", "bb", "bq", "bk", "bb", "bn", "br"],

            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],

            [None, None, None, None, None, None, None, None],

            [None, None, None, None, None, None, None, None],

            [None, None, None, None, None, None, None, None],

            [None, None, None, None, None, None, None, None],

            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],

            ["wr", "wn", "wb", "wq", "wk", "wb", "wn", "wr"],
        ]

        self.class_board = Board(8, 8)
        self.class_board.b = deepcopy(self.original_board)

        self.class_board.b_class = self.create_b_class(self.original_board, self.class_board)


        pg.init()

        pg.font.init()
        self.font = pg.font.SysFont("Roboto Regular", 20, False, False)
        self.font_win = pg.font.SysFont("Roboto Regular", 50, False, False)

        self.width = 800
        self.height = 800
        self.screen = pg.display.set_mode((self.width, self.height))

        self.run = False
        self.selected = []
        self.last_move = []
        self.white_choice = True
        self.playing = False
        self.checkmate=False

        self.robot_color = None

    def start_game(self):
        self.playing = True
        self.run=True
        while self.run:
            # for i in self.class_board.b:
            #     print(i)
            move = input("Move: ")
            from_ = move[:2]
            to_ = move[3:]
            selected_figure = self.class_board.b_class[8-int(from_[1])]["abcdefgh".index(from_[0])]
            if selected_figure.color[0] == "w" and not self.white_choice or selected_figure.color[0] == "b" and self.white_choice:
                continue
            # print(self.class_board.b_class[0][1])
            move_to = [8-int(to_[1]), "abcdefgh".index(to_[0])]
            self.last_move = [[8-int(from_[1]), "abcdefgh".index(from_[0])], move_to]
            possible = selected_figure.legal_moves(self.class_board)
            move = selected_figure.move_to(move_to, self.last_move, possible)
            print(move)
            if move:
                if move == "checkmate":
                    print("Checkmate!")
                    self.checkmate = True
                    self.playing = False
                else:
                    self.white_choice = not self.white_choice



    def create_b_class(self, board, class_board):
        b_class = []
        for i in range(len(board)):
            b_class.append([])
            for j in range(len(board[i])):
                if board[i][j] == "br":
                    b_class[-1].append(Rook("black", class_board, [i, j]))
                elif board[i][j] == "bn":
                    b_class[-1].append(Knight("black", class_board, [i, j]))
                elif board[i][j] == "bb":
                    b_class[-1].append(Bishop("black", class_board, [i, j]))
                elif board[i][j] == "bq":
                    b_class[-1].append(Queen("black", class_board, [i, j]))
                elif board[i][j] == "bk":
                    b_class[-1].append(King("black", class_board, [i, j]))
                elif board[i][j] == "bp":
                    b_class[-1].append(Pawn("black", class_board, [i, j]))
                elif board[i][j] == "wr":
                    b_class[-1].append(Rook("white", class_board, [i, j]))
                elif board[i][j] == "wn":
                    b_class[-1].append(Knight("white", class_board, [i, j]))
                elif board[i][j] == "wb":
                    b_class[-1].append(Bishop("white", class_board, [i, j]))
                elif board[i][j] == "wq":
                    b_class[-1].append(Queen("white", class_board, [i, j]))
                elif board[i][j] == "wk":
                    b_class[-1].append(King("white", class_board, [i, j]))
                elif board[i][j] == "wp":
                    b_class[-1].append(Pawn("white", class_board, [i, j]))
                else:
                    b_class[-1].append(None)
        return b_class


    def draw_circle_alpha(self, surface, color, center, radius):
            target_rect = pg.Rect(center, (0, 0)).inflate((radius * 2, radius * 2))
            shape_surf = pg.Surface(target_rect.size, pg.SRCALPHA)
            pg.draw.circle(shape_surf, color, (radius, radius), radius)
            surface.blit(shape_surf, target_rect)


    def update_screen(self, board, selected, screen, font, last_pos=None, checkmate=False):

        # draw rects
        string = "ABCDEFGH" if self.white_choice else "HGFEDCBA"
        for j in range(8):
            for i in range(8):
                if (j + i) % 2 == self.white_choice:
                    pg.draw.rect(screen, (255, 0, 0), (j * 100, i * 100, 100, 100))
                else:
                    pg.draw.rect(screen, (255, 255, 0), (j * 100, i * 100, 100, 100))
            screen.blit(font.render(string[j], True, (0, 0, 0), None), (j * 100 + 80, 780))
            if self.white_choice:
                screen.blit(font.render(str(8 - j), True, (0, 0, 0), None), (10, j * 100 + 10))
            else:
                screen.blit(font.render(str(j + 1), True, (0, 0, 0), None), (10, j * 100 + 10))

        
        # draw figures
        for i in range(len(board.b_class)):
            for j in range(len(board.b_class)):
                if board[i][j]:
                    if not self.white_choice:
                        board.b_class[i][j].draw(screen, [7-j, 7-i])
                    else:

                        board.b_class[i][j].draw(screen, [j, i])
        
        # draw possible moves
        if selected:
            possible = board.b_class[selected[0]][selected[1]].legal_moves(board, last_pos = last_pos)
            for i in possible:
                if not self.white_choice:
                    self.draw_circle_alpha(screen, (30, 100, 30, 120), ((7-i[1]) * 100 + 50, (7-i[0]) * 100 + 50), 30)
                else:
                    self.draw_circle_alpha(screen, (30, 100, 30, 120), (i[1] * 100 + 50, i[0] * 100 + 50), 30)


        if checkmate:
            if self.white_choice:
                text = "Winner is white!"
            else:
                text = "Winner is black!"


            screen.blit(self.font_win.render(text, True, (0, 0, 255), None), (270, 370))

        pg.display.update()


    def update_welcome_screen(self):
        self.screen.fill((200, 200, 200))

        self.screen.blit(self.font_win.render("CHESS GAME", True, (0, 0, 255), None), (267, 70))

        play_with_friend_rect = pg.draw.rect(self.screen, (30, 10, 50), (150, 200, 500, 100))
        play_with_friend_text = self.screen.blit(self.font_win.render("PLAY WITH A FRIEND", True, (0, 0, 255), None), (215, 235))

        play_with_robot_rect = pg.draw.rect(self.screen, (30, 10, 50), (150, 450, 500, 100))
        play_with_friend_text = self.screen.blit(self.font_win.render("PLAY WITH THE ROBOT", True, (0, 0, 255), None), (195, 485))

        pg.display.update()


    def eval_board(self, board):
        pass

    def game_over(self, board):
        pass

    def get_possible_moves(board, maximizing_player):
        pass

    def minimax(self, board, depth, alpha, beta, maximizing_player):
        if depth == 0 or self.game_over(board):
            return self.eval_board(board)
        if maximizing_player:
            maxeval = float("inf") * -1
            for child in self.get_possible_moves(board, maximizing_player):
                pass

    # color, board, position
    def start_draw(self):
        self.run=True
        while self.run:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.run = False
                    self.playing = False
                    break
                elif event.type == pg.MOUSEBUTTONDOWN:
                    x_, y_ = pg.mouse.get_pos()
                    x, y = x_ // 100, y_ // 100
                    if not self.white_choice:
                        x, y = 7-x, 7-y
                    if self.playing and not self.checkmate:
                        if self.selected and self.selected != [y, x]:
                            # print(x, y, selected)
                            possible = self.class_board.b_class[self.selected[0]][self.selected[1]].legal_moves(self.class_board, last_pos = self.last_move)
                            self.last_move = [self.selected, [y, x]]
                            move = self.class_board.b_class[self.selected[0]][self.selected[1]].move_to([y, x], self.last_move, possible)
                            self.selected = False
                            if move == "checkmate":
                                self.checkmate=True
                                continue
                            if move:
                                self.white_choice = not self.white_choice
                                # robot moves
                        elif self.class_board.b_class[y][x]:
                            if self.white_choice and self.class_board.b[y][x][0] == "w":
                                self.selected = [y, x]
                            elif not self.white_choice and self.class_board.b[y][x][0] == "b":
                                self.selected = [y, x]
                    elif self.checkmate:
                        # detect click on buttons
                        self.checkmate = False
                        self.playing = False
                    else:
                        # (150, 200, 500, 100)
                        if x_ in range(150, 650) and y_ in range(200, 300):
                            self.playing=True
                            self.checkmate=False
                            self.class_board.b = deepcopy(self.original_board)
                            self.class_board.b_class = self.create_b_class(self.original_board, self.class_board)
                            self.white_choice = True

                    
            if self.playing:
                self.update_screen(self.class_board, self.selected, self.screen, self.font, last_pos=self.last_move, checkmate=self.checkmate)
            else:
                self.update_welcome_screen()

        pg.quit()

if __name__ == "__main__":
    game = Game()
    t = Thread(target=game.start_game)
    t.start()
    game.start_draw()