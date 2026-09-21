import gymnasium as gym
from gymnasium import spaces
import numpy as np
import random
from board import Board

class DoozEnv(gym.Env):
    def __init__(self, board_size=5, ai_mark='O', human_mark='X'):
        super(DoozEnv, self).__init__()
        
        self.board_size = board_size
        self.ai_mark = ai_mark
        self.human_mark = human_mark
        
        self.action_space = spaces.Discrete(self.board_size * self.board_size)
        
        self.observation_space = spaces.Box(
            low=-1, high=1, 
            shape=(self.board_size, self.board_size), 
            dtype=np.float32
        )
        
        self.board = Board(self.board_size)
        self.prev_score_diff = 0

    def reset(self, seed=None, options=None):
        """بازی را به حالت اولیه برمی‌گرداند"""
        super().reset(seed=seed)
        self.board = Board(self.board_size)
        self.prev_score_diff = 0
        
        if self.human_mark == 'X':
            self._opponent_play()
            
        return self._get_obs(), {}

    def step(self, action):
        row = action // self.board_size
        col = action % self.board_size
        
        if self.board.grid[row][col] is not None:
            return self._get_obs(), -10.0, True, False, {"reason": "illegal_move"}
            
        self.board.make_move(row, col, self.ai_mark)
        
        done = self.board.is_full()
   
        if not done:
            self._opponent_play()
            done = self.board.is_full()
            
        reward = self._calculate_reward()
        
        return self._get_obs(), reward, done, False, {}

    def _get_obs(self):
        obs = np.zeros((self.board_size, self.board_size), dtype=np.float32)
        for r in range(self.board_size):
            for c in range(self.board_size):
                if self.board.grid[r][c] == self.ai_mark:
                    obs[r, c] = 1.0
                elif self.board.grid[r][c] == self.human_mark:
                    obs[r, c] = -1.0
        return obs

    def _calculate_reward(self):
        score_x, score_o = self.board.calculate_scores()
        
        ai_score = score_o if self.ai_mark == 'O' else score_x
        human_score = score_x if self.human_mark == 'X' else score_o
        
        current_score_diff = ai_score - human_score

        reward = current_score_diff - self.prev_score_diff
        self.prev_score_diff = current_score_diff
        
        return float(reward)

    def _opponent_play(self):
        legal_moves = self.board.get_legal_moves()
        if legal_moves:
            r, c = random.choice(legal_moves)
            self.board.make_move(r, c, self.human_mark)