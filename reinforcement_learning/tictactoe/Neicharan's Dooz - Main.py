# Ali Fazelniya ID: 4011833230
# Neicharan's Dooz with Minimax algorithm
# user is X and agent is O

# Import section: import pandas, numpy, deepcopy, pygame, sys, time, os
import pandas
import numpy as np  
from copy import deepcopy
import pygame
import sys
import time
import os 

# Defince colors for using in GUI with RGB code.
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Function for getting board size window:
def get_board_size():
    # Start Pygame
    pygame.init()
    # create a screen in 400 x 200 pixle size.
    screen = pygame.display.set_mode((400, 200))
    # Name the window "Board Size".
    pygame.display.set_caption("Board Size")
    # Set a font with 40 size for enter text.
    font = pygame.font.Font(None, 40) 
    # Set a font with 25 size for note text.
    fonta = pygame.font.Font(None, 25)
    # Creat a entry box in 200 x 40 pixle in (100,80) coordinate of window.
    input_box = pygame.Rect(100, 80, 200, 40) 
    # Set default balck color for entry box when user hasn't click in it yet. 
    color_inactive = pygame.Color('black')  
    # Set blue color for entry box when user click in it.
    color_active = pygame.Color('blue') 
    # Set first color of entry box with black/
    color = color_inactive
    # when user hasn't clicked in box active = False.
    active = False
    # user enter is empty first the text = ""
    text = ""
    # Program runs while running = True.
    running = True
    # program loop:
    while running:
        # check all click, entry , etc in window.
        for event in pygame.event.get():
            # If user click exit buttom then program exit.
            if event.type == pygame.QUIT: 
                pygame.quit()
                sys.exit()
            # Check  if user click on sth or not.
            if event.type == pygame.MOUSEBUTTONDOWN:
                # if user click on entry box then:
                if input_box.collidepoint(event.pos):
                    # active = True
                    active = not active
                else:
                    # else then active = False.
                    active = False
                # if user has clicked on it the it's color will be blue. 
                color = color_active if active else color_inactive
            # check if user enter a keybord key or not:
            if event.type == pygame.KEYDOWN:
                # if user entered sth and user has clicked on bow before:
                if active:
                    # if user push ENTER key:
                    if event.key == pygame.K_RETURN:
                        # Check if user's entry is digit and greater than 2 and smaller than 10.
                        if text.isdigit() and int(text) > 2 and int(text) <= 10:
                            # store user's entry in bord_size.
                            board_size = int(text)
                            # then program ends.
                            running = False 
                        else:
                            # if user's entry is not valid then text = ""
                            text = "" 
                    # if user push BACKSPACE key then:
                    elif event.key == pygame.K_BACKSPACE:
                        # delete last entered char.
                        text = text[:-1]
                    else:
                        # if user type sth then add it to text.
                        text += event.unicode 
        # Set background color of window white.
        screen.fill((WHITE))
        # draw the entry box.
        pygame.draw.rect(screen, color, input_box, 2, border_radius=10)  
        # convert entry text to shown text.
        text_surface = font.render(text, True, pygame.Color('black'))  
        # show the text that user is typing.
        screen.blit(text_surface, (input_box.x + 90, input_box.y + 7)) 
        input_box.w = max(200, text_surface.get_width() + 10)  
        # Show explain text ebove entry box "Enter board size".
        message_surface = font.render("Enter board size", True, pygame.Color('black'))
        screen.blit(message_surface, (80, 30))
        # Show Note text below entry box ""Note: Board size must be between 3 to 10!".
        message = fonta.render("Note: Board size must be between 3 to 10!", True, pygame.Color('black'))
        screen.blit(message, (35, 150))
        # update window.
        pygame.display.flip()
    # quit window and reurn board_size.  
    pygame.quit()  
    return board_size

# Move board size which user enetered in board_size var.
board_size = get_board_size()

# Building the main board of the game:
board = []
for i in range(board_size):
    row = []
    for j in range(board_size):
        row.append("_")
    board.append(row)

# Define rows labels a-z and define cols labels 1 - borad size.
row_labels = [chr(97 + i) for i in range(board_size)]
col_labels = [str(i + 1) for i in range(board_size)]

# Main board of the game is a pandas dataframe with defined row and col lables.
Main_board = pandas.DataFrame(board, index=row_labels, columns=col_labels)

