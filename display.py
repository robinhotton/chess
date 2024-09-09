import pygame
from game_controller import GameController

class Display:
    def __init__(self):
        self._screen_width = 750
        self._screen_height = 750  # Increase height to make room for the label
        self._board_size = 8
        self._square_size = self._screen_width // self._board_size

        self._game_controller = GameController()

        pygame.init()
        self._screen = pygame.display.set_mode((self._screen_width, self._screen_height))
        self._clock = pygame.time.Clock()
        pygame.display.set_caption("Chess")
        self._load_images()

        # Initialize font
        pygame.font.init()
        self._font = pygame.font.SysFont('Arial', 24)

    def _load_images(self):
        self._images = {}
        for row in self._game_controller.board.board:
            for piece in row:
                if piece is not None:
                    if piece.image_file not in self._images:
                        image = pygame.image.load(piece.image_file)
                        image = pygame.transform.scale(image, (self._square_size, self._square_size))
                        self._images[piece.image_file] = image

    def run_game(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    row = y // self._square_size
                    col = x // self._square_size
                    self._game_controller.handle_click((row, col))

            self._screen.fill(pygame.Color('white'))
            self._draw_board()
            self._draw_pieces()
            self._draw_turn_label()
            if self._game_controller.game_over:
                self._draw_game_over_message()
            pygame.display.flip()
            self._clock.tick(60)

        pygame.quit()

    def _draw_board(self):
        colors = [pygame.Color('white'), pygame.Color('gray')]
        for row in range(self._board_size):
            for col in range(self._board_size):
                color = colors[(row + col) % 2]
                pygame.draw.rect(self._screen, color, pygame.Rect(col * self._square_size, row * self._square_size, self._square_size, self._square_size))

        self._highlight_selected_piece()
        self._highlight_legal_moves()
        self._highlight_king_in_check()

    def _highlight_selected_piece(self):
        piece = self._game_controller.selected_piece
        if piece is not None:
            row, col = piece.position
            pygame.draw.rect(self._screen, pygame.Color('yellow'), pygame.Rect(col * self._square_size, row * self._square_size, self._square_size, self._square_size), 3)

    def _highlight_legal_moves(self):
        piece = self._game_controller.selected_piece
        if piece is not None:
            original_position = piece.position
            legal_moves = piece.get_legal_moves(self._game_controller.board.board)
            for move in legal_moves:
                self._game_controller.board.move_piece(piece, move)
                if not self._game_controller.is_in_check(piece.color):
                    row, col = move
                    center_x = col * self._square_size + self._square_size // 2
                    center_y = row * self._square_size + self._square_size // 2
                    pygame.draw.circle(self._screen, pygame.Color('blue'), (center_x, center_y), 5)
                self._game_controller.board.move_piece(piece, original_position)

    def _highlight_king_in_check(self):
        for color in ['white', 'black']:
            if self._game_controller.is_in_check(color):
                king_position = self._game_controller.board.find_king(color)
                if king_position:
                    x, y = king_position[1] * self._square_size, king_position[0] * self._square_size
                    pygame.draw.rect(self._screen, pygame.Color('red'), pygame.Rect(x, y, self._square_size, self._square_size), 3)

    def _draw_pieces(self):
        for row in range(self._board_size):
            for col in range(self._board_size):
                piece = self._game_controller.board.board[row][col]
                if piece is not None:
                    image = self._images[piece.image_file]
                    image_rect = image.get_rect()
                    image_rect.center = (col * self._square_size + self._square_size // 2, row * self._square_size + self._square_size // 2)
                    self._screen.blit(image, image_rect)

    def _draw_turn_label(self):
        turn_text = f"Turn: {self._game_controller.current_turn.capitalize()}"
        label = self._font.render(turn_text, True, pygame.Color('black'))
        self._screen.blit(label, (10, self._screen_width + 10))  # Position label below the board

    def _draw_game_over_message(self):
        game_over_text = f"Checkmate! {self._game_controller.current_turn.capitalize()} wins!"
        label = self._font.render(game_over_text, True, pygame.Color('red'))
        rect = label.get_rect(center=(self._screen_width // 2, self._screen_height - 20))
        self._screen.blit(label, rect)

if __name__ == "__main__":
    Display().run_game()
