import pygame
import sys
import os
from collections import deque

# Initialize Pygame
pygame.init()

# Game symbols
EMPTY = '.'
WALL = '#'
PLAYER = 'P'
WATER = 'W'
LAVA = 'L'
MOVABLE = 'M'
GOAL = 'G'
BARRIER = '*'
PURPLE = 'C'
TIMED = 'T'

# Colors
COLORS = {
    'bg': (20, 20, 20),
    'empty': (50, 50, 50),
    'wall': (100, 100, 100),
    'player': (0, 255, 0),
    'water': (0, 100, 255),
    'lava': (255, 50, 50),
    'movable': (255, 255, 0),
    'goal': (255, 0, 255),
    'barrier': (0, 255, 255),
    'purple': (200, 100, 255),
    'timed': (255, 150, 0),
    'text': (255, 255, 255),
}

# Tile size
TILE_SIZE = 40
UI_HEIGHT = 100

class TimedBlock:
    def __init__(self, turns_remaining):
        self.turns_remaining = turns_remaining
    
    def tick(self):
        self.turns_remaining -= 1
        return self.turns_remaining <= 0

class GameState:
    def __init__(self, map_file):
        self.load_map(map_file)
        self.move_count = 0
        self.purple_collected = 0
        self.game_over = False
        self.won = False
        
    def load_map(self, map_file):
        """Load map from text file"""
        with open(map_file, 'r') as f:
            lines = f.readlines()
        
        # Parse map
        self.height = len(lines)
        self.width = max(len(line.rstrip()) for line in lines)
        
        # Initialize grids
        self.grid = [[EMPTY for _ in range(self.width)] for _ in range(self.height)]
        self.water = [[False for _ in range(self.width)] for _ in range(self.height)]
        self.lava = [[False for _ in range(self.width)] for _ in range(self.height)]
        self.timed_blocks = {}
        
        self.player_pos = None
        self.goal_pos = None
        self.purple_total = 0
        self.movable_blocks = set()
        
        for row, line in enumerate(lines):
            for col, char in enumerate(line.rstrip()):
                if char == PLAYER:
                    self.player_pos = (row, col)
                    self.grid[row][col] = EMPTY
                elif char == WATER:
                    self.water[row][col] = True
                    self.grid[row][col] = EMPTY
                elif char == LAVA:
                    self.lava[row][col] = True
                    self.grid[row][col] = EMPTY
                elif char == GOAL:
                    self.goal_pos = (row, col)
                    self.grid[row][col] = GOAL
                elif char == PURPLE:
                    self.grid[row][col] = PURPLE
                    self.purple_total += 1
                elif char == MOVABLE:
                    self.grid[row][col] = MOVABLE
                    self.movable_blocks.add((row, col))
                elif char.startswith('T'):
                    parts = char.split(':')
                    turns = int(parts[1]) if len(parts) > 1 else 3
                    self.timed_blocks[(row, col)] = TimedBlock(turns)
                    self.grid[row][col] = TIMED
                else:
                    self.grid[row][col] = char
        
        if self.player_pos is None:
            raise ValueError("Map must contain a player starting position (P)")
    
    def is_in_bounds(self, row, col):
        return 0 <= row < self.height and 0 <= col < self.width
    
    def can_player_move(self, row, col):
        """Check if player can move to this position"""
        if not self.is_in_bounds(row, col):
            return False
        cell = self.grid[row][col]
        if cell in [WALL, BARRIER]:
            return False
        if cell == GOAL and self.purple_collected < self.purple_total:
            return False
        return True
    
    def can_liquid_spread(self, row, col):
        """Check if water/lava can spread to this position"""
        if not self.is_in_bounds(row, col):
            return False
        cell = self.grid[row][col]
        if cell in [WALL, MOVABLE, TIMED,GOAL,MOVABLE,PURPLE]:
            return False
        return True
    
    def move_player(self, direction):
        """Move player in given direction"""
        if self.game_over:
            return
        
        row, col = self.player_pos
        new_row, new_col = row, col
        
        if direction == 'up':
            new_row -= 1
        elif direction == 'down':
            new_row += 1
        elif direction == 'left':
            new_col -= 1
        elif direction == 'right':
            new_col += 1
        
        # Check if trying to push a movable block
        if self.is_in_bounds(new_row, new_col) and self.grid[new_row][new_col] == MOVABLE:
            push_row = new_row + (new_row - row)
            push_col = new_col + (new_col - col)
            
            if self.is_in_bounds(push_row, push_col):
                target_cell = self.grid[push_row][push_col]
                if target_cell == EMPTY and not self.water[push_row][push_col] and not self.lava[push_row][push_col]:
                    self.grid[new_row][new_col] = EMPTY
                    self.grid[push_row][push_col] = MOVABLE
                    self.movable_blocks.remove((new_row, new_col))
                    self.movable_blocks.add((push_row, push_col))
                    self.player_pos = (new_row, new_col)
                    self.move_count += 1
                    self.after_move()
                    return
            return
        
        # Normal movement
        if self.can_player_move(new_row, new_col):
            self.player_pos = (new_row, new_col)
            
            if self.grid[new_row][new_col] == PURPLE:
                self.purple_collected += 1
                self.grid[new_row][new_col] = EMPTY
            
            if self.grid[new_row][new_col] == GOAL and self.purple_collected >= self.purple_total:
                self.won = True
                self.game_over = True
                return
            
            self.move_count += 1
            self.after_move()
    
    def after_move(self):
        """Actions after each move"""
        # Update timed blocks
        expired_blocks = []
        for pos, timed_block in self.timed_blocks.items():
            if timed_block.tick():
                expired_blocks.append(pos)
        
        for pos in expired_blocks:
            row, col = pos
            self.grid[row][col] = EMPTY
            del self.timed_blocks[pos]
        
        # Spread liquids
        self.spread_liquids()
        
        # Check if player is in lava
        p_row, p_col = self.player_pos
        if self.lava[p_row][p_col]:
            self.game_over = True
            self.won = False
    
    def spread_liquids(self):
        """Spread water and lava to adjacent cells"""
        water_positions = []
        for row in range(self.height):
            for col in range(self.width):
                if self.water[row][col]:
                    water_positions.append((row, col))
        
        lava_positions = []
        for row in range(self.height):
            for col in range(self.width):
                if self.lava[row][col]:
                    lava_positions.append((row, col))
        
        # Spread water
        new_water = set()
        for row, col in water_positions:
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                new_row, new_col = row + dr, col + dc
                if self.can_liquid_spread(new_row, new_col):
                    new_water.add((new_row, new_col))
        
        for row, col in new_water:
            self.water[row][col] = True
        
        # Spread lava
        new_lava = set()
        for row, col in lava_positions:
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                new_row, new_col = row + dr, col + dc
                if self.can_liquid_spread(new_row, new_col):
                    new_lava.add((new_row, new_col))
        
        for row, col in new_lava:
            self.lava[row][col] = True

