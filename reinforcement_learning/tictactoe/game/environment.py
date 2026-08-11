# Environment and initialization for the game
import pandas
import numpy as np
import pygame
import sys

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)


def get_board_size():
    pygame.init()
    screen = pygame.display.set_mode((400, 200))
    pygame.display.set_caption("Board Size")
    font = pygame.font.Font(None, 40)
    fonta = pygame.font.Font(None, 25)
    input_box = pygame.Rect(100, 80, 200, 40)
    color_inactive = pygame.Color('black')
    color_active = pygame.Color('blue')
    color = color_inactive
    active = False
    text = ""
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = not active
                else:
                    active = False
                color = color_active if active else color_inactive
            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        if text.isdigit() and int(text) > 2 and int(text) <= 10:
                            board_size = int(text)
                            running = False
                        else:
                            text = ""
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode
        screen.fill((WHITE))
        pygame.draw.rect(screen, color, input_box, 2, border_radius=10)
        text_surface = font.render(text, True, pygame.Color('black'))
        screen.blit(text_surface, (input_box.x + 90, input_box.y + 7))
        input_box.w = max(200, text_surface.get_width() + 10)
        message_surface = font.render("Enter board size", True, pygame.Color('black'))
        screen.blit(message_surface, (80, 30))
        message = fonta.render("Note: Board size must be between 3 to 10!", True, pygame.Color('black'))
        screen.blit(message, (35, 150))
        pygame.display.flip()
    pygame.quit()
    return board_size


# Acquire board size at import (keeps behavior consistent with original script)
board_size = get_board_size()

# Build main board DataFrame
board = []
for _ in range(board_size):
    board.append(["_"] * board_size)

row_labels = [chr(97 + i) for i in range(board_size)]
col_labels = [str(i + 1) for i in range(board_size)]
Main_board = pandas.DataFrame(board, index=row_labels, columns=col_labels)

# GUI initialisation
pygame.init()
if board_size > 6:
    cell_size = 60
else:
    cell_size = 100
screen_size = board_size * cell_size
screen = pygame.display.set_mode((screen_size, screen_size))
pygame.display.set_caption("Neicharan's Dooz")
font = pygame.font.Font(None, 60)
