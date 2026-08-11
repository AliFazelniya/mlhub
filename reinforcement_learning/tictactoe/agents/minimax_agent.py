"""Minimax agent implementation."""
from copy import deepcopy
from game import rules, environment


def Minimax(board, depth, maximizing_player, alpha=float('-inf'), beta=float('inf')):
    if rules.check_game_over(board) or depth == 0:
        return rules.score(board), None

    if maximizing_player:
        best_value = float('-inf')
        best_move = None
        board_copy = deepcopy(board)
        for move in rules.possible_moves(board):
            board_copy.loc[move[0], move[1]] = environment.AGENT_MARKER
            value, _ = Minimax(board_copy, depth - 1, False, alpha, beta)
            board_copy.loc[move[0], move[1]] = "_"
            if value > best_value:
                best_value = value
                best_move = move
            alpha = max(alpha, value)
            if beta <= alpha:
                break
        return best_value, best_move
    else:
        best_value = float('inf')
        best_move = None
        board_copy = deepcopy(board)
        for move in rules.possible_moves(board):
            board_copy.loc[move[0], move[1]] = environment.USER_MARKER
            value, _ = Minimax(board_copy, depth - 1, True, alpha, beta)
            board_copy.loc[move[0], move[1]] = "_"
            if value < best_value:
                best_value = value
                best_move = move
            beta = min(beta, value)
            if beta <= alpha:
                break
        return best_value, best_move


def com_choice(board):
    board_copy = board.copy()
    _, best_move = Minimax(board_copy, environment.board_size + 3, True)
    if best_move:
        board.loc[best_move[0], best_move[1]] = environment.AGENT_MARKER
    else:
        print("No possible moves for agent!")
