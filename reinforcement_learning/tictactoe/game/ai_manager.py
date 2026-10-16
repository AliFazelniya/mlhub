"""Selects and applies the AI move, resolving RL vs Minimax engine support."""

from typing import Optional, Tuple

from game.engine.board import Board
from game.engine.minmax import MinimaxAI
from game.models_rl.registry import registry


def resolve_engine(requested_mode: str, board_size: int) -> str:
    """Return the engine actually usable for this board size.

    Falls back from ``'rl'`` to ``'minimax'`` when no DQN model exists.
    """
    if requested_mode == 'rl' and registry.has(board_size):
        return 'rl'
    return 'minimax'


def compute_ai_move(
    board: Board,
    ai_mark: str,
    human_mark: str,
    requested_mode: str,
) -> Tuple[Optional[Tuple[int, int]], str]:
    """Compute the AI move and report which engine was used.

    Returns ``((row, col) | None, engine_used)``.
    """
    engine_used = resolve_engine(requested_mode, board.size)

    if engine_used == 'rl':
        try:
            from game.models_rl.rl_agent import RLAgent
            agent = RLAgent(
                ai_player=ai_mark,
                human_player=human_mark,
                board_size=board.size,
            )
            move = agent.get_best_move(board)
            if move is not None:
                return move, 'rl'
            engine_used = 'minimax'
        except Exception:
            engine_used = 'minimax'

    minimax = MinimaxAI(ai_player=ai_mark, human_player=human_mark)
    return minimax.get_best_move(board), 'minimax'
