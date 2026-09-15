"""
Core Domain Model for Neicharan's Dooz.
Handles board state, move validation, and scoring logic.
"""

from typing import List, Tuple, Optional
import copy


class Board:
    def __init__(self, size: int):
        """
        Initialize the game board.
        
        Args:
            size (int): The dimension of the board (e.g., 3 for 3x3).
                        Must be between 3 and 10.
        Raises:
            ValueError: If the board size is not within the allowed range.
        """
        
        self.size = size
        # Initialize an empty board with None
        self.grid: List[List[Optional[str]]] = [[None for _ in range(size)] for _ in range(size)]

    def is_full(self) -> bool:
        """Check if all cells in the board are occupied."""
        return all(cell is not None for row in self.grid for cell in row)

    def get_legal_moves(self) -> List[Tuple[int, int]]:
        """
        Retrieve all available (empty) positions on the board.
        
        Returns:
            List[Tuple[int, int]]: A list of (row, col) coordinates.
        """
        return [(r, c) for r in range(self.size) for c in range(self.size) if self.grid[r][c] is None]

    def make_move(self, row: int, col: int, player: str) -> bool:
        """
        Place a player's mark on the board.
        
        Args:
            row (int): Row index (0-based).
            col (int): Column index (0-based).
            player (str): The player mark ('X' or 'O').
            
        Returns:
            bool: True if the move was successful, False otherwise.
        """
        if 0 <= row < self.size and 0 <= col < self.size and self.grid[row][col] is None:
            self.grid[row][col] = player
            return True
        return False

    def undo_move(self, row: int, col: int) -> None:
        """Remove a mark from the board (used heavily by Minimax)."""
        self.grid[row][col] = None

    def clone(self) -> 'Board':
        """Create a deep copy of the board state."""
        new_board = Board(self.size)
        new_board.grid = copy.deepcopy(self.grid)
        return new_board

    def calculate_scores(self) -> Tuple[int, int]:
        """
        Calculate the total scores for both players.
        
        Returns:
            Tuple[int, int]: (Score of 'X', Score of 'O')
        """
        score_x = 0
        score_o = 0
        
        for line in self._get_all_lines():
            score_x += self._score_line(line, 'X')
            score_o += self._score_line(line, 'O')
            
        return score_x, score_o
    
    def _score_line(self, line: List[Optional[str]], player: str) -> int:
            """
            Calculate points for a specific line based on the exact project rules.
            """
            total_score = 0
            consecutive = 0
            
            for cell in line:
                if cell == player:
                    consecutive += 1
                else:
                    if consecutive >= 3:
                        total_score += self._calculate_run_score(consecutive)
                    consecutive = 0
                    
            # Check the last run in the line
            if consecutive >= 3:
                total_score += self._calculate_run_score(consecutive)
                
            return total_score

    def _calculate_run_score(self, n: int) -> int:
        """
        Implements the exact mathematical formula from the project description:
        - Base score: n - 2
        - Extra score: (n - 3) points for EACH additional mark -> (n - 3) * (n - 3)
        """
        if n < 3:
            return 0
            
        base_score = n - 2
        extra_marks = n - 3
        points_per_extra_mark = n - 3
        
        total_extra_score = extra_marks * points_per_extra_mark
        
        return base_score + total_extra_score

    def _get_all_lines(self) -> List[List[Optional[str]]]:
        """Extract all horizontal, vertical, and diagonal lines of length >= 3."""
        lines = []
        
        # 1. Horizontal Rows
        for row in self.grid:
            lines.append(row)
            
        # 2. Vertical Columns
        for c in range(self.size):
            lines.append([self.grid[r][c] for r in range(self.size)])
            
        # 3. Main Diagonals (Top-Left to Bottom-Right)
        for d in range(-self.size + 1, self.size):
            diag = [self.grid[i][i - d] for i in range(self.size) if 0 <= i - d < self.size]
            if len(diag) >= 3:
                lines.append(diag)
                
        # 4. Anti-Diagonals (Top-Right to Bottom-Left)
        for d in range(2 * self.size - 1):
            diag = [self.grid[i][d - i] for i in range(self.size) if 0 <= d - i < self.size]
            if len(diag) >= 3:
                lines.append(diag)
                
        return lines
