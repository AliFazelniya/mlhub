"""RL inference agent backed by the in-memory DQN model registry.

This mirrors the legacy ``RLAgent`` from ``main.py`` but never loads a model
per request; it reads from :data:`game.models_rl.registry.registry`.
"""

import random
from typing import Optional, Tuple

import numpy as np

from game.engine.board import Board
from game.engine.minmax import MinimaxAI
from game.models_rl.registry import registry


class RLAgent:
    def __init__(self, ai_player: str, human_player: str, board_size: int):
        self.ai = ai_player
        self.human = human_player
        self.board_size = board_size
        self.model = registry.get(board_size)
        if self.model is None:
            raise FileNotFoundError(
                f"No trained DQN model loaded for a {board_size}x{board_size} board."
            )

    def _encode_state(self, board: Board) -> np.ndarray:
        state = np.zeros((self.board_size, self.board_size), dtype=np.float32)
        for r in range(self.board_size):
            for c in range(self.board_size):
                if board.grid[r][c] == self.ai:
                    state[r, c] = 1.0
                elif board.grid[r][c] == self.human:
                    state[r, c] = -1.0
        return state

    def get_best_move(self, board: Board) -> Optional[Tuple[int, int]]:
        legal_moves = board.get_legal_moves()
        if not legal_moves:
            return None

        state = self._encode_state(board)
        action, _states = self.model.predict(state, deterministic=True)

        row = int(action.item()) // self.board_size
        col = int(action.item()) % self.board_size

        if (row, col) not in legal_moves:
            # Never crash: fall back to Minimax, then to a random legal move.
            fallback = MinimaxAI(ai_player=self.ai, human_player=self.human)
            try:
                best = fallback.get_best_move(board)
            except Exception:
                best = None
            if best is not None:
                return best
            return random.choice(legal_moves)

        return (row, col)
