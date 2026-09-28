import math
from typing import Tuple, List, Optional
from board import Board

class MinimaxAI:
    def __init__(self, ai_player: str = 'O', human_player: str = 'X'):
        self.ai = ai_player
        self.human = human_player

    def get_best_move(self, board: Board) -> Optional[Tuple[int, int]]:
        legal_moves = board.get_legal_moves()
        if not legal_moves:
            return None

        smart_moves = self._get_smart_moves_from_legal(board, legal_moves)
        if not smart_moves:
            return None

        depth_limit = self._calculate_dynamic_depth(
            board.size, len(legal_moves)
        )

        best_val = -math.inf
        best_move = None

        for r, c in smart_moves:
            board.make_move(r, c, self.ai)
            move_val = self._minimax(
                board,
                depth_limit - 1,
                -math.inf,
                math.inf,
                False,
            )
            board.undo_move(r, c)

            if move_val > best_val:
                best_val = move_val
                best_move = (r, c)

        return best_move

    def _minimax(
        self,
        board: Board,
        depth: int,
        alpha: float,
        beta: float,
        is_maximizing: bool,
    ) -> float:
        if depth == 0 or board.is_full():
            return self._evaluate_board(board)

        legal_moves = board.get_legal_moves()
        smart_moves = self._get_smart_moves_from_legal(board, legal_moves)

        if is_maximizing:
            max_eval = -math.inf

            for r, c in smart_moves:
                board.make_move(r, c, self.ai)
                value = self._minimax(
                    board, depth - 1, alpha, beta, False
                )
                board.undo_move(r, c)

                if value > max_eval:
                    max_eval = value
                if value > alpha:
                    alpha = value
                if beta <= alpha:
                    break

            return max_eval

        min_eval = math.inf

        for r, c in smart_moves:
            board.make_move(r, c, self.human)
            value = self._minimax(
                board, depth - 1, alpha, beta, True
            )
            board.undo_move(r, c)

            if value < min_eval:
                min_eval = value
            if value < beta:
                beta = value
            if beta <= alpha:
                break

        return min_eval

    def _evaluate_board(self, board: Board) -> float:
        score_x, score_o = board.calculate_scores()

        if self.ai == 'O':
            return score_o - score_x
        return score_x - score_o

    def _calculate_dynamic_depth(self, board_size: int, empty_cells: int) -> int:
        if board_size <= 4:
            return min(6, empty_cells)
        elif board_size <= 6:
            return min(5, empty_cells)
        return min(4, empty_cells)

    def _get_smart_moves(self, board: Board) -> List[Tuple[int, int]]:
        return self._get_smart_moves_from_legal(
            board, board.get_legal_moves()
        )

    def _get_smart_moves_from_legal(
        self,
        board: Board,
        legal_moves: List[Tuple[int, int]],
    ) -> List[Tuple[int, int]]:
        if len(legal_moves) == board.size * board.size:
            return [(board.size // 2, board.size // 2)]

        scored_moves = []
        grid = board.grid
        size = board.size
        center = size / 2

        for r, c in legal_moves:
            adjacency = 0

            r0 = max(0, r - 1)
            r1 = min(size - 1, r + 1)
            c0 = max(0, c - 1)
            c1 = min(size - 1, c + 1)

            for nr in range(r0, r1 + 1):
                row = grid[nr]
                for nc in range(c0, c1 + 1):
                    if nr == r and nc == c:
                        continue
                    if row[nc] is not None:
                        adjacency += 1

            if size >= 6 and adjacency == 0:
                continue

            dist_to_center = abs(r - center) + abs(c - center)
            move_score = adjacency * 10 - dist_to_center
            scored_moves.append((move_score, (r, c)))

        scored_moves.sort(key=lambda x: x[0], reverse=True)

        if not scored_moves:
            return legal_moves

        return [move for _, move in scored_moves]