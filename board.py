from pawn import Pawn
from knight import Knight
from bishop import Bishop
from rook import Rook
from queen import Queen
from king import King
from piece import Piece


class Board:
    def __init__(self):
        self.board = [[None for _ in range(8)] for _ in range(8)]
        self._setup_pieces()

    def _setup_pieces(self):
        # Set up pawns
        for col in range(8):
            self.board[1][col] = Pawn('white', (1, col))
            self.board[6][col] = Pawn('black', (6, col))

        # Set up other pieces
        pieces = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
        for col, piece_cls in enumerate(pieces):
            self.board[0][col] = piece_cls('white', (0, col))
            self.board[7][col] = piece_cls('black', (7, col))

    def move_piece(self, piece: Piece, new_position: tuple):
        old_position = piece.position
        self.board[old_position[0]][old_position[1]] = None
        self.board[new_position[0]][new_position[1]] = piece
        piece.move(new_position)
        
    def affiche(self):
        for row in self.board:
            print([(f"{piece.color} {piece.__class__.__name__}", (piece.position[0], piece.position[1])) if piece is not None else None for piece in row])

    def find_king(self, color):
        for row in self.board:
            for piece in row:
                if piece is not None and isinstance(piece, King) and piece.color == color:
                    return piece.position
        return None