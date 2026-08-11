"""A simple random agent implementation."""
import random
from game import environment, rules


def choose_move(possible_moves):
    if not possible_moves:
        return None
    return random.choice(possible_moves)


def com_choice(board):
    possible_moves = rules.possible_moves(board)
    best_move = choose_move(possible_moves)
    if best_move:
        board.loc[best_move[0], best_move[1]] = environment.AGENT_MARKER
    else:
        print("No possible moves for random agent!")
