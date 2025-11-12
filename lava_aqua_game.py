import os
import sys
from collections import deque

# Game symbols
EMPTY = '.'
WALL = '#'
PLAYER = 'P'
WATER = 'W'
LAVA = 'L'
MOVABLE = 'M'
GOAL = 'G'
BARRIER = '*'  # Water/lava pass through, player can't
PURPLE = 'C'   # Collectible point
TIMED = 'T'    # Timed block format: T:5 (disappears after 5 moves)

# ANSI color codes for better visualization
COLORS = {
    EMPTY: '\033[90m',      # Gray
    WALL: '\033[37m',       # White
    PLAYER: '\033[92m',     # Bright Green
    WATER: '\033[94m',      # Blue
    LAVA: '\033[91m',       # Red
    MOVABLE: '\033[93m',    # Yellow
    GOAL: '\033[95m',       # Magenta
    BARRIER: '\033[96m',    # Cyan
    PURPLE: '\033[35m',     # Purple
    TIMED: '\033[33m',      # Orange
    'RESET': '\033[0m'
}

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
        self.timed_blocks = {}  # (row, col): TimedBlock
        
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
                    # Parse timed block (e.g., T:5)
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
            return False  # Goal is locked until all purple collected
        return True
    
    def can_liquid_spread(self, row, col):
        """Check if water/lava can spread to this position"""
        if not self.is_in_bounds(row, col):
            return False
        cell = self.grid[row][col]
        # Liquids can't pass through walls, movable blocks, or timed blocks
        if cell in [WALL, MOVABLE, TIMED]:
            return False
        return True
    
    def move_player(self, direction):
        """Move player in given direction (up, down, left, right)"""
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
            # Calculate position behind the movable block
            push_row = new_row + (new_row - row)
            push_col = new_col + (new_col - col)
            
            # Check if we can push the block
            if self.is_in_bounds(push_row, push_col):
                target_cell = self.grid[push_row][push_col]
                # Can push if target is empty and no liquid
                if target_cell == EMPTY and not self.water[push_row][push_col] and not self.lava[push_row][push_col]:
                    # Move the block
                    self.grid[new_row][new_col] = EMPTY
                    self.grid[push_row][push_col] = MOVABLE
                    self.movable_blocks.remove((new_row, new_col))
                    self.movable_blocks.add((push_row, push_col))
                    # Player moves to where block was
                    self.player_pos = (new_row, new_col)
                    self.move_count += 1
                    self.after_move()
                    return
            return  # Can't push, no move
        
        # Normal movement
        if self.can_player_move(new_row, new_col):
            self.player_pos = (new_row, new_col)
            
            # Check for purple collectible
            if self.grid[new_row][new_col] == PURPLE:
                self.purple_collected += 1
                self.grid[new_row][new_col] = EMPTY
            
            # Check for goal
            if self.grid[new_row][new_col] == GOAL and self.purple_collected >= self.purple_total:
                self.won = True
                self.game_over = True
                return
            
            self.move_count += 1
            self.after_move()
    
    def after_move(self):
        """Actions that happen after each move"""
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
        # Find all current water positions
        water_positions = []
        for row in range(self.height):
            for col in range(self.width):
                if self.water[row][col]:
                    water_positions.append((row, col))
        
        # Find all current lava positions
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
            # Water neutralizes lava (or you can make lava override water)
            if self.water[row][col]:
                # Optional: make them cancel out or lava wins
                self.lava[row][col] = True
            else:
                self.lava[row][col] = True
    
    def render(self):
        """Display the game board"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print(f"\n=== LAVA & AQUA PUZZLE ===")
        print(f"Moves: {self.move_count} | Purple Collected: {self.purple_collected}/{self.purple_total}")
        print()
        
        for row in range(self.height):
            line = ""
            for col in range(self.width):
                # Player position
                if (row, col) == self.player_pos:
                    line += COLORS[PLAYER] + PLAYER + COLORS['RESET']
                # Lava (higher priority than water)
                elif self.lava[row][col]:
                    line += COLORS[LAVA] + LAVA + COLORS['RESET']
                # Water
                elif self.water[row][col]:
                    line += COLORS[WATER] + WATER + COLORS['RESET']
                # Regular grid
                else:
                    cell = self.grid[row][col]
                    if cell == TIMED:
                        # Show remaining turns
                        turns = self.timed_blocks.get((row, col)).turns_remaining
                        line += COLORS[TIMED] + str(turns) + COLORS['RESET']
                    else:
                        line += COLORS.get(cell, '') + cell + COLORS['RESET']
                line += ' '
            print(line)
        
        print("\nControls: W=Up, S=Down, A=Left, D=Right, Q=Quit")
        
        if self.goal_pos:
            goal_status = "UNLOCKED" if self.purple_collected >= self.purple_total else "LOCKED"
            print(f"Goal Status: {goal_status}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python lava_aqua_game.py <map_file>")
        print("\nExample: python lava_aqua_game.py level1.txt")
        sys.exit(1)
    
    map_file = sys.argv[1]
    
    if not os.path.exists(map_file):
        print(f"Error: Map file '{map_file}' not found!")
        sys.exit(1)
    
    try:
        game = GameState(map_file)
    except Exception as e:
        print(f"Error loading map: {e}")
        sys.exit(1)
    
    # Game loop
    while not game.game_over:
        game.render()
        
        # Get input
        command = input("\nYour move: ").strip().lower()
        
        if command == 'q':
            print("Thanks for playing!")
            break
        elif command == 'w':
            game.move_player('up')
        elif command == 's':
            game.move_player('down')
        elif command == 'a':
            game.move_player('left')
        elif command == 'd':
            game.move_player('right')
        else:
            print("Invalid command! Use W/A/S/D to move, Q to quit.")
            input("Press Enter to continue...")
    
    # Game over
    game.render()
    print()
    if game.won:
        print("🎉 CONGRATULATIONS! You reached the goal!")
        print(f"Total moves: {game.move_count}")
    else:
        print("💀 GAME OVER! You were consumed by lava!")
        print(f"Total moves: {game.move_count}")

if __name__ == "__main__":
    main()

