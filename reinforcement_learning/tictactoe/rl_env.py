import gymnasium as gym
from gymnasium import spaces
import numpy as np
import random
from board import Board
from minmax import MinimaxAI


class TicEnv(gym.Env):
    def __init__(self, board_size=5, ai_mark='O', human_mark='X'):
        super().__init__()

        self.board_size = board_size
        self.ai_mark = ai_mark
        self.human_mark = human_mark

        self.action_space = spaces.Discrete(board_size * board_size)

        self.observation_space = spaces.Box(
            low=-1,
            high=1,
            shape=(board_size, board_size),
            dtype=np.float32,
        )

        self.board = Board(board_size)
        self.prev_score_diff = 0
        self.sparring_partner = MinimaxAI(
            ai_player=self.human_mark,
            human_player=self.ai_mark,
        )

        self._obs_buffer = np.zeros(
            (board_size, board_size),
            dtype=np.float32,
        )

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)

        self.board = Board(self.board_size)
        self.prev_score_diff = 0
        self._obs_buffer.fill(0)

        if self.human_mark == 'X':
            self._opponent_play()

        return self._get_obs(), {}

    def step(self, action):
        row = action // self.board_size
        col = action - row * self.board_size

        if self.board.grid[row][col] is not None:
            return (
                self._get_obs(),
                -10.0,
                True,
                False,
                {"reason": "illegal_move"},
            )

        self.board.make_move(row, col, self.ai_mark)

        score_x, score_o = self.board.calculate_scores()
        ai_score = score_o if self.ai_mark == 'O' else score_x

        if ai_score > 0:
            return self._get_obs(), 1.0, True, False, {}

        if self.board.is_full():
            return self._get_obs(), 0.5, True, False, {}

        self._opponent_play()

        score_x, score_o = self.board.calculate_scores()
        human_score = score_x if self.human_mark == 'X' else score_o

        if human_score > 0:
            return self._get_obs(), -1.0, True, False, {}

        if self.board.is_full():
            return self._get_obs(), 0.5, True, False, {}

        return self._get_obs(), 0.0, False, False, {}

    def _get_obs(self):
        grid = self.board.grid
        obs = self._obs_buffer
        ai_mark = self.ai_mark
        human_mark = self.human_mark

        for r in range(self.board_size):
            row = grid[r]
            obs_row = obs[r]
            for c in range(self.board_size):
                cell = row[c]
                if cell == ai_mark:
                    obs_row[c] = 1.0
                elif cell == human_mark:
                    obs_row[c] = -1.0
                else:
                    obs_row[c] = 0.0
        return obs.copy()

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

        if not legal_moves:
            return

        if random.random() < 0.5:
            r, c = random.choice(legal_moves)
        else:
            best_move = self.sparring_partner.get_best_move(self.board)
            if best_move is not None:
                r, c = best_move
            else:
                r, c = random.choice(legal_moves)

        self.board.make_move(r, c, self.human_mark)