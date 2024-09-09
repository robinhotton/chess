from piece import Piece
   
class Knight(Piece):
    def __init__(self, color: str, position: tuple):
        super().__init__(color, position)
        self.image_file = f"images/{self.color}_knight.png"

    def get_legal_moves(self, board):
        moves = []
        directions = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
        for direction in directions:
            new_row = self.position[0] + direction[0]
            new_col = self.position[1] + direction[1]
            if 0 <= new_row < len(board) and 0 <= new_col < len(board[0]):
                target_square = board[new_row][new_col]
                if target_square is None or target_square.color != self.color:
                    moves.append((new_row, new_col))
        return moves
