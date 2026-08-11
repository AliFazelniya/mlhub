"""A simple random agent placeholder."""
import random


def choose_move(board, possible_moves):
    if not possible_moves:
        return None
    return random.choice(possible_moves)
