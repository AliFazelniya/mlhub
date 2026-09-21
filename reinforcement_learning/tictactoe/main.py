"""
Main Application Entry Point.
Integrates Board, RL Agent (DQN), and the Pygame GUI.
"""
import os
import sys
import warnings
warnings.filterwarnings("ignore")
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0' 

import pygame
import numpy as np
from board import Board
from gui import GameGUI, prompt_setup, show_game_over
from rl_agent import DQN
from stable_baselines3 import DQN
import random

class RLAgent:
    def __init__(self, ai_player: str, human_player: str, board_size: int):
        self.ai = ai_player
        self.human = human_player
        self.board_size = board_size

        base_dir = os.path.dirname(os.path.abspath(__file__))
        model_filename = f"dqn_model_{board_size}x{board_size}.zip"
        model_path = os.path.join(base_dir, model_filename)
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"\n[Error] Model '{model_path}' not found!\n"
                f"Please run the train.py file first."
            )
            
        self.model = DQN.load(model_path)
        print(f"Model loaded successfully from {model_path}")

    def get_best_move(self, board: Board):
        legal_moves = board.get_legal_moves()
        if not legal_moves:
            return None
            
        state = np.zeros((self.board_size, self.board_size), dtype=np.float32)
        for r in range(self.board_size):
            for c in range(self.board_size):
                if board.grid[r][c] == self.ai:
                    state[r, c] = 1.0
                elif board.grid[r][c] == self.human:
                    state[r, c] = -1.0
                    
        action, _states = self.model.predict(state, deterministic=True)
        
        row = action.item() // self.board_size
        col = action.item() % self.board_size
        if (row, col) not in legal_moves:
            return random.choice(legal_moves)
            
        return (row, col)


class GameController:
    def __init__(self):
        size, self.human_mark = prompt_setup()
        self.ai_mark = 'O' if self.human_mark == 'X' else 'X'

        self.board = Board(size)
        try:
            self.ai_agent = RLAgent(ai_player=self.ai_mark, human_player=self.human_mark, board_size=size)
        except FileNotFoundError as e:
            print(e)
            sys.exit(1)
        
        self.view = GameGUI(self.board)
        
        self.current_turn = 'X'

    def update_display(self):
        score_x, score_o = self.board.calculate_scores()
        mouse_pos = pygame.mouse.get_pos()
        self.view.draw_board(score_x, score_o, self.human_mark, mouse_pos)

    def run(self) -> None:
        running = True
        
        while running and not self.board.is_full():
            self.update_display()
            
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
                                self.current_turn = self.ai_mark

            elif self.current_turn == self.ai_mark:
                pygame.event.pump()
                
                ai_move = self.ai_agent.get_best_move(self.board)
                if ai_move:
                    row, col = ai_move
                    self.board.make_move(row, col, self.ai_mark)
                    
                self.current_turn = self.human_mark

        self.update_display()
        score_x, score_o = self.board.calculate_scores()
        show_game_over(score_x, score_o, self.human_mark)


if __name__ == "__main__":
    game = GameController()
    game.run()