class GameGUI:
    def __init__(self, map_file):
        self.game = GameState(map_file)
        
        # Calculate window size
        self.board_width = self.game.width * TILE_SIZE
        self.board_height = self.game.height * TILE_SIZE
        self.window_width = self.board_width
        self.window_height = self.board_height + UI_HEIGHT
        
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption("Lava & Aqua Puzzle Game")
        
        self.font_large = pygame.font.Font(None, 36)
        self.font_medium = pygame.font.Font(None, 28)
        self.font_small = pygame.font.Font(None, 20)
        
        self.clock = pygame.time.Clock()
        self.running = True
    
    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w or event.key == pygame.K_UP:
                    self.game.move_player('up')
                elif event.key == pygame.K_s or event.key == pygame.K_DOWN:
                    self.game.move_player('down')
                elif event.key == pygame.K_a or event.key == pygame.K_LEFT:
                    self.game.move_player('left')
                elif event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                    self.game.move_player('right')
                elif event.key == pygame.K_q:
                    self.running = False
                elif event.key == pygame.K_r:
                    # Restart
                    map_file = sys.argv[1] if len(sys.argv) > 1 else "level1.txt"
                    self.game = GameState(map_file)
    
    def draw_tile(self, row, col, surface):
        """Draw a single tile"""
        x = col * TILE_SIZE
        y = row * TILE_SIZE
        rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
        
        # Draw background
        pygame.draw.rect(surface, COLORS['empty'], rect)
        
        # Check what to draw on this tile
        if (row, col) == self.game.player_pos:
            pygame.draw.rect(surface, COLORS['player'], rect)
            pygame.draw.circle(surface, (0, 0, 0), rect.center, TILE_SIZE // 4)
        elif self.game.lava[row][col]:
            pygame.draw.rect(surface, COLORS['lava'], rect)
        elif self.game.water[row][col]:
            pygame.draw.rect(surface, COLORS['water'], rect)
        else:
            cell = self.game.grid[row][col]
            if cell == WALL:
                pygame.draw.rect(surface, COLORS['wall'], rect)
            elif cell == GOAL:
                pygame.draw.rect(surface, COLORS['goal'], rect)
                # Draw star
                self.draw_star(rect.center, TILE_SIZE // 3, surface)
            elif cell == PURPLE:
                pygame.draw.rect(surface, COLORS['empty'], rect)
                pygame.draw.circle(surface, COLORS['purple'], rect.center, TILE_SIZE // 3)
            elif cell == MOVABLE:
                pygame.draw.rect(surface, COLORS['movable'], rect)
                pygame.draw.rect(surface, (0, 0, 0), rect, 2)
            elif cell == BARRIER:
                pygame.draw.rect(surface, COLORS['empty'], rect)
                pygame.draw.line(surface, COLORS['barrier'], rect.topleft, rect.bottomright, 2)
                pygame.draw.line(surface, COLORS['barrier'], rect.topright, rect.bottomleft, 2)
            elif cell == TIMED:
                pygame.draw.rect(surface, COLORS['timed'], rect)
                timed = self.game.timed_blocks.get((row, col))
                if timed:
                    text = self.font_small.render(str(timed.turns_remaining), True, (0, 0, 0))
                    surface.blit(text, text.get_rect(center=rect.center))
        
        # Draw grid
        pygame.draw.rect(surface, (40, 40, 40), rect, 1)
    
    def draw_star(self, center, size, surface):
        """Draw a star shape"""
        import math
        points = []
        for i in range(10):
            angle = i * math.pi / 5
            if i % 2 == 0:
                r = size
            else:
                r = size / 2
            x = center[0] + r * math.cos(angle - math.pi / 2)
            y = center[1] + r * math.sin(angle - math.pi / 2)
            points.append((x, y))
        if len(points) > 2:
            pygame.draw.polygon(surface, (255, 255, 255), points)
    
    def draw_board(self):
        """Draw the game board"""
        board_surface = pygame.Surface((self.board_width, self.board_height))
        board_surface.fill(COLORS['bg'])
        
        for row in range(self.game.height):
            for col in range(self.game.width):
                self.draw_tile(row, col, board_surface)
        
        self.screen.blit(board_surface, (0, 0))
    
    def draw_ui(self):
        """Draw UI panel"""
        ui_rect = pygame.Rect(0, self.board_height, self.window_width, UI_HEIGHT)
        pygame.draw.rect(self.screen, (40, 40, 40), ui_rect)
        
        # Draw separator line
        pygame.draw.line(self.screen, (100, 100, 100), (0, self.board_height), 
                        (self.window_width, self.board_height), 2)
        
        # Draw info
        y_offset = self.board_height + 10
        
        moves_text = self.font_medium.render(f"Moves: {self.game.move_count}", True, COLORS['text'])
        self.screen.blit(moves_text, (20, y_offset))
        
        purple_color = COLORS['purple'] if self.game.purple_collected == self.game.purple_total else COLORS['text']
        purple_text = self.font_medium.render(
            f"Purple: {self.game.purple_collected}/{self.game.purple_total}", 
            True, purple_color
        )
        self.screen.blit(purple_text, (self.window_width // 2 - 100, y_offset))
        
        goal_color = (0, 255, 0) if self.game.purple_collected >= self.game.purple_total else (200, 100, 100)
        goal_text = self.font_small.render("Goal: UNLOCKED" if self.game.purple_collected >= self.game.purple_total else "Goal: LOCKED", True, goal_color)
        self.screen.blit(goal_text, (self.window_width - 200, y_offset))
        
        # Controls
        controls_text = self.font_small.render("WASD: Move | Q: Quit | R: Restart", True, (150, 150, 150))
        self.screen.blit(controls_text, (20, y_offset + 35))
    
    def draw_game_over(self):
        """Draw game over screen"""
        overlay = pygame.Surface((self.window_width, self.board_height))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        if self.game.won:
            title = self.font_large.render("YOU WIN!", True, (0, 255, 0))
            message = self.font_medium.render(f"Completed in {self.game.move_count} moves", True, COLORS['text'])
        else:
            title = self.font_large.render("GAME OVER!", True, (255, 0, 0))
            message = self.font_medium.render("Consumed by lava!", True, COLORS['text'])
        
        restart_text = self.font_small.render("Press R to restart or Q to quit", True, (200, 200, 200))
        
        title_rect = title.get_rect(center=(self.window_width // 2, self.board_height // 2 - 40))
        message_rect = message.get_rect(center=(self.window_width // 2, self.board_height // 2 + 20))
        restart_rect = restart_text.get_rect(center=(self.window_width // 2, self.board_height // 2 + 70))
        
        self.screen.blit(title, title_rect)
        self.screen.blit(message, message_rect)
        self.screen.blit(restart_text, restart_rect)
    
    def run(self):
        while self.running:
            self.handle_input()
            
            # Draw everything
            self.draw_board()
            self.draw_ui()
            
            if self.game.game_over:
                self.draw_game_over()
            
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()

def main():
    if len(sys.argv) < 2:
        print("Usage: python lava_aqua_game_gui.py <map_file>")
        print("\nExample: python lava_aqua_game_gui.py level1.txt")
        sys.exit(1)
    
    map_file = sys.argv[1]
    
    if not os.path.exists(map_file):
        print(f"Error: Map file '{map_file}' not found!")
        sys.exit(1)
    
    try:
        gui = GameGUI(map_file)
        gui.run()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

