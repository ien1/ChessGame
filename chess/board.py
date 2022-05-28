
class Board:
    def __init__(self, x, y):
        self.x = x
        self.y = y

        self.b = [[None for i in range(x)] for j in range(y)]  # objects inside are text
        self.b_class = [[None for i in range(x)] for j in range(y)]  # objects inside are figure class

        # self.check_white = 
        self.last_pos = []

    def __repr__(self) -> str:
        return str(self.b)

    def __len__(self):
        return self.x * self.y

    def __setitem__(self, pos, val):
        self.b[pos[0]][pos[1]] = val

    def __getitem__(self, pos):
        return self.b[pos]

    # def activate(self, )

    def place_figures_to_original_pos(self):
        for i in range(len(self.b[1])):
            self.b[1][i] = "bp"  # black pawn
            self.b_class[1][i] = Pawn("white", self, [1, i])

            self.b[6][i] = "wp"  # white pawn
            self.b_class[6][i] = Pawn("white", self, [6, i])

        self[0, 0], self[0, 7], self[0, 1], self[0, 6], self[0, 3], self[0, 5], self[0, 6], self[0, 7] = "br", "br", "bn", "bn", "bb", "bb", "bq", "bk"
        self[7, 0], self[7, 7], self[7, 1], self[7, 6], self[7, 3], self[7, 5], self[7, 6], self[7, 7] = "wr", "wr", "wn", "wn", "wb", "wb", "wq", "wk"

        self.b_class[0, 0], self.b_class[0, 7], self.b_class[0, 1], self.b_class[0, 6], self.b_class[0, 3], self.b_class[0, 5], self.b_class[0, 6], self.b_class[0, 7] = Rook("black", self, [0, 0]), Rook("black", self, [0, 7]), Knight("black", self, [0, 1]), Knight("black", self, [0, 6]), Bishop("black", self, [0, 2]), Bishop("black", self, [0, 5]), Queen("black", self, [0, 3]), King("black", self, [0, 4])
        self.b_class[7, 0], self.b_class[7, 7], self.b_class[7, 1], self.b_class[7, 6], self.b_class[7, 3], self.b_class[7, 5], self.b_class[7, 6], self.b_class[7, 7] = Rook("black", self, [0, 0]), Rook("black", self, [0, 0]), Knight("white", self, [0, 0]), Knight("white", self, [0, 0]), Bishop("white", self, [0, 0]), Bishop("white", self, [0, 0]), Queen("white", self, [0, 0]), King("white", self, [0, 0])

if __name__ == "__main__":
    board = Board(8, 8)
    print("board:", board)
    print(board[0][1])