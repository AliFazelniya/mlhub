"""
Main Application Entry Point.
Integrates Board, RL Agent (DQN), and the Modern Pygame GUI.
"""

import sys
import os
import pygame
import torch
import numpy as np
from board import Board
from gui import GameGUI, prompt_setup, show_game_over
from rl_agent import DQN

class RLAgent:
    def __init__(self, ai_player: str, human_player: str, board_size: int):
        self.ai = ai_player
        self.human = human_player
        self.board_size = board_size
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        model_path = f"dooz_dqn_{board_size}x{board_size}.pth"
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"\n[Error] Model '{model_path}' not found!\n"
                f"Please train the model for board size {board_size}x{board_size} first by running 'train.py'."
            )
            
        self.model = DQN(board_size * board_size, board_size * board_size).to(self.device)
        self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        self.model.eval()
        print(f"[RL] Model loaded successfully from {model_path}")

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
                    
        state_tensor = torch.FloatTensor(state).flatten().unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            q_values = self.model(state_tensor).cpu().numpy()[0]
            
        best_val = -float('inf')
        best_move = None
        for (r, c) in legal_moves:
            action_idx = r * self.board_size + c
            if q_values[action_idx] > best_val:
                best_val = q_values[action_idx]
                best_move = (r, c)
                
        return best_move


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