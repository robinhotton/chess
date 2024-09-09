from piece import Piece

class Pawn(Piece):
    def __init__(self, color: str, position: tuple):
        super().__init__(color, position)
        self.image_file = f"images/{self.color}_pawn.png"
        self.direction = 1 if self.color == 'white' else -1

    def get_legal_moves(self, board):
        moves = []
        row, col = self.position
        
        # Move two squares forward from starting position
        if ((self.color == 'white' and row == 1) or (self.color == 'black' and row == 6)) and (board[row + self.direction * 2][col] is None) and (self.position[1] == col):
            moves.append((row + 2 * self.direction, col))
        # Move forward
        if (0 <= row + self.direction < len(board)) and (board[row + self.direction][col] is None) and (self.position[1] == col):
            moves.append((row + self.direction, col))
        # capture diagonally right
        if (0 <= row + self.direction < len(board)) \
            and (0 <= col + 1 < len(board[row])) \
            and (board[row + self.direction][col + 1] is not None) \
            and (board[row + self.direction][col + 1].color != self.color):
            moves.append((row + self.direction, col + 1))
        # capture diagonally left
        if (0 <= row + self.direction < len(board)) \
            and (0 <= col - 1 < len(board[row])) \
            and (board[row + self.direction][col - 1] is not None) \
            and (board[row + self.direction][col - 1].color != self.color):
            moves.append((row + self.direction, col - 1))
        # Prise en passant
        # un peu complexe, a faire plus tard
        return moves
