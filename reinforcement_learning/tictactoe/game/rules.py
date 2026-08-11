"""Game rules, scoring and terminal-state checks."""
import numpy as np
from game import environment

# Points trackers
agent_points = 0
user_points = 0
live_agent_points = 0
live_user_points = 0


def user_counter(arr):
    user_points_local = 0
    user_points_counter = 0
    for i in arr:
        if i == environment.USER_MARKER:
            user_points_counter += 1
        else:
            if user_points_counter >= 3:
                user_points_local += user_points_counter
            user_points_counter = 0
    if user_points_counter >= 3:
        user_points_local += user_points_counter
    return user_points_local


def agent_counter(arr):
    agent_points_local = 0
    agent_points_counter = 0
    for i in arr:
        if i == environment.AGENT_MARKER:
            agent_points_counter += 1
        else:
            if agent_points_counter >= 3:
                agent_points_local += agent_points_counter
            agent_points_counter = 0
    if agent_points_counter >= 3:
        agent_points_local += agent_points_counter
    return agent_points_local


def count_points(count_agent_points, count_user_points):
    global agent_points, user_points
    if count_agent_points > 2:
        agent_points += ((2 * count_agent_points) - 5)
    if count_user_points > 2:
        user_points += ((2 * count_user_points) - 5)


def live_count_points(live_count_agent_points, live_count_user_points):
    global live_agent_points, live_user_points
    if live_count_agent_points > 2:
        live_agent_points += ((2 * live_count_agent_points) - 5)
    if live_count_user_points > 2:
        live_user_points += ((2 * live_count_user_points) - 5)


def check_win_rows(board, jump):
    numpy_board = board.to_numpy()
    for i in range(environment.board_size):
        row = numpy_board[i, :]
        count_user_points = user_counter(row)
        count_agent_points = agent_counter(row)
        if jump:
            count_points(count_agent_points, count_user_points)
        else:
            live_count_points(count_agent_points, count_user_points)


def check_win_diameter(board, jump):
    numpy_board = board.to_numpy()
    diameter = np.diagonal(numpy_board, offset=0)
    count_agent_points = agent_counter(diameter)
    count_user_points = user_counter(diameter)
    if jump:
        count_points(count_agent_points, count_user_points)
    else:
        live_count_points(count_agent_points, count_user_points)


def check_win_columns(board, jump):
    numpy_board = board.to_numpy()
    for i in range(environment.board_size):
        column = numpy_board[:, i]
        count_agent_points = agent_counter(column)
        count_user_points = user_counter(column)
        if jump:
            count_points(count_agent_points, count_user_points)
        else:
            live_count_points(count_agent_points, count_user_points)


def check_win_subdiameter(board, jump):
    numpy_board = board.to_numpy()
    flipped_board = np.fliplr(numpy_board)
    subdiameter = np.diagonal(flipped_board, offset=0)
    count_agent_points = agent_counter(subdiameter)
    count_user_points = user_counter(subdiameter)
    if jump:
        count_points(count_agent_points, count_user_points)
    else:
        live_count_points(count_agent_points, count_user_points)


def check_parallel_diameters(board, jump):
    numpy_board = board.to_numpy()
    for i in range(1, environment.board_size - 2):
        upparallel = np.diagonal(numpy_board, offset=i)
        up_agent = agent_counter(upparallel)
        up_user = user_counter(upparallel)
        belowparallel = np.diagonal(numpy_board, offset=-i)
        below_agent = agent_counter(belowparallel)
        below_user = user_counter(belowparallel)
        if jump:
            count_points(up_agent, up_user)
            count_points(below_agent, below_user)
        else:
            live_count_points(up_agent, up_user)
            live_count_points(below_agent, below_user)


def check_parallel_subdiameters(board, jump):
    numpy_board = board.to_numpy()
    flipped_board = np.fliplr(numpy_board)
    for i in range(1, environment.board_size - 2):
        upsubparallel = np.diagonal(flipped_board, offset=i)
        upsub_agent = agent_counter(upsubparallel)
        upsub_user = user_counter(upsubparallel)
        belowsubparallel = np.diagonal(flipped_board, offset=-i)
        belowsub_agent = agent_counter(belowsubparallel)
        belowsub_user = user_counter(belowsubparallel)
        if jump:
            count_points(upsub_agent, upsub_user)
            count_points(belowsub_agent, belowsub_user)
        else:
            live_count_points(upsub_agent, upsub_user)
            live_count_points(belowsub_agent, belowsub_user)


def score(board):
    global live_agent_points, live_user_points
    live_user_points = 0
    live_agent_points = 0
    check_win_columns(board, False)
    check_win_diameter(board, False)
    check_win_subdiameter(board, False)
    check_win_rows(board, False)
    check_parallel_diameters(board, False)
    check_parallel_subdiameters(board, False)
    if live_user_points > live_agent_points:
        return -1
    elif live_agent_points > live_user_points:
        return 1
    else:
        return 0


def check_game_over(board):
    full_places = 0
    for i in range(environment.board_size):
        row = environment.row_labels[i]
        for j in range(1, environment.board_size + 1):
            if board.loc[row, str(j)] != "_":
                full_places += 1
    if full_places == environment.board_size * environment.board_size:
        return 1


def possible_moves(board):
    possible_moves_list = []
    for i in range(environment.board_size):
        row = environment.row_labels[i]
        for j in range(1, environment.board_size + 1):
            if board.loc[row, str(j)] == "_":
                move = [row, str(j)]
                possible_moves_list.append(move)
    return possible_moves_list


def check_winner():
    global agent_points, user_points
    check_win_rows(environment.Main_board, True)
    check_win_columns(environment.Main_board, True)
    check_win_diameter(environment.Main_board, True)
    check_win_subdiameter(environment.Main_board, True)
    check_parallel_diameters(environment.Main_board, True)
    check_parallel_subdiameters(environment.Main_board, True)
    if user_points > agent_points:
        return "User"
    elif user_points < agent_points:
        return "Agent"
    else:
        return "Draw"
