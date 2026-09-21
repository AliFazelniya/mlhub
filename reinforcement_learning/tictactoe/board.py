from typing import List, Tuple, Optional
import copy


class Board:
    def __init__(self, size: int):
        
        self.size = size
        self.grid: List[List[Optional[str]]] = [[None for _ in range(size)] for _ in range(size)]

    def is_full(self) -> bool:
        return all(cell is not None for row in self.grid for cell in row)

    def get_legal_moves(self) -> List[Tuple[int, int]]:
        return [(r, c) for r in range(self.size) for c in range(self.size) if self.grid[r][c] is None]

    def make_move(self, row: int, col: int, player: str) -> bool:

        if 0 <= row < self.size and 0 <= col < self.size and self.grid[row][col] is None:
            self.grid[row][col] = player
            return True
        return False

    def undo_move(self, row: int, col: int) -> None:
        self.grid[row][col] = None

    def clone(self) -> 'Board':
        new_board = Board(self.size)
        new_board.grid = copy.deepcopy(self.grid)
        return new_board

    def calculate_scores(self) -> Tuple[int, int]:
        score_x = 0
        score_o = 0
        
        for line in self._get_all_lines():
            score_x += self._score_line(line, 'X')
            score_o += self._score_line(line, 'O')
            
        return score_x, score_o
    
    def _score_line(self, line: List[Optional[str]], player: str) -> int:
            total_score = 0
            consecutive = 0
            
            for cell in line:
                if cell == player:
                    consecutive += 1
                else:
                    if consecutive >= 3:
                        total_score += self._calculate_run_score(consecutive)
                    consecutive = 0
                    
            if consecutive >= 3:
                total_score += self._calculate_run_score(consecutive)
                
            return total_score

    def _calculate_run_score(self, n: int) -> int:
        if n < 3:
            return 0
            
        base_score = n - 2
        extra_marks = n - 3
        points_per_extra_mark = n - 3
        
        total_extra_score = extra_marks * points_per_extra_mark
        
        return base_score + total_extra_score

    def _get_all_lines(self) -> List[List[Optional[str]]]:
        lines = []
        
        for row in self.grid:
            lines.append(row)
            
        for c in range(self.size):
            lines.append([self.grid[r][c] for r in range(self.size)])
            
        for d in range(-self.size + 1, self.size):
            diag = [self.grid[i][i - d] for i in range(self.size) if 0 <= i - d < self.size]
            if len(diag) >= 3:
                lines.append(diag)
                
        for d in range(2 * self.size - 1):
            diag = [self.grid[i][d - i] for i in range(self.size) if 0 <= d - i < self.size]
            if len(diag) >= 3:
                lines.append(diag)
                
        return lines
