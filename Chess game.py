import pygame
import sys
import math
import random
import copy # Keep for AI

# --- Constants (Keep from original logic) ---
WIDTH = 8
HEIGHT = 8

# Piece representations (Keep for logic, images used for display)
PIECES = {
    'bR': '♜', 'bN': '♞', 'bB': '♝', 'bQ': '♛', 'bK': '♚', 'bP': '♟',
    'wR': '♖', 'wN': '♘', 'wB': '♗', 'wQ': '♕', 'wK': '♔', 'wP': '♙',
    None: '.'
}

# Piece values for evaluation (Keep for AI)
PIECE_VALUES = {
    'P': 1, 'N': 3, 'B': 3, 'R': 5, 'Q': 9, 'K': 1000
}

# --- Pygame Specific Constants ---
SQ_SIZE = 64 # Size of each square in pixels
BOARD_WIDTH = WIDTH * SQ_SIZE
BOARD_HEIGHT = HEIGHT * SQ_SIZE
SCREEN_WIDTH = BOARD_WIDTH
SCREEN_HEIGHT = BOARD_HEIGHT # Can add space for status messages later
IMAGES = {} # Dictionary to hold loaded piece images

# Colors
WHITE = (235, 235, 208)
BLACK = (119, 148, 85)
HIGHLIGHT_COLOR = (255, 255, 51, 150) # Yellowish with transparency
VALID_MOVE_COLOR = (135, 152, 105, 150) # Darker green overlay

# --- ChessGame Class (Mostly Unchanged) ---
# (Paste the entire ChessGame class from the previous AI example here)
# ... (Make sure it includes __init__, _setup_board, get_piece_at, parse_move,
#      is_valid_square, is_valid_move, all _is_valid_..._move methods,
#      _is_path_clear, make_move, undo_move, _coords_to_algebraic,
#      generate_all_valid_moves, get_piece_value, evaluate_board,
#      get_ai_move, get_ai_move_level_0, _1, _2, minimax)
# Important: Remove or comment out self.print_board() if it exists.
# Important: Ensure is_valid_move uses turn_color correctly.