# Creating the main window of the game: the window where user and agent are playing in. 
pygame.init()  
# Define size of each cell of the game: if board size > 6 then cell size is 60 else then cell size in 100.
if board_size > 6:
    cell_size = 60
else:
    cell_size = 100
# Define size of the main window.
screen_size = board_size * cell_size
# Creating Screen.
screen = pygame.display.set_mode((screen_size, screen_size))
# Set game name for the main window: "Neicharan's Dooz"
pygame.display.set_caption("Neicharan's Dooz")
# Define font and size of the texts.
font = pygame.font.Font(None, 60)

# Function to show the main window in screen.
def draw_board():
    # set window background color: White.
    screen.fill(WHITE)
    # Creating cells in window by drwing lines in horizental and vertical lines.
    for row in range(board_size):
        pygame.draw.line(screen, BLACK, (0, row * cell_size), (screen_size, row * cell_size), 2)
        pygame.draw.line(screen, BLACK, (row * cell_size, 0), (row * cell_size, screen_size), 2)

    # Drawing X & O in the Main board. each time someone makes a move by calling this function new Main_board is gonna be shown by checking all cells and draw X or O. 
    for row in range(board_size):
        for col in range(board_size):
            # Checking all cells of the the Main board:
            if Main_board.loc[row_labels[row]][str(col+1)] == "X":
                # Call draw_x function if the cell is X 
                draw_x(row, col)
            elif Main_board.loc[row_labels[row]][str(col+1)] == "O":
                # Call draw_o finction if the cell is O
                draw_o(row, col)

# Function for draw X in the main window.
def draw_x(row, col):
    padding = 20
    x_start = col * cell_size + padding
    y_start = row * cell_size + padding
    x_end = (col + 1) * cell_size - padding
    y_end = (row + 1) * cell_size - padding
    pygame.draw.line(screen, RED, (x_start, y_start), (x_end, y_end), 4)
    pygame.draw.line(screen, RED, (x_start, y_end), (x_end, y_start), 4)

# Function for drawing O in the main window.
def draw_o(row, col):
    center_x = col * cell_size + cell_size // 2
    center_y = row * cell_size + cell_size // 2
    radius = cell_size // 2 - 20
    pygame.draw.circle(screen, BLUE, (center_x, center_y), radius, 4)

# Function for getting row and col of the cell that user click on the screen.
def get_cell(x, y):
    # convert user choice on screen by getting coordinate of user's click in devide into by cell_size.
    row = y // cell_size
    col = x // cell_size
    # Return the converted row and col to make move in the Main_bord
    return row, col

# Function to make a move by agent.
def com_choice(board):
    # copy the current Main_board for using MiniMax algorithm.
    board_copy = board.copy()
    # Calling Minimax function to calculate best move for current game state.
    _ , best_move = Minimax(board_copy , board_size+3,  True)
    # Make the best calculated move if it exists.
    if best_move:
        board.loc[best_move[0], best_move[1]] = "O"
    # Print there is no possible moves if it doesn't.
    else:
        print("No possible moves for agent!")

# Function to calculate user's points in a line. This function is gonna user in row, col, diammeters and subdiammters check functions to calculate user's points.
def user_counter(arr):
    # Var to store all points in a line.
    user_points = 0
    # Var to calculate all cells that are X in a line.
    user_points_counter = 0
    # Checking all cells in line.
    for i in arr:
        # Check if the cell is X or not:
        if i == "X":
            # If X then user_points_counter + 1
            user_points_counter += 1
        else:
            # If not check if user_points_counter >= 3. It means that there and 3 or more X cell in a row.
            if user_points_counter >= 3:
                # If there and 3 or more X cell in a row then store points in user_points.
                user_points += user_points_counter
            # user_points_counter = 0 to calculate points for next cells. 
            user_points_counter = 0  
    # Store points if all cells in line are X (abardooz).
    if user_points_counter >= 3:
        user_points += user_points_counter
    return user_points

# Function to calculate agent's points in a line. This function is gonna user in row, col, diammeters and subdiammters check functions to calculate agent's points.
def agent_counter(arr):
    # Var to store all points in a line.
    agent_points = 0
    # Var to calculate all cells that are O in a line.
    agent_points_counter = 0
    # Checking all cells in line.
    for i in arr:
        # Check if the cell is O or not:
        if i == "O":
            # If O then user_points_counter + 1
            agent_points_counter += 1
        else:
            # If not check if agent_points_counter >= 3. It means that there and 3 or more O cell in a row.
            if agent_points_counter >= 3:
                # If there and 3 or more O cell in a row then store points in agent_points.
                agent_points += agent_points_counter
            # agent_points_counter = 0 to calculate points for next cells. 
            agent_points_counter = 0
    # Store points if all cells in line are O (abardooz).
    if agent_points_counter >= 3:
        agent_points += agent_points_counter  
    return agent_points

