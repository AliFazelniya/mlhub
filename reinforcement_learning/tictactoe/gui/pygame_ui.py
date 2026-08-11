"""User interface helpers for the TicTacToe game."""
import sys
import pygame
from game import environment
from game import board as board_ui

# UI theme colors
BACKGROUND = (18, 25, 38)
PANEL = (34, 45, 63)
PANEL_LIGHT = (44, 57, 78)
PRIMARY = (64, 196, 255)
SECONDARY = (253, 187, 45)
HIGHLIGHT = (130, 158, 199)
TEXT = (236, 240, 245)
MUTED = (169, 179, 196)
ERROR = (235, 77, 75)


def _draw_shadow_rect(screen, rect, radius=18, offset=(0, 6)):
    shadow_surface = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    pygame.draw.rect(shadow_surface, (0, 0, 0, 40), shadow_surface.get_rect(), border_radius=radius)
    screen.blit(shadow_surface, (rect.x + offset[0], rect.y + offset[1]))


def _draw_button(screen, rect, text, selected, font, active=False):
    background_color = PRIMARY if selected else PANEL_LIGHT if active else PANEL
    border_color = SECONDARY if selected else HIGHLIGHT
    text_color = TEXT if selected or active else MUTED
    _draw_shadow_rect(screen, rect, radius=16, offset=(0, 5))
    pygame.draw.rect(screen, background_color, rect, border_radius=16)
    pygame.draw.rect(screen, border_color, rect, 2, border_radius=16)
    text_surface = font.render(text, True, text_color)
    text_rect = text_surface.get_rect(center=rect.center)
    screen.blit(text_surface, text_rect)


def _draw_chip(screen, rect, label, selected, font):
    background_color = PRIMARY if selected else PANEL_LIGHT
    text_color = BACKGROUND if selected else TEXT
    pygame.draw.rect(screen, background_color, rect, border_radius=14)
    pygame.draw.rect(screen, HIGHLIGHT, rect, 2, border_radius=14)
    text_surface = font.render(label, True, text_color)
    text_rect = text_surface.get_rect(center=rect.center)
    screen.blit(text_surface, text_rect)


def settings_menu():
    pygame.init()
    screen = pygame.display.set_mode((820, 680))
    pygame.display.set_caption("TicTacToe Pro — Settings")
    title_font = pygame.font.Font(None, 72)
    section_font = pygame.font.Font(None, 34)
    option_font = pygame.font.Font(None, 30)
    input_font = pygame.font.Font(None, 36)
    hint_font = pygame.font.Font(None, 24)

    board_size_text = "3"
    selected_marker = "X"
    selected_mode = "Minimax"
    active_input = False
    error_message = ""

    input_box = pygame.Rect(88, 236, 180, 56)
    marker_x_button = pygame.Rect(340, 226, 180, 56)
    marker_o_button = pygame.Rect(540, 226, 180, 56)
    mode_minimax_button = pygame.Rect(340, 322, 180, 56)
    mode_random_button = pygame.Rect(540, 322, 180, 56)
    start_button = pygame.Rect(260, 520, 300, 68)

    while True:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active_input = True
                else:
                    active_input = False

                if marker_x_button.collidepoint(event.pos):
                    selected_marker = "X"
                elif marker_o_button.collidepoint(event.pos):
                    selected_marker = "O"
                elif mode_minimax_button.collidepoint(event.pos):
                    selected_mode = "Minimax"
                elif mode_random_button.collidepoint(event.pos):
                    selected_mode = "Random"
                elif start_button.collidepoint(event.pos):
                    if board_size_text.isdigit() and 3 <= int(board_size_text) <= 10:
                        return int(board_size_text), selected_marker, selected_mode.lower()
                    error_message = "Board size must be a number between 3 and 10."

            if event.type == pygame.KEYDOWN and active_input:
                if event.key == pygame.K_RETURN:
                    active_input = False
                elif event.key == pygame.K_BACKSPACE:
                    board_size_text = board_size_text[:-1]
                elif event.unicode.isdigit() and len(board_size_text) < 2:
                    board_size_text += event.unicode

        screen.fill(BACKGROUND)

        card_rect = pygame.Rect(40, 44, 740, 592)
        _draw_shadow_rect(screen, card_rect, radius=24, offset=(0, 10))
        pygame.draw.rect(screen, PANEL, card_rect, border_radius=24)

        title_surface = title_font.render("TicTacToe Pro", True, TEXT)
        screen.blit(title_surface, (72, 72))

        subtitle = "Choose your player and agent settings before you begin."
        subtitle_surface = option_font.render(subtitle, True, MUTED)
        screen.blit(subtitle_surface, (72, 150))

        section_label = section_font.render("Game Setup", True, TEXT)
        screen.blit(section_label, (88, 206))

        pygame.draw.rect(screen, PANEL_LIGHT, input_box, border_radius=16)
        pygame.draw.rect(screen, PRIMARY if active_input else HIGHLIGHT, input_box, 2, border_radius=16)
        size_label = option_font.render("Board size (3-10)", True, MUTED)
        screen.blit(size_label, (88, 208))
        input_text = input_font.render(board_size_text, True, TEXT)
        screen.blit(input_text, (input_box.x + 18, input_box.y + 12))

        marker_prompt = option_font.render("Your marker", True, TEXT)
        screen.blit(marker_prompt, (340, 186))
        _draw_chip(screen, marker_x_button, "Play as X", selected_marker == "X", option_font)
        _draw_chip(screen, marker_o_button, "Play as O", selected_marker == "O", option_font)

        mode_prompt = option_font.render("Agent difficulty", True, TEXT)
        screen.blit(mode_prompt, (340, 282))
        _draw_chip(screen, mode_minimax_button, "Minimax", selected_mode == "Minimax", option_font)
        _draw_chip(screen, mode_random_button, "Random", selected_mode == "Random", option_font)

        start_text = "Start Game"
        hovered = start_button.collidepoint(mouse_pos)
        _draw_button(screen, start_button, start_text, hovered, option_font, active=hovered)

        if error_message:
            error_surface = hint_font.render(error_message, True, ERROR)
            screen.blit(error_surface, (88, 430))

        hint_surface = hint_font.render("Professional game interface with polished visuals and simple controls.", True, MUTED)
        screen.blit(hint_surface, (88, 570))

        pygame.display.flip()


def draw():
    board_ui.draw_board()


def get_cell(x, y):
    return board_ui.get_cell(x, y)
