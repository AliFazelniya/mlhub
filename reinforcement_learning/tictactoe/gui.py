"""
Modern Pygame GUI for Neicharan's Dooz.
Features Dark Mode, hover effects, and an interactive setup menu.
"""

import pygame
import sys
from typing import Tuple, Optional
from board import Board

# Modern Dark Theme Palette (Catppuccin inspired)
BG_COLOR = (30, 30, 46)        # Deep dark background
GRID_COLOR = (69, 71, 90)      # Subtle grid lines
TEXT_COLOR = (205, 214, 244)   # Soft white text
X_COLOR = (243, 139, 168)      # Pastel Red/Pink for X
O_COLOR = (137, 180, 250)      # Pastel Blue for O
BTN_BG = (49, 50, 68)          # Button background
BTN_HOVER = (88, 91, 112)      # Button hover state
BTN_ACTIVE = (166, 227, 161)   # Green for active/selected buttons
HOVER_CELL = (40, 40, 56)      # Highlight for cell hovering


class GameGUI:
    def __init__(self, board: Board):
        pygame.init()
        self.board = board
        
        self.margin = 70  # Space for labels
        self.cell_size = min(600 // self.board.size, 100)
        self.board_width = self.board.size * self.cell_size
        self.width = self.board_width + self.margin + 30
        self.height = self.board_width + self.margin + 80
        
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Tic-Tac-Toe")
        
        # Modern Fonts
        self.font = pygame.font.SysFont("segoeui", 22, bold=True)
        self.score_font = pygame.font.SysFont("segoeui", 20)

    def draw_board(self, score_x: int, score_o: int, human_mark: str, mouse_pos: Tuple[int, int]) -> None:
        self.screen.fill(BG_COLOR)
        
        # Draw Hover Effect
        hover_move = self.get_move_from_mouse(mouse_pos)
        if hover_move and self.board.grid[hover_move[0]][hover_move[1]] is None:
            r, c = hover_move
            rect = (self.margin + c * self.cell_size, self.margin + r * self.cell_size, self.cell_size, self.cell_size)
            pygame.draw.rect(self.screen, HOVER_CELL, rect)

        # Draw Labels (1, 2, 3... and a, b, c...)
        for i in range(self.board.size):
            col_text = self.font.render(str(i + 1), True, GRID_COLOR)
            col_rect = col_text.get_rect(center=(self.margin + i * self.cell_size + self.cell_size // 2, self.margin // 2 + 10))
            self.screen.blit(col_text, col_rect)
            
            row_label = chr(ord('a') + i)
            row_text = self.font.render(row_label, True, GRID_COLOR)
            row_rect = row_text.get_rect(center=(self.margin // 2 + 10, self.margin + i * self.cell_size + self.cell_size // 2))
            self.screen.blit(row_text, row_rect)

        # Draw Grid (Rounded boundaries look modern)
        board_rect = (self.margin, self.margin, self.board_width, self.board_width)
        pygame.draw.rect(self.screen, GRID_COLOR, board_rect, 3, border_radius=8)
        
        for x in range(1, self.board.size):
            pygame.draw.line(self.screen, GRID_COLOR, 
                             (self.margin + x * self.cell_size, self.margin), 
                             (self.margin + x * self.cell_size, self.margin + self.board_width), 2)
            pygame.draw.line(self.screen, GRID_COLOR, 
                             (self.margin, self.margin + x * self.cell_size), 
                             (self.margin + self.board_width, self.margin + x * self.cell_size), 2)

        # Draw Marks
        for r in range(self.board.size):
            for c in range(self.board.size):
                if self.board.grid[r][c] == 'X':
                    self._draw_x(r, c)
                elif self.board.grid[r][c] == 'O':
                    self._draw_o(r, c)
                    
        # Draw Scores with dynamic colors based on who the human is
        you_str = "You" if human_mark == 'X' else "AI"
        ai_str = "AI" if human_mark == 'X' else "You"
        
        score_text_x = self.score_font.render(f"X ({you_str}): {score_x}", True, X_COLOR)
        score_text_o = self.score_font.render(f"O ({ai_str}): {score_o}", True, O_COLOR)
        
        self.screen.blit(score_text_x, (self.margin, self.height - 50))
        self.screen.blit(score_text_o, (self.width - self.margin - score_text_o.get_width(), self.height - 50))

        pygame.display.update()

    def _draw_x(self, row: int, col: int) -> None:
        padding = self.cell_size // 3.5
        left = self.margin + col * self.cell_size + padding
        top = self.margin + row * self.cell_size + padding
        right = self.margin + (col + 1) * self.cell_size - padding
        bottom = self.margin + (row + 1) * self.cell_size - padding
        
        pygame.draw.line(self.screen, X_COLOR, (left, top), (right, bottom), 6)
        pygame.draw.line(self.screen, X_COLOR, (left, bottom), (right, top), 6)

    def _draw_o(self, row: int, col: int) -> None:
        center = (
            self.margin + col * self.cell_size + self.cell_size // 2,
            self.margin + row * self.cell_size + self.cell_size // 2
        )
        radius = self.cell_size // 2 - self.cell_size // 4
        pygame.draw.circle(self.screen, O_COLOR, center, radius, 5)

    def get_move_from_mouse(self, mouse_pos: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        x, y = mouse_pos
        if x < self.margin or y < self.margin or x >= self.margin + self.board_width or y >= self.margin + self.board_width:
            return None
        col = (x - self.margin) // self.cell_size
        row = (y - self.margin) // self.cell_size
        return row, col


def draw_button(screen, rect, text, font, base_color, hover_color, mouse_pos, is_active=False):
    """Helper to draw modern buttons."""
    is_hovered = pygame.Rect(rect).collidepoint(mouse_pos)
    color = BTN_ACTIVE if is_active else (hover_color if is_hovered else base_color)
    pygame.draw.rect(screen, color, rect, border_radius=10)
    
    text_surf = font.render(text, True, BG_COLOR if is_active else TEXT_COLOR)
    text_rect = text_surf.get_rect(center=pygame.Rect(rect).center)
    screen.blit(text_surf, text_rect)
    return is_hovered


def prompt_setup() -> Tuple[int, str]:
    """Interactive GUI setup menu to choose board size and player mark."""
    pygame.init()
    screen = pygame.display.set_mode((450, 400))
    pygame.display.set_caption("Game Setup")
    
    font_title = pygame.font.SysFont("segoeui", 32, bold=True)
    font_main = pygame.font.SysFont("segoeui", 22)
    
    board_size = 5
    human_mark = 'X'
    
    # UI Elements Rects
    btn_minus = (130, 120, 50, 50)
    btn_plus = (270, 120, 50, 50)
    btn_x = (100, 230, 100, 50)
    btn_o = (250, 230, 100, 50)
    btn_start = (125, 320, 200, 50)

    while True:
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.Rect(btn_minus).collidepoint(mouse_pos) and board_size > 3:
                    board_size -= 1
                elif pygame.Rect(btn_plus).collidepoint(mouse_pos) and board_size < 10:
                    board_size += 1
                elif pygame.Rect(btn_x).collidepoint(mouse_pos):
                    human_mark = 'X'
                elif pygame.Rect(btn_o).collidepoint(mouse_pos):
                    human_mark = 'O'
                elif pygame.Rect(btn_start).collidepoint(mouse_pos):
                    return board_size, human_mark

        screen.fill(BG_COLOR)
        
        # Titles
        title_surf = font_title.render("Game Setup", True, TEXT_COLOR)
        screen.blit(title_surf, title_surf.get_rect(center=(225, 40)))
        
        size_lbl = font_main.render("Board Size", True, TEXT_COLOR)
        screen.blit(size_lbl, size_lbl.get_rect(center=(225, 95)))
        
        role_lbl = font_main.render("Play As", True, TEXT_COLOR)
        screen.blit(role_lbl, role_lbl.get_rect(center=(225, 200)))

        # Controls
        draw_button(screen, btn_minus, "-", font_title, BTN_BG, BTN_HOVER, mouse_pos)
        draw_button(screen, btn_plus, "+", font_title, BTN_BG, BTN_HOVER, mouse_pos)
        
        size_val = font_title.render(str(board_size), True, TEXT_COLOR)
        screen.blit(size_val, size_val.get_rect(center=(225, 145)))

        draw_button(screen, btn_x, "X", font_title, BTN_BG, BTN_HOVER, mouse_pos, is_active=(human_mark == 'X'))
        draw_button(screen, btn_o, "O", font_title, BTN_BG, BTN_HOVER, mouse_pos, is_active=(human_mark == 'O'))
        
        draw_button(screen, btn_start, "START GAME", font_main, BTN_BG, BTN_ACTIVE, mouse_pos)
        
        pygame.display.update()


def show_game_over(score_x: int, score_o: int, human_mark: str):
    pygame.init()
    screen = pygame.display.set_mode((450, 300))
    pygame.display.set_caption("Game Over")
    
    font_large = pygame.font.SysFont("segoeui", 36, bold=True)
    font_small = pygame.font.SysFont("segoeui", 22)

    human_score = score_x if human_mark == 'X' else score_o
    ai_score = score_o if human_mark == 'X' else score_x

    if human_score > ai_score:
        msg = "Victory!"
        color = BTN_ACTIVE
    elif ai_score > human_score:
        msg = "Defeat!"
        color = X_COLOR
    else:
        msg = "It's a Tie!"
        color = O_COLOR

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
                pygame.quit()
                sys.exit()

        screen.fill(BG_COLOR)
        
        title_surf = font_large.render(msg, True, color)
        screen.blit(title_surf, title_surf.get_rect(center=(225, 60)))
        
        h_surf = font_small.render(f"Your Score: {human_score}", True, TEXT_COLOR)
        a_surf = font_small.render(f"Agent Score: {ai_score}", True, TEXT_COLOR)
        exit_surf = font_small.render("Press any key to exit...", True, GRID_COLOR)
        
        screen.blit(h_surf, h_surf.get_rect(center=(225, 130)))
        screen.blit(a_surf, a_surf.get_rect(center=(225, 170)))
        screen.blit(exit_surf, exit_surf.get_rect(center=(225, 240)))
        
        pygame.display.update()