# Define vars to store all points of user and agent at the end of the game.
agent_points = 0
user_points = 0

# Function to calculate final points of user and agent at the end of the game.
def count_points(count_agent_points , count_user_points):
    # Note: Formula of final points: 2*n - 5 which is n is number of X cells or O cells in a row of lines.
    # Vars to store final points
    global agent_points
    global user_points
    # Calculate final points with the formula:
    if count_agent_points > 2:
        agent_points += ((2*count_agent_points)-5)
    if count_user_points > 2:
        user_points += ((2*count_user_points)-5)

# Define vars to store all points of user and agent at any state of the game.
live_agent_points = 0
live_user_points = 0

# Function to calculate final points of user and agent at any state of the game. These function and previous vars are gonna user to culcalate points in Terminal state of MiniMax algorithm. 
def live_count_points(live_count_agent_points , live_count_user_points):
    # Note: Formula of final points: 2*n - 5 which is n is number of X cells or O cells in a row of lines.
    # Vars to store final points
    global live_agent_points
    global live_user_points
    # Calculate final points with the formula:
    if live_count_agent_points > 2:
        live_agent_points += ((2*live_count_agent_points)-5)
    if live_count_user_points > 2:
        live_user_points += ((2*live_count_user_points)-5)

# Function to get every rows in the bord and calculate cells of the row and pass the cells in the row to count functions.
def check_win_rows(board , jump):
    # Convert board DataFrame to Numpy array to simplify get rows with indexing numpy array.
    numpy_board = board.to_numpy()
    # Loop for getting all rows:
    for i in range(board_size):
        # Define vars to store all points of user and agent at the row.
        count_agent_points = 0  # agent points
        count_user_points = 0   # user points
        row = numpy_board[i , :]     # get row of ith index of numpy array.
        # Pass this row to user_counter and agent_counter functions to calculate all X or O cells in this row.
        count_user_points = user_counter(row) 
        count_agent_points = agent_counter(row)
        # Calcalute points of this row: Note: there is a filter here. when ever we want to cal final points of the main game: jump = True then call count_points 
        # and when we want to cal points of any state of game: jump = Flase then call live_count_points.
        if jump:
            count_points(count_agent_points, count_user_points)
        else:
            live_count_points(count_agent_points, count_user_points)

# Function to get main diameter of the board and calculate cells of the it and pass cells in the diameter to count functions.
def check_win_diameter(board , jump):
    # Define vars to store all points of user and agent at main diameter.
    count_agent_points = 0    # agent points
    count_user_points = 0     # user points
    # Convert board DataFrame to Numpy array to simplify get main diameter.
    numpy_board = board.to_numpy()
    diameter = np.diagonal(numpy_board, offset= 0) # get main diameter of numpy array.
    # Pass main diameter to user_counter and agent_counter functions to calculate all X or O cells in main diameter.
    count_agent_points = agent_counter(diameter)
    count_user_points = user_counter(diameter)
    # Calcalute points of main diameter: Note: there is a filter here. when ever we want to cal final points of the main game: jump = True then call count_points 
    # and when we want to cal points of any state of game: jump = Flase then call live_count_points.
    if jump:
        count_points(count_agent_points, count_user_points)
    else:
        live_count_points(count_agent_points, count_user_points)

# Function to get every cols in the bord and calculate cells of the col and pass the cells in the col to count functions.
def check_win_columns(board , jump):
    # Convert board DataFrame to Numpy array to simplify get cols with indexing numpy array.
    numpy_board = board.to_numpy()
    # Loop for getting all cols:
    for i in range(board_size):
        # Define vars to store all points of user and agent at the col.
        count_agent_points = 0   # agent points
        count_user_points = 0    # user points
        column = numpy_board[:, i]   # get col of ith index of numpy array.
        # Pass this col to user_counter and agent_counter functions to calculate all X or O cells in this col.
        count_agent_points = agent_counter(column)
        count_user_points = user_counter(column)
        # Calcalute points of this col: Note: there is a filter here. when ever we want to cal final points of the main game: jump = True then call count_points 
        # and when we want to cal points of any state of game: jump = Flase then call live_count_points.
        if jump:
            count_points(count_agent_points, count_user_points)
        else:
            live_count_points(count_agent_points, count_user_points)

