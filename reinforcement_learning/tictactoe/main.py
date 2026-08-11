"""Refactored entry point for the TicTacToe game."""
import pygame
import sys
import time

from game import environment, board as board_ui, rules
from gui.pygame_ui import settings_menu
from agents import minimax_agent, random_agent


def main():
    board_size, user_choice, agent_mode = settings_menu()
    environment.USER_MARKER = user_choice
    environment.AGENT_MARKER = "O" if user_choice == "X" else "X"
    rules.user_points = 0
    rules.agent_points = 0
    rules.live_user_points = 0
    rules.live_agent_points = 0
    environment.init_game(board_size)

    current_player = environment.USER_MARKER if environment.USER_MARKER == "X" else environment.AGENT_MARKER
    running = True

    while running:
        status_text = "Your turn" if current_player == environment.USER_MARKER else "Computer is thinking..."
        mode_text = f"Mode: {agent_mode.title()} | You: {environment.USER_MARKER} | Agent: {environment.AGENT_MARKER}"
        board_ui.draw_board(status_text, mode_text)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and current_player == environment.USER_MARKER:
                x, y = event.pos
                row, col = board_ui.get_cell(x, y)
                if row is None or col is None:
                    continue
                if 0 <= row < environment.board_size and 0 <= col < environment.board_size:
                    if environment.Main_board.loc[environment.row_labels[row], str(col + 1)] == "_":
                        environment.Main_board.loc[environment.row_labels[row], str(col + 1)] = environment.USER_MARKER
                        current_player = environment.AGENT_MARKER

        if current_player == environment.AGENT_MARKER and rules.check_game_over(environment.Main_board) != 1:
            if agent_mode == "minimax":
                minimax_agent.com_choice(environment.Main_board)
            else:
                random_agent.com_choice(environment.Main_board)
            current_player = environment.USER_MARKER

        if rules.check_game_over(environment.Main_board) == 1:
            running = False

        board_ui.draw_board(status_text, mode_text)
        pygame.display.flip()
        time.sleep(0.05)

    winner = rules.check_winner()
    if winner == "Draw":
        result_message = "Draw!"
    else:
        result_message = "You won!" if winner == "User" else "Computer won!"
    board_ui.show_game_result(result_message, rules.user_points, rules.agent_points, environment.Main_board)


if __name__ == '__main__':
    main()
