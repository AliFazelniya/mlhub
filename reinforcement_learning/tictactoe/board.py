from typing import List, Tuple, Optional


class Board:

    def __init__(self, size: int):
        self.size = size
        self.grid: List[List[Optional[str]]] = [
            [None] * size for _ in range(size)
        ]
        self._empty_cells = size * size
        self._line_coords = self._build_line_coords()

    def _build_line_coords(self):
        size = self.size
        lines = []

        for r in range(size):
            lines.append(tuple((r, c) for c in range(size)))

        for c in range(size):
            lines.append(tuple((r, c) for r in range(size)))

        for d in range(-size + 1, size):
            diag = tuple(
                (i, i - d)
                for i in range(size)
                if 0 <= i - d < size
            )
            if len(diag) >= 3:
                lines.append(diag)

        for d in range(2 * size - 1):
            diag = tuple(
                (i, d - i)
                for i in range(size)
                if 0 <= d - i < size
            )
            if len(diag) >= 3:
                lines.append(diag)

        return tuple(lines)

    def is_full(self) -> bool:
        return self._empty_cells == 0

    def get_legal_moves(self) -> List[Tuple[int, int]]:
        return [
            (r, c)
            for r in range(self.size)
            for c in range(self.size)
            if self.grid[r][c] is None
        ]

    def make_move(self, row: int, col: int, player: str) -> bool:
        if (
            0 <= row < self.size
            and 0 <= col < self.size
            and self.grid[row][col] is None
        ):
            self.grid[row][col] = player
            self._empty_cells -= 1
            return True
        return False

    def undo_move(self, row: int, col: int) -> None:
        if self.grid[row][col] is not None:
            self.grid[row][col] = None
            self._empty_cells += 1

    def clone(self) -> "Board":
        new_board = Board(self.size)
        new_board.grid = [row.copy() for row in self.grid]
        new_board._empty_cells = self._empty_cells
        return new_board

    def calculate_scores(self) -> Tuple[int, int]:
        score_x = 0
        score_o = 0
        grid = self.grid

        for coords in self._line_coords:
            consecutive_x = 0
            consecutive_o = 0

            for r, c in coords:
                cell = grid[r][c]

                if cell == 'X':
                    consecutive_x += 1
                    if consecutive_o >= 3:
                        n = consecutive_o
                        score_o += (n - 2) + (n - 3) * (n - 3)
                    consecutive_o = 0

                elif cell == 'O':
                    consecutive_o += 1
                    if consecutive_x >= 3:
                        n = consecutive_x
                        score_x += (n - 2) + (n - 3) * (n - 3)
                    consecutive_x = 0

                else:
                    if consecutive_x >= 3:
                        n = consecutive_x
                        score_x += (n - 2) + (n - 3) * (n - 3)
                    if consecutive_o >= 3:
                        n = consecutive_o
                        score_o += (n - 2) + (n - 3) * (n - 3)
                    consecutive_x = 0
                    consecutive_o = 0

            if consecutive_x >= 3:
                n = consecutive_x
                score_x += (n - 2) + (n - 3) * (n - 3)
            if consecutive_o >= 3:
                n = consecutive_o
                score_o += (n - 2) + (n - 3) * (n - 3)

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
        return base_score + extra_marks * points_per_extra_mark

    def _get_all_lines(self) -> List[List[Optional[str]]]:
        return [
            [self.grid[r][c] for r, c in coords]
            for coords in self._line_coords
        ]