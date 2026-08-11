"""Drawing and UI helpers for the game."""
from game import environment
import pygame
import sys


WHITE = environment.WHITE
BLACK = environment.BLACK
RED = environment.RED
BLUE = environment.BLUE


def draw_x(row, col):
    padding = 20
    x_start = col * environment.cell_size + padding
    y_start = row * environment.cell_size + padding
    x_end = (col + 1) * environment.cell_size - padding
    y_end = (row + 1) * environment.cell_size - padding
    pygame.draw.line(environment.screen, RED, (x_start, y_start), (x_end, y_end), 4)
    pygame.draw.line(environment.screen, RED, (x_start, y_end), (x_end, y_start), 4)


def draw_o(row, col):
    center_x = col * environment.cell_size + environment.cell_size // 2
    center_y = row * environment.cell_size + environment.cell_size // 2
    radius = environment.cell_size // 2 - 20
    pygame.draw.circle(environment.screen, BLUE, (center_x, center_y), radius, 4)


def draw_board():
    environment.screen.fill(WHITE)
    for row in range(environment.board_size):
        pygame.draw.line(environment.screen, BLACK, (0, row * environment.cell_size), (environment.screen_size, row * environment.cell_size), 2)
        pygame.draw.line(environment.screen, BLACK, (row * environment.cell_size, 0), (row * environment.cell_size, environment.screen_size), 2)

    for row in range(environment.board_size):
        for col in range(environment.board_size):
            cell = environment.Main_board.loc[environment.row_labels[row]][str(col+1)]
            if cell == "X":
                draw_x(row, col)
            elif cell == "O":
                draw_o(row, col)


def get_cell(x, y):
    row = y // environment.cell_size
    col = x // environment.cell_size
    return row, col


def show_game_result(result_message, user_points, agent_points, final_board):
    pygame.init()
    board_size = len(final_board)
    cell_size = 50
    screen_width = 400 + board_size * cell_size
    screen_height = max(250, board_size * cell_size) + 50
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Game Over")
    font = pygame.font.Font(None, 60)
    small_font = pygame.font.Font(None, 40)
    tiny_font = pygame.font.Font(None, 30)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                running = False
        screen.fill(WHITE)
        result_text = font.render(result_message, True, pygame.Color('black'))
        screen.blit(result_text, (20, 20))
        user_score_text = small_font.render(f"Your Points: {user_points}", True, pygame.Color('blue'))
        agent_score_text = small_font.render(f"Computer Points: {agent_points}", True, pygame.Color('red'))
        screen.blit(user_score_text, (20, 100))
        screen.blit(agent_score_text, (20, 150))
        sub_text_surface = tiny_font.render("Press any key to exit", True, pygame.Color('black'))
        screen.blit(sub_text_surface, (20, screen_height - 40))
        board_start_x = 350
        board_start_y = 50
        for row in range(board_size):
            for col in range(board_size):
                cell_x = board_start_x + col * cell_size
                cell_y = board_start_y + row * cell_size
                pygame.draw.rect(screen, BLACK, (cell_x, cell_y, cell_size, cell_size), 2)
                if final_board.loc[environment.row_labels[row]][str(col+1)] == "X":
                    pygame.draw.line(screen, BLUE, (cell_x + 10, cell_y + 10), (cell_x + cell_size - 10, cell_y + cell_size - 10), 3)
                    pygame.draw.line(screen, BLUE, (cell_x + 10, cell_y + cell_size - 10), (cell_x + cell_size - 10, cell_y + 10), 3)
                elif final_board.loc[environment.row_labels[row]][str(col+1)] == "O":
                    pygame.draw.circle(screen, RED, (cell_x + cell_size // 2, cell_y + cell_size // 2), cell_size // 3, 3)
        pygame.display.flip()
    pygame.quit()