class ChessGame:
    """Represents the state and rules of a chess game."""

    def __init__(self, ai_difficulty=None):
        """Initializes the board, game state, and AI difficulty."""
        self.board = self._setup_board()
        self.current_turn = 'w' # 'w' for white, 'b' for black
        self.ai_difficulty = ai_difficulty # None for PvP, 0, 1, 2 for AI levels
        self.move_log = [] # Optional: To keep track of moves
        # --- Add game over state ---
        self.game_over = False
        self.winner = None # 'w', 'b', or 'draw'

    def _setup_board(self):
        board = [[None for _ in range(WIDTH)] for _ in range(HEIGHT)]
        board[0] = ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR']
        board[1] = ['bP'] * WIDTH
        board[6] = ['wP'] * WIDTH
        board[7] = ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']
        return board

    # --- Keep all the validation and move logic methods ---
    # get_piece_at, parse_move, is_valid_square, is_valid_move,
    # _is_valid_pawn_move, _is_valid_rook_move, ... King, _is_path_clear

    def get_piece_at(self, row, col):
        if 0 <= row < HEIGHT and 0 <= col < WIDTH:
            return self.board[row][col]
        return None

    def parse_move(self, move_str):
        if len(move_str) != 4: return None
        start_col_char, start_row_char, end_col_char, end_row_char = move_str
        if not ('a' <= start_col_char <= 'h' and '1' <= start_row_char <= '8' and
                'a' <= end_col_char <= 'h' and '1' <= end_row_char <= '8'): return None
        start_col = ord(start_col_char) - ord('a')
        start_row = 8 - int(start_row_char)
        end_col = ord(end_col_char) - ord('a')
        end_row = 8 - int(end_row_char)
        # Basic bounds check for array access
        if not (0 <= start_row < HEIGHT and 0 <= start_col < WIDTH and
                0 <= end_row < HEIGHT and 0 <= end_col < WIDTH):
            return None
        return ((start_row, start_col), (end_row, end_col))

    def is_valid_square(self, row, col):
        return 0 <= row < HEIGHT and 0 <= col < WIDTH

    def is_valid_move(self, start_pos, end_pos, turn_color=None):
        start_row, start_col = start_pos
        end_row, end_col = end_pos

        active_turn = turn_color if turn_color else self.current_turn

        if not (self.is_valid_square(start_row, start_col) and self.is_valid_square(end_row, end_col)): return False
        if start_pos == end_pos: return False

        piece = self.get_piece_at(start_row, start_col)
        target_piece = self.get_piece_at(end_row, end_col)

        if piece is None: return False
        if piece[0] != active_turn: return False
        if target_piece is not None and target_piece[0] == active_turn: return False

        piece_type = piece[1]
        is_capture = target_piece is not None

        valid_piece_move = False
        if piece_type == 'P':
            valid_piece_move = self._is_valid_pawn_move(start_pos, end_pos, is_capture, active_turn)
        elif piece_type == 'R':
            valid_piece_move = self._is_valid_rook_move(start_pos, end_pos)
        elif piece_type == 'N':
            valid_piece_move = self._is_valid_knight_move(start_pos, end_pos)
        elif piece_type == 'B':
            valid_piece_move = self._is_valid_bishop_move(start_pos, end_pos)
        elif piece_type == 'Q':
            valid_piece_move = self._is_valid_queen_move(start_pos, end_pos)
        elif piece_type == 'K':
             valid_piece_move = self._is_valid_king_move(start_pos, end_pos)

        if not valid_piece_move: return False

        if piece_type in ['R', 'B', 'Q']:
            if not self._is_path_clear(start_pos, end_pos): return False

        # Basic check - does move leave king in check? (Simplified - not implemented yet)
        # if self.move_leaves_king_in_check(start_pos, end_pos, active_turn): return False

        return True

    def _is_valid_pawn_move(self, start_pos, end_pos, is_capture, color):
        start_row, start_col = start_pos
        end_row, end_col = end_pos
        dr = end_row - start_row; dc = end_col - start_col
        direction = -1 if color == 'w' else 1
        start_rank = 6 if color == 'w' else 1

        if not is_capture and dc == 0 and dr == direction and self.get_piece_at(end_row, end_col) is None: return True
        if (not is_capture and dc == 0 and dr == 2 * direction and
            start_row == start_rank and self.get_piece_at(end_row, end_col) is None and
            self.get_piece_at(start_row + direction, start_col) is None): return True
        if is_capture and abs(dc) == 1 and dr == direction: return True
        return False # Add en passant later

    def _is_valid_rook_move(self, start_pos, end_pos):
        start_row, start_col = start_pos; end_row, end_col = end_pos
        return start_row == end_row or start_col == end_col

    def _is_valid_knight_move(self, start_pos, end_pos):
        start_row, start_col = start_pos; end_row, end_col = end_pos
        dr = abs(end_row - start_row); dc = abs(end_col - start_col)
        return (dr == 2 and dc == 1) or (dr == 1 and dc == 2)

    def _is_valid_bishop_move(self, start_pos, end_pos):
        start_row, start_col = start_pos; end_row, end_col = end_pos
        return abs(end_row - start_row) == abs(end_col - start_col)

    def _is_valid_queen_move(self, start_pos, end_pos):
        return self._is_valid_rook_move(start_pos, end_pos) or \
               self._is_valid_bishop_move(start_pos, end_pos)

    def _is_valid_king_move(self, start_pos, end_pos):
        start_row, start_col = start_pos; end_row, end_col = end_pos
        return max(abs(end_row - start_row), abs(end_col - start_col)) == 1 # Add castling later

    def _is_path_clear(self, start_pos, end_pos):
        start_row, start_col = start_pos; end_row, end_col = end_pos
        dr = end_row - start_row; dc = end_col - start_col
        step_row = 0 if dr == 0 else (1 if dr > 0 else -1)
        step_col = 0 if dc == 0 else (1 if dc > 0 else -1)
        current_row, current_col = start_row + step_row, start_col + step_col
        while (current_row, current_col) != (end_row, end_col):
            if not self.is_valid_square(current_row, current_col): return False
            if self.get_piece_at(current_row, current_col) is not None: return False
            current_row += step_row; current_col += step_col
        return True

    def make_move(self, start_pos, end_pos):
        start_row, start_col = start_pos
        end_row, end_col = end_pos
        piece = self.board[start_row][start_col]
        captured_piece = self.board[end_row][end_col]

        if piece is None: return None, None # Should not happen if logic is correct

        self.board[end_row][end_col] = piece
        self.board[start_row][start_col] = None
        promoted_to = None

        # Pawn Promotion (Auto-Queen for now)
        if piece[1] == 'P':
            if (piece[0] == 'w' and end_row == 0) or (piece[0] == 'b' and end_row == 7):
                promoted_to = piece[0] + 'Q'
                self.board[end_row][end_col] = promoted_to

        # Log move before switching turn
        self.move_log.append(((start_row, start_col), (end_row, end_col), captured_piece, promoted_to))

        # Switch turn
        self.current_turn = 'b' if self.current_turn == 'w' else 'w'

        # --- Check for game over AFTER move ---
        self.check_game_over()

        return piece, captured_piece

    def undo_move(self):
        if not self.move_log: return False
        last_move = self.move_log.pop()
        start_pos, end_pos, captured_piece, promoted_to = last_move
        start_row, start_col = start_pos; end_row, end_col = end_pos
        moved_piece_after_move = self.board[end_row][end_col] # Might be the promoted piece

        # Determine the piece that *originally* moved
        original_moved_piece = promoted_to[0] + 'P' if promoted_to else moved_piece_after_move

        # Move piece back
        self.board[start_row][start_col] = original_moved_piece
        # Restore captured piece (or None if it was empty)
        self.board[end_row][end_col] = captured_piece

        # Switch turn back
        self.current_turn = 'b' if self.current_turn == 'w' else 'w'

        # --- Reset game over state if undoing ---
        self.game_over = False
        self.winner = None
        return True

    def _coords_to_algebraic(self, pos):
        row, col = pos
        if not self.is_valid_square(row, col): return "Invalid"
        return f"{chr(ord('a') + col)}{8 - row}"

    def generate_all_valid_moves(self, color):
        valid_moves = []
        for r_start in range(HEIGHT):
            for c_start in range(WIDTH):
                piece = self.get_piece_at(r_start, c_start)
                if piece and piece[0] == color:
                    for r_end in range(HEIGHT):
                        for c_end in range(WIDTH):
                            start_pos = (r_start, c_start)
                            end_pos = (r_end, c_end)
                            # Temporarily switch turn to check validity from the perspective of 'color'
                            original_turn = self.current_turn
                            self.current_turn = color
                            is_valid = self.is_valid_move(start_pos, end_pos, turn_color=color)
                            self.current_turn = original_turn # Switch back!

                            if is_valid:
                                # --- Add check detection simulation (basic) ---
                                # # Simulate the move
                                # moved_p, captured_p = self.make_move(start_pos, end_pos)
                                # # Check if the king of 'color' is now in check
                                # in_check = self.is_king_in_check(color)
                                # # Undo the move
                                # self.undo_move()
                                # # Only add if move doesn't leave king in check
                                # if not in_check:
                                #     valid_moves.append((start_pos, end_pos))
                                # Currently, we skip the check detection part for simplicity
                                valid_moves.append((start_pos, end_pos))

        return valid_moves

    # --- Add Check and Game Over Logic ---
    def find_king(self, color):
        """Finds the coordinates of the king of the specified color."""
        king_char = color + 'K'
        for r in range(HEIGHT):
            for c in range(WIDTH):
                if self.board[r][c] == king_char:
                    return (r, c)
        return None # Should not happen in a normal game

    def is_square_attacked(self, row, col, attacker_color):
        """Checks if the given square is attacked by any piece of the attacker_color."""
        opponent_color = 'w' if attacker_color == 'b' else 'b'
        # Temporarily switch turn perspective for validation
        original_turn = self.current_turn
        self.current_turn = attacker_color
        for r_start in range(HEIGHT):
            for c_start in range(WIDTH):
                piece = self.get_piece_at(r_start, c_start)
                if piece and piece[0] == attacker_color:
                    # Can the attacker piece move to the target square?
                    # Need to handle pawn capture differently
                    if piece[1] == 'P':
                        direction = -1 if attacker_color == 'w' else 1
                        if r_start + direction == row and abs(c_start - col) == 1:
                             self.current_turn = original_turn # Restore turn
                             return True # Pawn capture threat
                    # Check standard move validation for other pieces
                    elif self.is_valid_move((r_start, c_start), (row, col), turn_color=attacker_color):
                        self.current_turn = original_turn # Restore turn
                        return True
        self.current_turn = original_turn # Restore turn
        return False

    def is_king_in_check(self, color):
        """Checks if the king of the specified color is currently under attack."""
        king_pos = self.find_king(color)
        if not king_pos:
            return False # King not found? Problem.
        opponent_color = 'w' if color == 'b' else 'b'
        return self.is_square_attacked(king_pos[0], king_pos[1], opponent_color)

    def check_game_over(self):
        """Checks if the game has ended (checkmate or stalemate)."""
        possible_moves = self.generate_all_valid_moves(self.current_turn)

        if not possible_moves:
            king_in_check = self.is_king_in_check(self.current_turn)
            if king_in_check:
                self.winner = 'b' if self.current_turn == 'w' else 'w' # Opponent wins
                print(f"Checkmate! {'Black' if self.winner == 'b' else 'White'} wins.")
            else:
                self.winner = 'draw'
                print("Stalemate! It's a draw.")
            self.game_over = True
        else:
            self.game_over = False
            self.winner = None

        # Add other draw conditions later (50-move rule, threefold repetition)

    # --- Keep AI methods ---
    def get_piece_value(self, piece):
        if piece is None: return 0
        return PIECE_VALUES.get(piece[1], 0)

    def evaluate_board(self):
        score = 0
        for r in range(HEIGHT):
            for c in range(WIDTH):
                piece = self.get_piece_at(r, c)
                if piece:
                    value = self.get_piece_value(piece)
                    if piece[0] == 'w': score += value
                    else: score -= value
        # Add positional scoring later if desired
        return score

    def get_ai_move(self):
        """Calls the appropriate AI level function."""
        if self.game_over: return None
        print(f"AI (Level {self.ai_difficulty}, {self.current_turn}) is thinking...") # Added turn color
        if self.ai_difficulty == 0:
            move = self.get_ai_move_level_0()
        elif self.ai_difficulty == 1:
            move = self.get_ai_move_level_1()
        elif self.ai_difficulty == 2:
            move = self.get_ai_move_level_2()
        else:
            move = None
        print("AI finished thinking.")
        return move

    def get_ai_move_level_0(self):
        valid_moves = self.generate_all_valid_moves(self.current_turn)
        if not valid_moves: return None
        return random.choice(valid_moves)

    def get_ai_move_level_1(self):
        valid_moves = self.generate_all_valid_moves(self.current_turn)
        if not valid_moves: return None
        capture_moves = []
        for move in valid_moves:
            target_piece = self.get_piece_at(move[1][0], move[1][1])
            if target_piece is not None:
                capture_value = self.get_piece_value(target_piece)
                capture_moves.append((capture_value, move))
        if capture_moves:
            capture_moves.sort(key=lambda x: x[0], reverse=True)
            best_value = capture_moves[0][0]
            best_captures = [m[1] for m in capture_moves if m[0] == best_value]
            return random.choice(best_captures)
        else:
            return random.choice(valid_moves)

    def get_ai_move_level_2(self):
        depth = 2 # Adjust depth for performance vs strength trade-off
        best_move = None
        is_maximizing = (self.current_turn == 'w') # True if white (AI or not), False if black

        # Adjust initial best_value based on whose turn it is
        if is_maximizing:
            best_value = -math.inf
        else: # Minimizing (Black AI)
            best_value = math.inf

        possible_moves = self.generate_all_valid_moves(self.current_turn)
        if not possible_moves: return None # Should be caught by game over check

        # Shuffle moves to add variety when scores are equal
        random.shuffle(possible_moves)

        for move in possible_moves:
            # Simulate move
            moved_p, captured_p = self.make_move(move[0], move[1])
            if moved_p is None: continue # Should not happen

            # Call minimax for the opponent's turn
            board_value = self.minimax(depth - 1, not is_maximizing) # Flip maximizing player

            # Undo the move
            self.undo_move()

            # Update best move
            if is_maximizing: # White AI trying to maximize
                if board_value > best_value:
                    best_value = board_value
                    best_move = move
            else: # Black AI trying to minimize
                 if board_value < best_value:
                    best_value = board_value
                    best_move = move
            # Note: No random choice on equal needed due to initial shuffle

        # Fallback if no move evaluated (shouldn't happen if possible_moves exist)
        if best_move is None and possible_moves:
             best_move = possible_moves[0]

        return best_move


    def minimax(self, depth, is_maximizing_player):
        if depth == 0 or self.game_over: # Check game_over in recursion too
            # Return large values for checkmate immediately
            if self.game_over:
                if self.winner == 'w': return math.inf # White wins
                elif self.winner == 'b': return -math.inf # Black wins
                else: return 0 # Draw
            return self.evaluate_board()

        current_player_color = 'w' if is_maximizing_player else 'b'
        possible_moves = self.generate_all_valid_moves(current_player_color)

        # If no moves, it's stalemate or checkmate - evaluate the resulting state
        if not possible_moves:
            # Re-check game over state from this simulated position
            # Need to temporarily set turn to evaluate correctly
            original_turn = self.current_turn
            self.current_turn = current_player_color
            self.check_game_over()
            eval_score = 0
            if self.game_over:
                if self.winner == 'w': eval_score = math.inf
                elif self.winner == 'b': eval_score = -math.inf
                else: eval_score = 0
            else: # Should not happen if no moves, but fallback
                eval_score = self.evaluate_board()
            # Reset game over state and turn for the simulation
            self.game_over = False
            self.winner = None
            self.current_turn = original_turn
            return eval_score


        if is_maximizing_player: # White's turn (wants highest score)
            max_eval = -math.inf
            for move in possible_moves:
                moved_p, captured_p = self.make_move(move[0], move[1])
                if moved_p is None: continue
                eval_score = self.minimax(depth - 1, False) # Go to minimizing player
                self.undo_move()
                max_eval = max(max_eval, eval_score)
            return max_eval
        else: # Minimizing player (Black's turn, wants lowest score for White)
            min_eval = math.inf
            for move in possible_moves:
                moved_p, captured_p = self.make_move(move[0], move[1])
                if moved_p is None: continue
                eval_score = self.minimax(depth - 1, True) # Go to maximizing player
                self.undo_move()
                min_eval = min(min_eval, eval_score)
            return min_eval
    # --- End of ChessGame Class ---


