"""Drawing and UI helpers for the game."""
from game import environment
import pygame
import sys

# UI theme colors
BACKGROUND = (20, 27, 42)
BOARD_PANEL = (32, 40, 63)
GRID = (104, 128, 188)
X_COLOR = (245, 105, 65)
O_COLOR = (97, 199, 255)
TEXT = (242, 245, 252)
SUBTEXT = (164, 177, 203)
RESULT_PANEL = (14, 20, 34)


def draw_x(row, col):
    padding = max(16, environment.cell_size // 6)
    x_start = col * environment.cell_size + padding
    y_start = environment.top_margin + row * environment.cell_size + padding
    x_end = (col + 1) * environment.cell_size - padding
    y_end = environment.top_margin + (row + 1) * environment.cell_size - padding
    pygame.draw.line(environment.screen, X_COLOR, (x_start, y_start), (x_end, y_end), 8)
    pygame.draw.line(environment.screen, X_COLOR, (x_start, y_end), (x_end, y_start), 8)


def draw_o(row, col):
    center_x = col * environment.cell_size + environment.cell_size // 2
    center_y = environment.top_margin + row * environment.cell_size + environment.cell_size // 2
    radius = environment.cell_size // 2 - max(16, environment.cell_size // 6)
    pygame.draw.circle(environment.screen, O_COLOR, (center_x, center_y), radius, 8)


def draw_board(status_text=None, mode_text=None):
    environment.screen.fill(BACKGROUND)

    # Top information banner
    banner_rect = pygame.Rect(0, 0, environment.screen_width, environment.top_margin)
    pygame.draw.rect(environment.screen, BOARD_PANEL, banner_rect)
    pygame.draw.line(environment.screen, GRID, (0, environment.top_margin), (environment.screen_width, environment.top_margin), 1)

    title_font = pygame.font.Font(None, 42)
    small_font = pygame.font.Font(None, 28)

    title_surface = title_font.render("TicTacToe Pro", True, TEXT)
    environment.screen.blit(title_surface, (20, 12))

    if status_text:
        status_surface = small_font.render(status_text, True, TEXT)
        environment.screen.blit(status_surface, (20, 56))

    if mode_text:
        mode_surface = small_font.render(mode_text, True, SUBTEXT)
        environment.screen.blit(mode_surface, (environment.screen_width - mode_surface.get_width() - 24, 40))

    # Grid background panel
    board_rect = pygame.Rect(0, environment.top_margin, environment.board_width, environment.board_width)
    pygame.draw.rect(environment.screen, BOARD_PANEL, board_rect)
    pygame.draw.rect(environment.screen, GRID, board_rect, 4, border_radius=18)

    # Draw grid lines
    for row in range(1, environment.board_size):
        y = environment.top_margin + row * environment.cell_size
        pygame.draw.line(environment.screen, GRID, (24, y), (environment.board_width - 24, y), 4)
        x = row * environment.cell_size
        pygame.draw.line(environment.screen, GRID, (x, environment.top_margin + 24), (x, environment.top_margin + environment.board_width - 24), 4)

    # Render pieces
    for row in range(environment.board_size):
        for col in range(environment.board_size):
            cell = environment.Main_board.loc[environment.row_labels[row]][str(col + 1)]
            if cell == "X":
                draw_x(row, col)
            elif cell == "O":
                draw_o(row, col)

    # Footer panel with instructions
    footer_text = "Click a cell to make your move. Press ESC to quit."
    footer_surface = small_font.render(footer_text, True, SUBTEXT)
    environment.screen.blit(footer_surface, (20, environment.screen_height - 36))


def get_cell(x, y):
    if y < environment.top_margin or x < 0 or x > environment.board_width:
        return None, None
    row = (y - environment.top_margin) // environment.cell_size
    col = x // environment.cell_size
    return row, col


def show_game_result(result_message, user_points, agent_points, final_board):
    pygame.init()
    board_size = len(final_board)
    cell_size = min(52, max(36, 520 // board_size))
    board_size_pixels = board_size * cell_size
    screen_width = max(520, board_size_pixels + 160)
    screen_height = max(500, board_size_pixels + 240)
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Game Over")
    font = pygame.font.Font(None, 56)
    small_font = pygame.font.Font(None, 32)
    tiny_font = pygame.font.Font(None, 22)
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                running = False

        screen.fill(BACKGROUND)
        panel = pygame.Rect(40, 40, screen_width - 80, screen_height - 80)
        pygame.draw.rect(screen, RESULT_PANEL, panel, border_radius=24)
        pygame.draw.rect(screen, GRID, panel, 3, border_radius=24)

        title_surface = font.render(result_message, True, TEXT)
        screen.blit(title_surface, (screen_width // 2 - title_surface.get_width() // 2, 64))

        score_surface = small_font.render(f"You: {user_points}    Agent: {agent_points}", True, SUBTEXT)
        screen.blit(score_surface, (screen_width // 2 - score_surface.get_width() // 2, 140))

        final_label = small_font.render("Final board state", True, TEXT)
        screen.blit(final_label, (72, 210))

        board_start_x = 72
        board_start_y = 260
        board_panel = pygame.Rect(board_start_x - 12, board_start_y - 12, board_size_pixels + 24, board_size_pixels + 24)
        pygame.draw.rect(screen, BOARD_PANEL, board_panel, border_radius=18)
        pygame.draw.rect(screen, GRID, board_panel, 2, border_radius=18)

        for row in range(board_size + 1):
            y = board_start_y + row * cell_size
            pygame.draw.line(screen, GRID, (board_start_x, y), (board_start_x + board_size_pixels, y), 2)
            x = board_start_x + row * cell_size
            pygame.draw.line(screen, GRID, (x, board_start_y), (x, board_start_y + board_size_pixels), 2)

        for row in range(board_size):
            for col in range(board_size):
                cell_value = final_board.loc[environment.row_labels[row]][str(col + 1)]
                if cell_value == "X":
                    start = (board_start_x + col * cell_size + 12, board_start_y + row * cell_size + 12)
                    end = (board_start_x + (col + 1) * cell_size - 12, board_start_y + (row + 1) * cell_size - 12)
                    pygame.draw.line(screen, X_COLOR, start, end, 6)
                    pygame.draw.line(screen, X_COLOR, (start[0], end[1]), (end[0], start[1]), 6)
                elif cell_value == "O":
                    center = (board_start_x + col * cell_size + cell_size // 2, board_start_y + row * cell_size + cell_size // 2)
                    radius = cell_size // 2 - 12
                    pygame.draw.circle(screen, O_COLOR, center, radius, 6)

        footer_text = "Press any key or close window to finish."
        footer_surface = tiny_font.render(footer_text, True, SUBTEXT)
        screen.blit(footer_surface, (screen_width // 2 - footer_surface.get_width() // 2, screen_height - 45))

        pygame.display.flip()

    pygame.quit()