# Function to get main subdiameter of the board and calculate cells of the it and pass cells in the subdiameter to count functions.
def check_win_subdiameter(board , jump):
    # Define vars to store all points of user and agent at main subdiameter.
    count_agent_points = 0  # agent points
    count_user_points = 0   # user points
    # Convert board DataFrame to Numpy array to simplify get main subdiameter.
    numpy_board = board.to_numpy()
    # Get main subdiameter of numpy array: step 1: flip the board , step 2: get main diameter of flipped board which is main subdiameter of board.
    flipped_board = np.fliplr(numpy_board)
    subdiameter = np.diagonal(flipped_board, offset= 0)
    # Pass main subdiameter to user_counter and agent_counter functions to calculate all X or O cells in main diameter.
    count_agent_points = agent_counter(subdiameter)
    count_user_points = user_counter(subdiameter)
    # Calcalute points of main subdiameter: Note: there is a filter here. when ever we want to cal final points of the main game: jump = True then call count_points 
    # and when we want to cal points of any state of game: jump = Flase then call live_count_points.
    if jump:
        count_points(count_agent_points, count_user_points)
    else:
        live_count_points(count_agent_points, count_user_points)

# Function to get every diameter in the bord and calculate cells of the diameter and pass the cells in the diameter to count functions.
def check_parallel_diameters(board , jump):
    # Convert board DataFrame to Numpy array to simplify get all diameters.
    numpy_board = board.to_numpy()
    # Loop for getting all diameters:
    for i in range(1, board_size-2):
        # Define vars to store all points of user and agent at diameters above main diameter.
        updiameters_count_agent_points = 0  # agent points
        updiameters_count_user_points = 0   # user points
        # Get diameter of ith index of numpy array. Note offset = 1 refers to first diameter above main diameter and ... to offset = board_size - 2 which is the last diameter above main diameter.  
        upparallel = np.diagonal(numpy_board, offset = i) 
        # Pass this updiameter to user_counter and agent_counter functions to calculate all X or O cells in this updiameter.
        updiameters_count_agent_points = agent_counter(upparallel)
        updiameters_count_user_points = user_counter(upparallel)
        # Define vars to store all points of user and agent at diameters below main diameter.
        belowdiameters_count_agent_points = 0  # agent points
        belowdiameters_count_user_points = 0   # user points
        # Get diameter of ith index of numpy array. Note offset = -1 refers to first diameter below main diameter and ... to offset = -(board_size - 2) which is the last diameter below main diameter.
        belowparallel = np.diagonal(numpy_board, offset= -i)
        # Pass this belowdiameter to user_counter and agent_counter functions to calculate all X or O cells in this belowdiameter.
        belowdiameters_count_agent_points = agent_counter(belowparallel)
        belowdiameters_count_user_points = user_counter(belowparallel)
        # Calcalute points of updiameter and belowdiameter: Note: there is a filter here. when ever we want to cal final points of the main game: jump = True then call count_points 
        # and when we want to cal points of any state of game: jump = Flase then call live_count_points.
        if jump:
            count_points(updiameters_count_agent_points, updiameters_count_user_points)
            count_points(belowdiameters_count_agent_points, belowdiameters_count_user_points)
        else:
            live_count_points(updiameters_count_agent_points, updiameters_count_user_points)
            live_count_points(belowdiameters_count_agent_points, belowdiameters_count_user_points)

