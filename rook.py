from piece import Piece

class Rook(Piece):
    def __init__(self, color: str, position: tuple):
        super().__init__(color, position)
        self.image_file = f"images/{self.color}_rook.png"

    def get_legal_moves(self, board):
        moves = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for direction in directions:
            for i in range(1, len(board)):
                new_row = self.position[0] + direction[0] * i
                new_col = self.position[1] + direction[1] * i
                if 0 <= new_row < len(board) and 0 <= new_col < len(board[0]):
                    target_square = board[new_row][new_col]
                    if target_square is None:
                        moves.append((new_row, new_col))
                    elif target_square.color != self.color:
                        moves.append((new_row, new_col))
                        break
                    else:
                        break
                else:
                    break
        return moves
