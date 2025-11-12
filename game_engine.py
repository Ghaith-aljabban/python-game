"""
Core game engine and logic
"""

from config import *
from map_loader import MapLoader


class GameEngine:
    """Manages game state and rules"""
    
    def __init__(self, map_file):
        # Load the map
        map_data = MapLoader.load_from_file(map_file)
        
        # Set up the game board
        self.width = map_data['width']
        self.height = map_data['height']
        self.grid = map_data['grid']
        self.water = map_data['water']
        self.lava = map_data['lava']
        self.timed_blocks = map_data['timed_blocks']
        self.movable_blocks = map_data['movable_blocks']
        
        # Set up game entities
        self.player_pos = map_data['player_pos']
        self.goal_pos = map_data['goal_pos']
        self.purple_total = map_data['purple_total']
        
        # Game state
        self.move_count = 0
        self.purple_collected = 0
        self.game_over = False
        self.won = False
    
    def is_position_valid(self, row, col):
        """Check if a position is within the map boundaries"""
        return 0 <= row < self.height and 0 <= col < self.width
    
    def can_player_enter(self, row, col):
        """Check if the player can move to this position"""
        if not self.is_position_valid(row, col):
            return False
        
        cell = self.grid[row][col]
        
        # Can't walk through walls or barriers
        if cell in [WALL, BARRIER]:
            return False
        
        # Can't enter locked goal
        if cell == GOAL and self.purple_collected < self.purple_total:
            return False
        
        return True
    
    def can_liquid_flow_to(self, row, col):
        """Check if water or lava can spread to this position"""
        if not self.is_position_valid(row, col):
            return False
        
        cell = self.grid[row][col]
        
        # Liquids can't pass through solid blocks, purple points, goal, or timed blocks
        if cell in [WALL, MOVABLE, TIMED, PURPLE, GOAL]:
            return False
        
        return True
    
    def try_move_player(self, direction):
        """Attempt to move the player in a direction"""
        if self.game_over:
            return
        
        # Calculate new position
        row, col = self.player_pos
        delta_row, delta_col = self._get_direction_delta(direction)
        new_row = row + delta_row
        new_col = col + delta_col
        
        # Try to push a movable block if there is one
        if self._is_movable_block_at(new_row, new_col):
            if self._try_push_block(new_row, new_col, delta_row, delta_col):
                self.player_pos = (new_row, new_col)
                self._finish_turn()
            return
        
        # Normal movement
        if self.can_player_enter(new_row, new_col):
            self.player_pos = (new_row, new_col)
            self._handle_tile_interaction(new_row, new_col)
            self._finish_turn()
    
    def _get_direction_delta(self, direction):
        """Convert a direction string to row/col delta"""
        directions = {
            'up': (-1, 0),
            'down': (1, 0),
            'left': (0, -1),
            'right': (0, 1)
        }
        return directions.get(direction, (0, 0))
    
    def _is_movable_block_at(self, row, col):
        """Check if there's a movable block at the position"""
        return (self.is_position_valid(row, col) and 
                self.grid[row][col] == MOVABLE)
    
    def _try_push_block(self, block_row, block_col, delta_row, delta_col):
        """Try to push a movable block in a direction"""
        push_row = block_row + delta_row
        push_col = block_col + delta_col
        
        # Check if the push destination is valid
        if not self.is_position_valid(push_row, push_col):
            return False
        
        target = self.grid[push_row][push_col]
        
        # Can only push into empty spaces without liquid
        if (target == EMPTY and 
            not self.water[push_row][push_col] and 
            not self.lava[push_row][push_col]):
            
            # Move the block
            self.grid[block_row][block_col] = EMPTY
            self.grid[push_row][push_col] = MOVABLE
            self.movable_blocks.remove((block_row, block_col))
            self.movable_blocks.add((push_row, push_col))
            return True
        
        return False
    
    def _handle_tile_interaction(self, row, col):
        """Handle player interaction with the tile they moved to"""
        cell = self.grid[row][col]
        
        # Collect purple point
        if cell == PURPLE:
            self.purple_collected += 1
            self.grid[row][col] = EMPTY
        
        # Check for winning condition
        if cell == GOAL and self.purple_collected >= self.purple_total:
            self.won = True
            self.game_over = True
    
    def _finish_turn(self):
        """Complete the turn after player moves"""
        self.move_count += 1
        self._update_timed_blocks()
        self._spread_all_liquids()
        self._check_player_death()
    
    def _update_timed_blocks(self):
        """Update all timed blocks and remove expired ones"""
        expired = []
        
        for pos, block in self.timed_blocks.items():
            if block.countdown():
                expired.append(pos)
        
        # Remove expired blocks
        for pos in expired:
            row, col = pos
            self.grid[row][col] = EMPTY
            del self.timed_blocks[pos]
    
    def _spread_all_liquids(self):
        """Spread water and lava to adjacent tiles"""
        water_new_positions = self._calculate_liquid_spread(self.water)
        lava_new_positions = self._calculate_liquid_spread(self.lava)
        
        # Check for water-lava collisions and create blocks
        collision_positions = water_new_positions & lava_new_positions
        for row, col in collision_positions:
            # Create a movable block where water and lava meet
            self.grid[row][col] = MOVABLE
            self.movable_blocks.add((row, col))
            # Remove from spread lists
            water_new_positions.discard((row, col))
            lava_new_positions.discard((row, col))
        
        # Apply the spread for remaining positions
        for row, col in water_new_positions:
            self.water[row][col] = True
        
        for row, col in lava_new_positions:
            self.lava[row][col] = True
    
    def _calculate_liquid_spread(self, liquid_grid):
        """Calculate where a liquid will spread (without applying it)"""
        # Find all current liquid positions
        current_positions = []
        for row in range(self.height):
            for col in range(self.width):
                if liquid_grid[row][col]:
                    current_positions.append((row, col))
        
        # Calculate spread to adjacent tiles
        new_positions = set()
        for row, col in current_positions:
            for delta_row, delta_col in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                new_row = row + delta_row
                new_col = col + delta_col
                
                if self.can_liquid_flow_to(new_row, new_col):
                    # Only spread to empty positions (not already occupied by this liquid)
                    if not liquid_grid[new_row][new_col]:
                        new_positions.add((new_row, new_col))
        
        return new_positions
    
    def _check_player_death(self):
        """Check if the player has died from lava"""
        player_row, player_col = self.player_pos
        
        if self.lava[player_row][player_col]:
            self.game_over = True
            self.won = False
    
    def is_goal_unlocked(self):
        """Check if the goal is unlocked (all purple collected)"""
        return self.purple_collected >= self.purple_total