# Function to get every subdiameter in the bord and calculate cells of the subdiameter and pass the cells in the subdiameter to count functions.
def check_parallel_subdiameters(board , jump):
    # Convert board DataFrame to Numpy array to simplify get all subdiameters.
    numpy_board = board.to_numpy()
    # Flip the board Note: Same as cal main subdiameter we must flip the board first and the rest of the proc will be same as check_parallel_diameter function.
    flipped_board = np.fliplr(numpy_board)
    # Loop for getting all subdiameters:
    for i in range(1, board_size-2):
        # Define vars to store all points of user and agent at subdiameters above main subdiameter.
        upsubdiameters_count_agent_points = 0   # agent points
        upsubdiameters_count_user_points = 0   # user points
        # Get subdiameter of ith index of numpy array. Note offset = 1 refers to first subdiameter above main subdiameter and ... to offset = board_size - 2 which is the last subdiameter above main subdiameter.  
        upsubparallel = np.diagonal(flipped_board, offset = i)
        # Pass this upsubdiameter to user_counter and agent_counter functions to calculate all X or O cells in this upsubdiameter.
        upsubdiameters_count_agent_points = agent_counter(upsubparallel)
        upsubdiameters_count_user_points = user_counter(upsubparallel)
        # Define vars to store all points of user and agent at subdiameters below main subdiameter.
        belowsubdiameters_count_agent_points = 0   # agent points
        belowsubdiameters_count_user_points = 0   # user points
         # Get subdiameter of ith index of numpy array. Note offset = -1 refers to first subdiameter below main subdiameter and ... to offset = -(board_size - 2) which is the last subdiameter below main subdiameter.
        belowsubparallel = np.diagonal(flipped_board, offset = -i)
        # Pass this belowsubdiameter to user_counter and agent_counter functions to calculate all X or O cells in this belowsubdiameter.
        belowsubdiameters_count_agent_points = agent_counter(belowsubparallel)
        belowsubdiameters_count_user_points = user_counter(belowsubparallel)
        # Calcalute points of upsubdiameter and belowsubdiameter: Note: there is a filter here. when ever we want to cal final points of the main game: jump = True then call count_points 
        # and when we want to cal points of any state of game: jump = Flase then call live_count_points.
        if jump:
            count_points(upsubdiameters_count_agent_points, upsubdiameters_count_user_points)
            count_points(belowsubdiameters_count_agent_points, belowsubdiameters_count_user_points)
        else:
            live_count_points(upsubdiameters_count_agent_points, upsubdiameters_count_user_points)
            live_count_points(belowsubdiameters_count_agent_points, belowsubdiameters_count_user_points)

# Method 1: Transposition table: this function is used to write a transposition table of every game in a text file to store all transposition tables of played game to make MiniMax faster. Note 1: transposition tables ard dicts.
# transposition table for X and transposition table for O are gonna be passed to this function and this function create the text file. Note2: if the file doesn't exist by now it will creat first one
# and if a file exist it will add new transposition tables to previous file.
def transposition_writer(move, size, xtrans_table, otrans_table):
    # If move = "X" then we want to create xtransposition_table:
    if move == "X":
        # Open or Create file with a name xtransposition_table{size}.txt which is size is the board_size.
        with open(f"xtransposition_table{size}.txt", "a") as xfile:
            # Loop to write all element of xtransposition_table dict to file:
            for x,y in xtrans_table.items():
                xfile.write(f"{x}:{y}".replace(" ", "")+ "\n")
    # If move = "O" then we want to create otransposition_table:
    if move == "O":
        # Open or Create file with a name otransposition_table{size}.txt which is size is the board_size.
        with open(f"otransposition_table{size}.txt", "a") as ofile:
            # Loop to write all element of otransposition_table dict to file:
            for x,y in otrans_table.items():
                ofile.write(f"{x}:{y}".replace(" ", "") + "\n")

# Function to read transposition tables file and store them in transposition table dicts in script.
def transposition_table_reader(move, size):
    # Create transposition table dicts.
    xtrans_table = {}   #xtransposition_table
    otrans_table = {}   #otransposition_table

    # If move = "X" then we want to read xtransposition_table:
    if move == "X":
        # If file dose not exist(never played a game with this size) then create a clear table.
        if not os.path.exists(f"xtransposition_table{size}.txt"):
            xtrans_table = {}
        # If file exists then convert all lines of text file into transposition tables elements format.
        else:
            # Open file to read the lines and convert to dict elements:
            with open(f"xtransposition_table{size}.txt", "r") as xfile:
                # Store all lines of text file in a var. this var will be a list of all lines.
                xfile_lines = xfile.readlines()
                # Loop for converting all lines:
                for i in range(len(xfile_lines)):
                    # Var to save ith line of the lines list.
                    line = xfile_lines[i]
                    # Remove all \n from this line. 
                    line.replace("\n", "")
                    # Convert line to dict element and update dict with new line. prep_line function will be explained.
                    xtrans_table.update(prep_line(line))

    # If move = "O" then we want to read otransposition_table:
    if move == "O":
        # If file dose not exist(never played a game with this size) then create a clear table.
        if not os.path.exists(f"otransposition_table{size}.txt"):
            otrans_table = {}
        # If file exists then convert all lines of text file into transposition tables elements format.
        else:
            # Open file to read the lines and convert to dict elements:
            with open(f"otransposition_table{size}.txt", "r") as ofile:
                # Store all lines of text file in a var. this var will be a list of all lines.
                ofile_lines = ofile.readlines()
                # Loop for converting all lines:
                for i in range(len(ofile_lines)):
                    # Var to save ith line of the lines list.
                    line = ofile_lines[i]
                    # Remove all \n from this line. 
                    line.replace("\n", "")
                    # Convert line to dict element and update dict with new line. prep_line function will be explained.
                    otrans_table.update(prep_line(line))
    # return transposition tables
    return xtrans_table, otrans_table

