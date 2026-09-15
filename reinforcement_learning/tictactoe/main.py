"""
Main Application Entry Point.
Integrates Board, Minimax AI, and the Modern Pygame GUI.
"""

import sys
import pygame
from board import Board
from ai import MinimaxAI
from gui import GameGUI, prompt_setup, show_game_over


class GameController:
    def __init__(self):
        # 1. Ask for board size and human role via graphical prompt
        size, self.human_mark = prompt_setup()
        self.ai_mark = 'O' if self.human_mark == 'X' else 'X'
        
        # 2. Initialize Core Logic and AI with selected roles
        self.board = Board(size)
        self.ai_agent = MinimaxAI(ai_player=self.ai_mark, human_player=self.human_mark)
        
        # 3. Initialize Pygame GUI Window
        self.view = GameGUI(self.board)
        
        # In Tic-Tac-Toe, 'X' always goes first
        self.current_turn = 'X'

    def format_move(self, row: int, col: int) -> str:
        """Helper to print moves in the standard a1, b3 format for logs."""
        row_char = chr(ord('a') + row)
        col_num = col + 1
        return f"{row_char}{col_num}"

    def update_display(self):
        """Helper to fetch scores and draw the board with hover state."""
        score_x, score_o = self.board.calculate_scores()
        mouse_pos = pygame.mouse.get_pos()
        self.view.draw_board(score_x, score_o, self.human_mark, mouse_pos)

    def run(self) -> None:
        """Main game loop for event handling and turn management."""
        running = True
        
        while running and not self.board.is_full():
            self.update_display()
            
            # --- HUMAN TURN ---
            if self.current_turn == self.human_mark:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                        
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        move = self.view.get_move_from_mouse(event.pos)
                        if move is not None:
                            row, col = move
                            if self.board.make_move(row, col, self.human_mark):
                                self.current_turn = self.ai_mark  # Switch turn

            # --- AI TURN ---
            elif self.current_turn == self.ai_mark:
                # Keep checking for QUIT event while AI is 'thinking' (prevent OS from saying "Not Responding")
                pygame.event.pump()
                
                ai_move = self.ai_agent.get_best_move(self.board)
                if ai_move:
                    row, col = ai_move
                    self.board.make_move(row, col, self.ai_mark)
                    
                self.current_turn = self.human_mark  # Switch turn

        # --- GAME OVER ---
        self.update_display() # One final draw
        score_x, score_o = self.board.calculate_scores()
        show_game_over(score_x, score_o, self.human_mark)


if __name__ == "__main__":
    game = GameController()
    game.run()
