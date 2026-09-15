"""
Advanced AI Agent Module using Minimax with Alpha-Beta Pruning.
Includes Proximity Pruning and Move Ordering for large boards.
"""

import math
from typing import Tuple, List, Optional
from board import Board


class MinimaxAI:
    def __init__(self, ai_player: str = 'O', human_player: str = 'X'):
        self.ai = ai_player
        self.human = human_player

    def get_best_move(self, board: Board) -> Optional[Tuple[int, int]]:
        """Determine the optimal move using depth-limited Minimax."""
        # Use our new smart move generator instead of raw legal moves
        smart_moves = self._get_smart_moves(board)
        if not smart_moves:
            return None

        depth_limit = self._calculate_dynamic_depth(board.size, len(board.get_legal_moves()))
        
        best_val = -math.inf
        best_move = None
        
        for r, c in smart_moves:
            board.make_move(r, c, self.ai)
            move_val = self._minimax(board, depth_limit - 1, -math.inf, math.inf, False)
            board.undo_move(r, c)
            
            if move_val > best_val:
                best_val = move_val
                best_move = (r, c)
                
        return best_move

    def _minimax(self, board: Board, depth: int, alpha: float, beta: float, is_maximizing: bool) -> float:
        """Core Minimax algorithm with Alpha-Beta pruning."""
        if depth == 0 or board.is_full():
            return self._evaluate_board(board)

        smart_moves = self._get_smart_moves(board)

        if is_maximizing:
            max_eval = -math.inf
            for r, c in smart_moves:
                board.make_move(r, c, self.ai)
                eval = self._minimax(board, depth - 1, alpha, beta, False)
                board.undo_move(r, c)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = math.inf
            for r, c in smart_moves:
                board.make_move(r, c, self.human)
                eval = self._minimax(board, depth - 1, alpha, beta, True)
                board.undo_move(r, c)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval

    def _evaluate_board(self, board: Board) -> float:
        """Heuristic evaluation function based on exact score differences."""
        score_x, score_o = board.calculate_scores()
        if self.ai == 'O':
            return score_o - score_x
        return score_x - score_o

    def _calculate_dynamic_depth(self, board_size: int, empty_cells: int) -> int:
        """Adjust depth dynamically. Thanks to pruning, we can look deeper!"""
        if board_size <= 4:
            return min(6, empty_cells)
        elif board_size <= 6:
            return min(5, empty_cells)
        else:
            # 🌟 Increased from 3 to 4 for large boards! AI is now much smarter.
            return min(4, empty_cells)

    def _get_smart_moves(self, board: Board) -> List[Tuple[int, int]]:
        """
        Move Ordering & Proximity Pruning:
        Generates a sorted list of strategic moves to drastically reduce the Minimax branching factor.
        """
        legal_moves = board.get_legal_moves()
        
        # Rule 1: If board is completely empty, strictly play in the center
        if len(legal_moves) == board.size * board.size:
            return [(board.size // 2, board.size // 2)]
            
        scored_moves = []
        center_r, center_c = board.size / 2, board.size / 2
        
        for r, c in legal_moves:
            adjacency = 0
            # Check the 8 neighboring cells
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < board.size and 0 <= nc < board.size:
                        if board.grid[nr][nc] is not None:
                            adjacency += 1
                            
            # Rule 2: Proximity Pruning. On large boards, completely ignore isolated empty cells.
            if board.size >= 6 and adjacency == 0:
                continue
                
            # Rule 3: Move Ordering. Prioritize cells with more neighbors, tie-breaking with center distance.
            dist_to_center = abs(r - center_r) + abs(c - center_c)
            move_score = (adjacency * 10) - dist_to_center
            
            scored_moves.append((move_score, (r, c)))
            
        # Sort by best score descending (Alpha-Beta works best when good moves are evaluated first)
        scored_moves.sort(key=lambda x: x[0], reverse=True)
        
        # Fallback: if pruning accidentally removes all moves (extremely rare edge case)
        if not scored_moves:
            return legal_moves
            
        # Return only the coordinates
        return [move for score, move in scored_moves]