# Function to convert lines of transposition tables text file to dict element to use in app. this function will get a line and convert it to dict element.
def prep_line(line):
    # Delete all aditional chars.
    line_list = line.strip()
    # Split line to tow parts between ":".
    line_list = line.split(":")
    # First part is string format of the table it will be store in table var.
    table = line_list[0]
    # In the second part which is value and best move, remove "()"
    tuple_amounts = line_list[1].replace("(", "").replace(")", "").split(",")
    # Convert value to int to use in algorithm
    tuple_amounts[0] = int(tuple_amounts[0])
    # To get the best move reomve "[]", "'", "\'" and any aditional chars.
    move_list = [tuple_amounts[1].strip().replace("[", "").replace("]", "").replace('"', "").replace("'", "").strip(), tuple_amounts[2].strip().replace("[", "").replace("]", "").replace('"', "").replace("'", "").strip()]
    move_list[0] = move_list[0].strip('\'').strip()
    move_list[1] = move_list[1].strip('\'').strip()
    # Store value and best move after converting in a list.
    lista = []
    lista.append(tuple_amounts[0])
    lista.append(move_list)
    # convert that list to tuple.
    tup_lista = tuple(lista)
    # return dict element
    return {table: tup_lista}

# Store transposition tables in tow vars: xtransposition_table for "X" and otransposition_table for "O".
xtransposition_table, _ = transposition_table_reader("X", board_size)
_ , otransposition_table = transposition_table_reader("O", board_size)

# MiniMax Function: Designed by MiniMax Algorithm with alpha beta pruning.
def Minimax(board , depth, maxamim, alpha=float('-inf'), beta=float('inf')):
    # Global vars to cal points for user and agent in terminal state,
    global live_agent_points
    global live_user_points
    # Treminal state: If game is over (all cells are filled) or we reached to final depth which is passed in com_choice function.
    if check_game_over(board) or depth == 0:
        # Cal points for user and agent at any terminal state. 
        live_user_points = 0
        live_agent_points = 0
        return score(board) , None
    
    # Convert board dataframe to string for checking in transposition tables or save in it.
    board_key = board.to_string().replace('\n', '')

    # If max the it means its agant turn:
    if maxamim:
        # Check if this board is already in transposition table or not. if it is then return the previous move and points which is saved in transposition table before.
        if board_key in otransposition_table:
            return otransposition_table[board_key]
        # If it is not in transposition table then:
        # best value for now = -infinity
        best_value = float('-inf')
        # up to now we have no best_move and we must find it.
        best_move = None
        # copy board with deepcopy.
        board_copy = deepcopy(board)
        # Loop to check all moves in MiniMax Algorithm: possible_moves function will return all clear cells in board.
        for move in possible_moves(board):
            # Make a move by agent to go forward in MiniMax Algorithm. 
            board_copy.loc[move[0],move[1]] = "O"
            # Call Minimax function again with reducing depth and call min agent and store final value of state in a var.
            value , _ = Minimax(board_copy, depth-1, False, alpha, beta)
            # Redo move. 
            board_copy.loc[move[0],move[1]] = "_"
            # Compare value with best_value: if now move value is greater and previous best_value then now move is the best_move far now.
            if value > best_value:
                # then our best value and move willl be this new move and value.
                best_value = value
                best_move = move

            # Alpha bata pruning for max node:
            alpha = max(alpha, value)
            if beta <= alpha:
                break
        # save this board with final value and best_move of it in transposition table.
        otransposition_table[board_key] = (best_value, best_move)
        # return final found best_value and best_move
        return best_value , best_move
    
    # If min the it means its agant's opponent turn:
    else:
        # Check if this board is already in transposition table or not. if it is then return the previous move and points which is saved in transposition table before.
        if board_key in xtransposition_table:
            return xtransposition_table[board_key]
        # If it is not in transposition table then:
        # best value for now = infinity
        best_value = float('inf')
        # up to now we have no best_move and we must find it.
        best_move = None
        # copy board with deepcopy.
        board_copy = deepcopy(board)
        # Loop to check all moves in MiniMax Algorithm: possible_moves function will return all clear cells in board.
        for move in possible_moves(board):
            # Make a move by agent's opponent to go forward in MiniMax Algorithm. 
            board_copy.loc[move[0],move[1]] = "X"
            # Call Minimax function again with reducing depth and call max agent and store final value of state in a var.
            value, _ = Minimax(board_copy,depth-1, True, alpha, beta)
            # Redo move. 
            board_copy.loc[move[0],move[1]] = "_"
            # Compare value with best_value: if now move value is smaller and previous best_value then now move is the best_move far now.
            if value < best_value:
                # then our best value and move willl be this new move and value.
                best_value = value
                best_move = move
            
            # Alpha bata pruning for min node:
            beta = min(beta, value)
            if beta <= alpha:
                break

        # save this board with final value and best_move of it in transposition table.
        xtransposition_table[board_key] = (best_value, best_move)
        # return final found best_value and best_move
        return best_value , best_move

