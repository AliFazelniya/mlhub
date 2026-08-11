"""Refactored entry point for the TicTacToe game."""
import pygame
import sys
import time

from game import environment, board as board_ui, rules
from agents import minimax_agent


# Current player
current_player = "X"


def main():
    global current_player
    running = True
    while running:
        board_ui.draw_board()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and current_player == "X":
                x, y = event.pos
                row, col = board_ui.get_cell(x, y)
                if environment.Main_board.loc[environment.row_labels[row], str(col+1)] == "_":
                    environment.Main_board.loc[environment.row_labels[row], str(col+1)] = current_player
                    current_player = "O"
                    board_ui.draw_board()
                    pygame.display.flip()

        if rules.check_game_over(environment.Main_board) != 1:
            if current_player == "O":
                minimax_agent.com_choice(environment.Main_board)
                current_player = "X"
        else:
            time.sleep(1)
            running = False

        board_ui.draw_board()
        pygame.display.flip()

    winner = rules.check_winner()
    result_message = "Draw!" if winner == "Draw" else f"{'You' if winner == 'User' else 'Agent'} Won!"
    board_ui.show_game_result(result_message, rules.user_points, rules.agent_points, environment.Main_board)


if __name__ == '__main__':
    main()
