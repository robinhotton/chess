from board import Board

class GameController:
    def __init__(self):
        self.board = Board()
        self.current_turn = 'white'
        self.selected_piece = None
        self.game_over = False

    def switch_turn(self):
        self.current_turn = 'black' if self.current_turn == 'white' else 'white'

    def handle_click(self, position):
        if self.game_over:
            return

        if self.selected_piece is None:
            print('Trying selecting piece', position)
            self.select_piece(position)
        else:
            if self.move_piece(position):
                if self.is_checkmate(self.current_turn):
                    print(f"Checkmate! {self.current_turn.capitalize()} wins!")
                    self.game_over = True
                else:
                    self.switch_turn()
            else:
                self.selected_piece = None

    def select_piece(self, position):
        piece = self.board.board[position[0]][position[1]]
        if piece is not None and piece.color == self.current_turn:
            self.selected_piece = piece
            print('Selected piece', piece.__class__.__name__)
            return True
        print('No piece selected')
        return False

    def move_piece(self, position):
        if self.selected_piece:
            legal_moves = self.selected_piece.get_legal_moves(self.board.board)
            if position in legal_moves:
                original_position = self.selected_piece.position
                self.board.move_piece(self.selected_piece, position)
                if self.is_in_check(self.current_turn):
                    # Undo the move if it leaves the king in check
                    self.board.move_piece(self.selected_piece, original_position)
                    return False
                self.selected_piece = None
                return True
        return False

    def is_in_check(self, color):
        king_position = self.board.find_king(color)
        for row in self.board.board:
            for piece in row:
                if piece is not None and piece.color != color:
                    if king_position in piece.get_legal_moves(self.board.board):
                        return True
        return False

    def simulate_move(self, piece, move):
        """Simulates moving a piece and returns the new board state."""
        original_position = piece.position
        target_piece = self.board.board[move[0]][move[1]]

        self.board.board[original_position[0]][original_position[1]] = None
        self.board.board[move[0]][move[1]] = piece
        piece.position = move

        return original_position, target_piece

    def undo_move(self, piece, original_position, target_piece):
        """Undoes a simulated move."""
        self.board.board[piece.position[0]][piece.position[1]] = target_piece
        self.board.board[original_position[0]][original_position[1]] = piece
        piece.position = original_position

    def is_checkmate(self, color):
        for row in self.board.board:
            for piece in row:
                if piece is not None and piece.color == color:
                    original_position = piece.position
                    for move in piece.get_legal_moves(self.board.board):
                        original_position, target_piece = self.simulate_move(piece, move)
                        if not self.is_in_check(color):
                            self.undo_move(piece, original_position, target_piece)
                            return False
                        self.undo_move(piece, original_position, target_piece)
        return True