# Function to cal all points for any state of board.   
def score(board):
    # call all check functions with jump = False
    check_win_columns(board , False)
    check_win_diameter(board , False)
    check_win_subdiameter(board, False)
    check_win_rows(board , False)
    check_parallel_diameters(board , False)
    check_parallel_subdiameters(board , False)
    # then if user wins return -1 cuz agent lose and if agent wins return 1 else return 0 (draw)
    if live_user_points > live_agent_points:
        return -1
    elif live_agent_points > live_user_points:
        return 1
    else:
        return 0

# Function to check if this state is terminal or not. Check if game is over or not.
def check_game_over(board):
    full_places = 0
    # Loop for checking all filled cells of the board:
    for i in range(board_size):
        row = row_labels[i]
        for j in range(1, board_size+1):
            if board.loc[row, str(j)] != "_":
                full_places += 1

    # If all cells are filled then game is over so return 1
    if full_places == board_size*board_size:
        return 1

# Function to cal all empty moves in board for using in MiniMax function.
def possible_moves(board):
    # Create a list to store all empty moves.
    possible_moves_list = []
    # Loop to check every cell of the board and add it to possible_moves_list if it is empty.
    for i in range(board_size):
        row = row_labels[i]
        for j in range(1, board_size+1):
            if board.loc[row, str(j)] == "_":
                # move is a list with this format = ["a-z", "1-board_size"]
                move = [row, str(j)]
                possible_moves_list.append(move)
    # return the final list
    return possible_moves_list