# --- Pygame Helper Functions ---

def load_piece_images():
    """Loads images from the 'images' folder."""
    pieces = ['wP', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bP', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for piece in pieces:
        try:
            img_path = f"images/{piece}.png" # Assumes 'images' subfolder
            IMAGES[piece] = pygame.transform.scale(pygame.image.load(img_path), (SQ_SIZE, SQ_SIZE))
        except pygame.error as e:
            print(f"Error loading image: {img_path}")
            print(e)
            sys.exit()
        except FileNotFoundError:
             print(f"Error: Image file not found at {img_path}")
             print("Please ensure you have an 'images' folder with files like wP.png, bK.png, etc.")
             sys.exit()


def draw_board(screen):
    """Draws the squares of the board."""
    for r in range(HEIGHT):
        for c in range(WIDTH):
            color = WHITE if (r + c) % 2 == 0 else BLACK
            pygame.draw.rect(screen, color, pygame.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

def draw_pieces(screen, board):
    """Draws the pieces on the board."""
    for r in range(HEIGHT):
        for c in range(WIDTH):
            piece = board[r][c]
            if piece is not None and piece in IMAGES:
                screen.blit(IMAGES[piece], pygame.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

def draw_highlights(screen, selected_square, valid_moves):
    """Draws highlights for the selected square and its valid moves."""
    if selected_square:
        r, c = selected_square
        # Create a surface for transparent highlighting
        highlight_surface = pygame.Surface((SQ_SIZE, SQ_SIZE), pygame.SRCALPHA)
        highlight_surface.fill(HIGHLIGHT_COLOR)
        screen.blit(highlight_surface, (c * SQ_SIZE, r * SQ_SIZE))

        # Draw valid move indicators (small circles)
        move_indicator_surface = pygame.Surface((SQ_SIZE, SQ_SIZE), pygame.SRCALPHA)
        move_indicator_surface.fill(VALID_MOVE_COLOR)

        for move in valid_moves:
            end_r, end_c = move[1] # Get the end position of the valid move
            screen.blit(move_indicator_surface, (end_c * SQ_SIZE, end_r * SQ_SIZE))
            # Alternative: Draw circles
            # center_x = end_c * SQ_SIZE + SQ_SIZE // 2
            # center_y = end_r * SQ_SIZE + SQ_SIZE // 2
            # pygame.draw.circle(screen, VALID_MOVE_COLOR, (center_x, center_y), SQ_SIZE // 6)


def draw_game_state(screen, game):
    """Draws the board, pieces, and highlights."""
    draw_board(screen)
    # Draw highlights underneath pieces
    # draw_highlights(screen, selected_square, current_valid_moves) # Draw highlights first if desired
    draw_pieces(screen, game.board)
    # Draw highlights on top of pieces (or choose one) - requires selected_square and current_valid_moves passed in
    # draw_highlights(screen, selected_square, current_valid_moves)


def draw_game_over_message(screen, winner):
    """Displays the game over message."""
    font = pygame.font.SysFont('Arial', 48, True, False)
    if winner == 'draw':
        text = "Stalemate! It's a Draw!"
    elif winner == 'w':
        text = "Checkmate! White Wins!"
    elif winner == 'b':
        text = "Checkmate! Black Wins!"
    else:
        return # Should not happen

    text_object = font.render(text, True, pygame.Color('Gray'))
    text_location = pygame.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(
        BOARD_WIDTH / 2 - text_object.get_width() / 2,
        BOARD_HEIGHT / 2 - text_object.get_height() / 2)
    # Add a semi-transparent background box
    bg_surface = pygame.Surface((text_object.get_width() + 20, text_object.get_height() + 20), pygame.SRCALPHA)
    bg_surface.fill((50, 50, 50, 180)) # Dark grey, semi-transparent
    screen.blit(bg_surface, (text_location.x - 10, text_location.y - 10))
    screen.blit(text_object, text_location)


# --- Main Game Loop ---

def main():
    # --- AI Setup ---
    ai_level = None
    while True:
        try:
            choice = input("Play against AI? (y/n): ").strip().lower()
            if choice == 'y':
                level_str = input("Enter AI difficulty (0=Easy, 1=Medium, 2=Harder): ").strip()
                level = int(level_str)
                if level in [0, 1, 2]:
                    ai_level = level
                    print(f"Starting game against AI Level {ai_level}.")
                    break
                else:
                    print("Invalid level. Choose 0, 1, or 2.")
            elif choice == 'n':
                ai_level = None
                print("Starting Player vs Player game.")
                break
            else:
                print("Please enter 'y' or 'n'.")
        except ValueError:
            print("Invalid input. Please enter a number for difficulty.")
        except EOFError:
             print("\nInput stream closed. Exiting.")
             sys.exit()

    # --- Pygame Initialization ---
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Simple Pygame Chess')
    clock = pygame.time.Clock()
    load_piece_images() # Load images into the global IMAGES dict

    # --- Game State Initialization ---
    game = ChessGame(ai_difficulty=ai_level)
    running = True
    selected_square = None  # Store the (row, col) of the selected piece
    player_clicks = []      # Store sequence of clicks: [start_sq, end_sq]
    current_valid_moves = [] # Store valid moves for the selected piece

    # --- Game Loop ---
    while running:
        is_human_turn = (game.ai_difficulty is None or game.current_turn == 'w')

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # --- Mouse Click Handling (Only if Human Turn and Game Not Over) ---
            elif event.type == pygame.MOUSEBUTTONDOWN and is_human_turn and not game.game_over:
                location = pygame.mouse.get_pos()  # (x, y) location of the mouse click
                col = location[0] // SQ_SIZE
                row = location[1] // SQ_SIZE

                clicked_square = (row, col)

                # Ignore clicks outside the board (if screen is larger)
                if not game.is_valid_square(row, col):
                    selected_square = None
                    player_clicks = []
                    current_valid_moves = []
                    continue

                clicked_piece = game.get_piece_at(row, col)

                # --- Click Logic ---
                if selected_square is None: # First click - selecting a piece
                    if clicked_piece is not None and clicked_piece[0] == game.current_turn:
                        selected_square = clicked_square
                        player_clicks.append(selected_square)
                        # Generate and store valid moves for highlighting
                        current_valid_moves = game.generate_all_valid_moves(game.current_turn)
                        # Filter moves starting from the selected square
                        current_valid_moves = [m for m in current_valid_moves if m[0] == selected_square]
                        print(f"Selected {clicked_piece} at {game._coords_to_algebraic(selected_square)}. Valid moves: {[game._coords_to_algebraic(m[1]) for m in current_valid_moves]}") # Debug
                    else:
                         print("Invalid selection: Not your piece or empty square.") # Debug

                else: # Second click - selecting destination or changing selection
                    player_clicks.append(clicked_square)
                    start_pos = player_clicks[0]
                    end_pos = player_clicks[1]

                    # Is the second click a valid move destination?
                    move_tuple = (start_pos, end_pos)

                    # Check if the target square is in the pre-calculated valid moves
                    is_a_valid_target = False
                    for valid_move in current_valid_moves:
                        if valid_move[1] == end_pos:
                             is_a_valid_target = True
                             move_tuple = valid_move # Ensure we use the validated tuple
                             break

                    if is_a_valid_target:
                        print(f"Attempting move: {game._coords_to_algebraic(start_pos)} to {game._coords_to_algebraic(end_pos)}") # Debug
                        # Make the move using the game logic
                        moved_p, captured_p = game.make_move(move_tuple[0], move_tuple[1])
                        if moved_p: # Move was successful
                            print(f"Move successful. Captured: {captured_p}") # Debug
                            selected_square = None # Reset selection
                            player_clicks = []
                            current_valid_moves = []
                            # Turn automatically switched in make_move
                        else:
                            # This case shouldn't happen if is_a_valid_target is true, but safety reset
                            print("Move failed unexpectedly after validation.") # Debug
                            selected_square = None
                            player_clicks = []
                            current_valid_moves = []

                    else: # Second click was not a valid destination
                        print(f"Invalid target square: {game._coords_to_algebraic(end_pos)}") # Debug
                        # Did they click another one of their own pieces? -> Change selection
                        if clicked_piece is not None and clicked_piece[0] == game.current_turn:
                             selected_square = clicked_square
                             player_clicks = [selected_square] # Reset clicks to just the new one
                             # Regenerate valid moves for the new piece
                             current_valid_moves = game.generate_all_valid_moves(game.current_turn)
                             current_valid_moves = [m for m in current_valid_moves if m[0] == selected_square]
                             print(f"Changed selection to {clicked_piece} at {game._coords_to_algebraic(selected_square)}. Valid moves: {[game._coords_to_algebraic(m[1]) for m in current_valid_moves]}") # Debug
                        else: # Clicked empty square or opponent piece invalidly -> Deselect
                            selected_square = None
                            player_clicks = []
                            current_valid_moves = []
                            print("Deselected piece.") # Debug

            # --- Key Press Handling (Optional: e.g., 'u' to undo) ---
            elif event.type == pygame.KEYDOWN:
                 if event.key == pygame.K_u:
                     if game.undo_move():
                         print("Move undone.")
                         # If AI was playing, might need to undo twice to get back to human turn
                         if game.ai_difficulty is not None:
                             game.undo_move()
                             print("Second undo (AI).")
                         selected_square = None # Reset UI state
                         player_clicks = []
                         current_valid_moves = []
                         game.game_over = False # Ensure game over state is reset
                         game.winner = None
                     else:
                         print("Cannot undo.")
                 elif event.key == pygame.K_r: # 'r' to reset game
                      print("Resetting game...")
                      main() # Restart the main function
                      return # Exit the current instance


        # --- AI Turn Logic ---
        if not is_human_turn and not game.game_over:
            ai_move = game.get_ai_move()
            if ai_move:
                print(f"AI chooses move: {game._coords_to_algebraic(ai_move[0])} to {game._coords_to_algebraic(ai_move[1])}")
                moved_p, captured_p = game.make_move(ai_move[0], ai_move[1])
                # AI move done, turn switched in make_move
            else:
                 # Should be handled by check_game_over, but log if AI fails to move
                 print("AI could not find a move (Game should be over?).")
                 game.check_game_over() # Double check


        # --- Drawing ---
        draw_game_state(screen, game) # Draw board and pieces first
        # Draw highlights based on current selection state
        draw_highlights(screen, selected_square, current_valid_moves)

        # Draw game over message if applicable
        if game.game_over:
            draw_game_over_message(screen, game.winner)

        # --- Update Display ---
        pygame.display.flip()
        clock.tick(30)  # Limit frame rate

    pygame.quit()
    sys.exit()

# --- Run the Game ---
if __name__ == "__main__":
    main()