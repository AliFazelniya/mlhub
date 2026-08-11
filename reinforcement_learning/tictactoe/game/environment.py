# Environment and initialization for the game
import pandas
import numpy as np
import pygame

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Markers and board state
USER_MARKER = "X"
AGENT_MARKER = "O"
board_size = 3
cell_size = 100
top_margin = 80
board_width = board_size * cell_size
screen_width = board_width
screen_height = board_width + top_margin
screen = None
font = None
Main_board = None
row_labels = []
col_labels = []


def init_game(selected_board_size: int = 3):
    global board_size, cell_size, board_width, screen_width, screen_height, screen, font, row_labels, col_labels, Main_board

    board_size = selected_board_size
    row_labels = [chr(97 + i) for i in range(board_size)]
    col_labels = [str(i + 1) for i in range(board_size)]
    Main_board = pandas.DataFrame(
        [["_"] * board_size for _ in range(board_size)],
        index=row_labels,
        columns=col_labels,
    )

    pygame.init()
    cell_size = 60 if board_size > 6 else 100
    board_width = board_size * cell_size
    screen_width = board_width
    screen_height = board_width + top_margin
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Tic Tac Toe")
    font = pygame.font.Font(None, 40)