# Function for result window.
def show_game_result(result_message, user_points, agent_points, final_board):
    # Start pygame app.
    pygame.init()
    # Set window size
    board_size = len(final_board) #Number of rows of board.
    cell_size = 50  #size of each cell
    screen_width = 400 + board_size * cell_size # Window width according to size of board.
    screen_height = max(250, board_size * cell_size) + 50   #Window height minimum 250 pixle
    # Set Screen and it's name: "Game Over"  
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Game Over")
    # Set font for showing result of the game
    font = pygame.font.Font(None, 60)
    # Set font fot showing points 
    small_font = pygame.font.Font(None, 40) 
    # Set font for showing "Press any key to exit"
    tiny_font = pygame.font.Font(None, 30) 
    # Program runs:
    running = True
    while running:
        # chekc if anything happens:
        for event in pygame.event.get():
            # If user click on exit buttom then program ends.
            if event.type == pygame.QUIT: 
                pygame.quit()
                sys.exit()
            # If user clicked any keybord key the program ends.
            if event.type == pygame.KEYDOWN: 
                running = False
        # set background white.
        screen.fill(WHITE)
        # show result text
        result_text = font.render(result_message, True, pygame.Color('black'))
        screen.blit(result_text, (20, 20))
        # show user points
        user_score_text = small_font.render(f"Your Points: {user_points}", True, pygame.Color('blue'))
        # show agent points
        agent_score_text = small_font.render(f"Computer Points: {agent_points}", True, pygame.Color('red'))
        screen.blit(user_score_text, (20, 100))
        screen.blit(agent_score_text, (20, 150))
        # show text "Press any key to exit"
        sub_text_surface = tiny_font.render("Press any key to exit", True, pygame.Color('black'))
        screen.blit(sub_text_surface, (20, screen_height - 40))
        # Set Final board place in window.
        board_start_x = 350
        board_start_y = 50
        # Draw Final board in set placed
        for row in range(board_size):
            for col in range(board_size):
                # Cal cordinate of each cell
                cell_x = board_start_x + col * cell_size
                cell_y = board_start_y + row * cell_size
                # Draw each cell
                pygame.draw.rect(screen, BLACK, (cell_x, cell_y, cell_size, cell_size), 2) 
                # Draw "X" if cell = "X":
                if final_board.loc[row_labels[row]][str(col+1)] == "X":
                    pygame.draw.line(screen, BLUE, (cell_x + 10, cell_y + 10),
                                     (cell_x + cell_size - 10, cell_y + cell_size - 10), 3)
                    pygame.draw.line(screen, BLUE, (cell_x + 10, cell_y + cell_size - 10),
                                     (cell_x + cell_size - 10, cell_y + 10), 3)
                # Draw "O" if cell = "O":
                elif final_board.loc[row_labels[row]][str(col+1)] == "O":
                    pygame.draw.circle(screen, RED, (cell_x + cell_size // 2, cell_y + cell_size // 2),
                                       cell_size // 3, 3)
        # update window
        pygame.display.flip()
    #quit if user enter a key.
    pygame.quit()

# Cuz user first start game then current_player = "X"
current_player = "X"

# Main function of game. function that will draw the board, get user choice and make agent move.
def main():
    # Global current_player cuz it will be changed in this function as user of agent's turn.
    global current_player
    # GUI Settings. Running = True while the game is not finished.
    running = True
    while running:
        # draw board first.
        draw_board()
        for event in pygame.event.get():
            
            # If user click on exit buttom then program ends.
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # If user click on a cell then:
            if event.type == pygame.MOUSEBUTTONDOWN and current_player == "X":
                # Get coordinate of user's click and store in x , y
                x, y = event.pos
                # Convert coordinate of user's click with get_cell function and store it in row, col. 
                row, col = get_cell(x, y)
                # Check if the cell choice of user is empty:
                if Main_board.loc[row_labels[row], str(col+1)] == "_":
                    # if it is empty then make move for user if not then wait for user to choose an empty cell.
                    Main_board.loc[row_labels[row], str(col+1)] = current_player
                    # after user move current_player = "O" cuz its agent's turn now.
                    current_player = "O"
                    # draw board after user make move
                    draw_board()
                    pygame.display.flip()

        # after user's move if game is not over then its agent's turn.
        if check_game_over(Main_board) != 1:
            # agent make move.
            if current_player == "O":
                com_choice(Main_board)
                # after agent's move it is user's turn again so current_player = "X"
                current_player = "X"

        # if game is over then:
        else:
            # wait for 1 second and then running = False 
            time.sleep(1)
            running = False

        # show board
        draw_board()
        pygame.display.flip()

    # Cuz game is over then check for winner and store result in winner.
    winner = check_winner()
    if winner:
        running = False
    result_message = "Draw!" if winner == "Draw" else f"{'You' if winner == 'User' else 'Agent'} Won!"
    # show result window.
    show_game_result(result_message, user_points, agent_points, Main_board)

# Function to cal all points at the final of the game.
def check_winner():
    # call all check functions with jump = True
    check_win_rows(Main_board , True)
    check_win_columns(Main_board , True)
    check_win_diameter(Main_board , True)
    check_win_subdiameter(Main_board, True)
    check_parallel_diameters(Main_board , True)
    check_parallel_subdiameters(Main_board , True)
    # Call transposition tables writer to write transposition tables of this game to file.
    transposition_writer("X", board_size, xtransposition_table, otransposition_table)
    transposition_writer("O", board_size, xtransposition_table, otransposition_table)
    # then if user wins return "User" and if agent wins return "Agent" else return "draw"
    if  user_points > agent_points:
        result_message = "User"
    elif user_points < agent_points:
        result_message = "Agent"
    else:
        result_message = "Draw"
    return result_message


if __name__ == "__main__":
    main()
