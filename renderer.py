
import pygame
import math
from config import *


class Renderer:
    def __init__(self, game_engine):
        self.game = game_engine
        
        self.board_width = self.game.width * TILE_SIZE
        self.board_height = self.game.height * TILE_SIZE
        self.window_width = self.board_width
        self.window_height = self.board_height + UI_HEIGHT
        
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption("Lava & Aqua Puzzle Game")
        
        self.font_large = pygame.font.Font(None, 36)
        self.font_medium = pygame.font.Font(None, 28)
        self.font_small = pygame.font.Font(None, 20)
    
    def draw_frame(self):
        self._draw_game_board()
        self._draw_user_interface()
        
        if self.game.game_over:
            self._draw_game_over_screen()
        
        pygame.display.flip()
    
    def _draw_game_board(self):
        board_surface = pygame.Surface((self.board_width, self.board_height))
        board_surface.fill(COLORS['bg'])
        
        for row in range(self.game.height):
            for col in range(self.game.width):
                self._draw_single_tile(row, col, board_surface)
        
        self.screen.blit(board_surface, (0, 0))
    
    def _draw_single_tile(self, row, col, surface):
        x = col * TILE_SIZE
        y = row * TILE_SIZE
        rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
        cell = self.game.grid[row][col]
        
        pygame.draw.rect(surface, COLORS['empty'], rect)
        
        if self._is_player_here(row, col):
            self._draw_player(rect, surface)
        elif self._is_lava_here(row, col):
            if cell == BARRIER:
                self._draw_lava_over_barrier(rect, surface)
            else:
                self._draw_lava(rect, surface)
        elif self._is_water_here(row, col):
            if cell == BARRIER:
                self._draw_water_over_barrier(rect, surface)
            else:
                self._draw_water(rect, surface)
        else:
            self._draw_static_tile(row, col, rect, surface)
        
        pygame.draw.rect(surface, (40, 40, 40), rect, 1)
    
    def _is_player_here(self, row, col):
        return (row, col) == self.game.player_pos
    
    def _is_lava_here(self, row, col):
        return self.game.lava[row][col] and not self.game.grid[row][col] == WALL
    
    def _is_water_here(self, row, col):
        return self.game.water[row][col]
    
    def _draw_player(self, rect, surface):
        pygame.draw.rect(surface, COLORS['player'], rect)
        pygame.draw.circle(surface, (0, 0, 0), rect.center, TILE_SIZE // 4)
    
    def _draw_lava(self, rect, surface):
        pygame.draw.rect(surface, COLORS['lava'], rect)
    
    def _draw_water(self, rect, surface):
        pygame.draw.rect(surface, COLORS['water'], rect)
    
    def _draw_lava_over_barrier(self, rect, surface):
        pygame.draw.rect(surface, COLORS['lava'], rect)
        pygame.draw.line(surface, (255, 255, 255), rect.topleft, rect.bottomright, 5)
        pygame.draw.line(surface, (255, 255, 255), rect.topright, rect.bottomleft, 5)
    
    def _draw_water_over_barrier(self, rect, surface):
        pygame.draw.rect(surface, COLORS['water'], rect)
        pygame.draw.line(surface, COLORS['barrier'], rect.topleft, rect.bottomright, 5)
        pygame.draw.line(surface, COLORS['barrier'], rect.topright, rect.bottomleft, 5)
    
    def _draw_static_tile(self, row, col, rect, surface):
        cell = self.game.grid[row][col]
        
        if cell == WALL:
            pygame.draw.rect(surface, COLORS['wall'], rect)
            
        elif cell == GOAL:
            pygame.draw.rect(surface, COLORS['goal'], rect)
            self._draw_star(rect.center, TILE_SIZE // 3, surface)
            
        elif cell == PURPLE:
            pygame.draw.rect(surface, COLORS['empty'], rect)
            pygame.draw.circle(surface, COLORS['purple'], rect.center, TILE_SIZE // 3)
            
        elif cell == MOVABLE:
            pygame.draw.rect(surface, COLORS['movable'], rect)
            pygame.draw.rect(surface, (0, 0, 0), rect, 2)
            
        elif cell == BARRIER:
            pygame.draw.rect(surface, COLORS['empty'], rect)
            pygame.draw.line(surface, COLORS['barrier'], rect.topleft, rect.bottomright, 5)
            pygame.draw.line(surface, COLORS['barrier'], rect.topright, rect.bottomleft, 5)
            
        elif cell == TIMED:
            pygame.draw.rect(surface, COLORS['timed'], rect)
            timed_block = self.game.timed_blocks.get((row, col))
            if timed_block:
                text = self.font_small.render(str(timed_block.turns_remaining), True, (0, 0, 0))
                surface.blit(text, text.get_rect(center=rect.center))
    
    def _draw_star(self, center, size, surface):
        points = []
        for i in range(10):
            angle = i * math.pi / 5
            radius = size if i % 2 == 0 else size / 2
            x = center[0] + radius * math.cos(angle - math.pi / 2)
            y = center[1] + radius * math.sin(angle - math.pi / 2)
            points.append((x, y))
        
        if len(points) > 2:
            pygame.draw.polygon(surface, (255, 255, 255), points)
    
    def _draw_user_interface(self):
        ui_rect = pygame.Rect(0, self.board_height, self.window_width, UI_HEIGHT)
        pygame.draw.rect(self.screen, (40, 40, 40), ui_rect)
        
        pygame.draw.line(self.screen, (100, 100, 100), 
                        (0, self.board_height), 
                        (self.window_width, self.board_height), 2)
        
        y_pos = self.board_height + 10
        
        moves_text = self.font_medium.render(f"Moves: {self.game.move_count}", True, COLORS['text'])
        self.screen.blit(moves_text, (20, y_pos))


        purple_color = COLORS['purple'] if self.game.purple_collected == self.game.purple_total else COLORS['text']
        purple_text = self.font_medium.render(
            f"Purple: {self.game.purple_collected}/{self.game.purple_total}", 
            True, purple_color
        )
        self.screen.blit(purple_text, (self.window_width // 2 - 100, y_pos))
        
        goal_unlocked = self.game.is_goal_unlocked()
        goal_color = (0, 255, 0) if goal_unlocked else (200, 100, 100)
        goal_status = "UNLOCKED" if goal_unlocked else "LOCKED"
        goal_text = self.font_small.render(f"Goal: {goal_status}", True, goal_color)
        self.screen.blit(goal_text, (self.window_width - 200, y_pos))
        
        controls_text = self.font_small.render(f"WASD/Arrows: Move | Q: Quit | R: Restart | G: Solve game | Z: Undo", True, (150, 150, 150))
        self.screen.blit(controls_text, (20, y_pos + 35))

        moves_text = self.font_small.render(f"Available moves: {', '.join(map(str, self.game.get_valid_moves()))}", True, (150, 150, 150))
        self.screen.blit(moves_text, (20, y_pos + 55))
            
    def _draw_game_over_screen(self):
        overlay = pygame.Surface((self.window_width, self.board_height))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        if self.game.won:
            title = self.font_large.render("YOU WIN!", True, (0, 255, 0))
            message = self.font_medium.render(
                f"Completed in {self.game.move_count} moves", 
                True, COLORS['text']
            )
        else:
            title = self.font_large.render("GAME OVER!", True, (255, 0, 0))
            message = self.font_medium.render("Consumed by lava!", True, COLORS['text'])
        
        restart_text = self.font_small.render(
            "Press R to restart or Q to quit", 
            True, (200, 200, 200)
        )
        
        center_x = self.window_width // 2
        center_y = self.board_height // 2
        
        title_rect = title.get_rect(center=(center_x, center_y - 40))
        message_rect = message.get_rect(center=(center_x, center_y + 20))
        restart_rect = restart_text.get_rect(center=(center_x, center_y + 70))
        
        self.screen.blit(title, title_rect)
        self.screen.blit(message, message_rect)
        self.screen.blit(restart_text, restart_rect)
