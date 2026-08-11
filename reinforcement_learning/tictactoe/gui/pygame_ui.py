"""Simple GUI glue (exports draw/update)."""
from project.game import board


def draw():
    board.draw_board()


def get_cell(x, y):
    return board.get_cell(x, y)
