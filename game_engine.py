
import copy
from config import *
from map_loader import MapLoader


class GameEngine:
    
    def __init__(self, map_file):
        map_data = MapLoader.load_from_file(map_file)
        
        self.width = map_data['width']
        self.height = map_data['height']
        self.grid = map_data['grid']
        self.water = map_data['water']
        self.lava = map_data['lava']
        self.timed_blocks = map_data['timed_blocks']
        self.movable_blocks = map_data['movable_blocks']
        
        self.player_pos = map_data['player_pos']
        self.goal_pos = map_data['goal_pos']
        self.purple_total = map_data['purple_total']
        
        self.move_count = 0
        self.purple_collected = 0
        self.game_over = False
        self.won = False
    
    def is_position_valid(self, row, col):
        return 0 <= row < self.height and 0 <= col < self.width
    
    def can_player_enter(self, row, col):
        if not self.is_position_valid(row, col):
            return False
        
        cell = self.grid[row][col]
        
        if cell in [WALL, BARRIER,TIMED]:
            return False
        
        if cell == GOAL and self.purple_collected < self.purple_total:
            return False
        
        return True
    
    def can_liquid_flow_to(self, row, col):
        if not self.is_position_valid(row, col):
            return False
        
        cell = self.grid[row][col]
        
        if cell in [WALL, MOVABLE, TIMED, PURPLE, GOAL]:
            return False
        
        return True
    
    def try_move_player(self, direction):
        if self.game_over:
            return
        
        row, col = self.player_pos
        delta_row, delta_col = self._get_direction_delta(direction)
        new_row = row + delta_row
        new_col = col + delta_col
        
        if self._is_movable_block_at(new_row, new_col):
            if self._try_push_block(new_row, new_col, delta_row, delta_col):
                self.player_pos = (new_row, new_col)
                self._finish_turn()
            return
        
        if self.can_player_enter(new_row, new_col):
            self.player_pos = (new_row, new_col)
            self._handle_win_interaction(new_row, new_col)
            self._finish_turn()
    
    def _get_direction_delta(self, direction):
        directions = {
            'up': (-1, 0),
            'down': (1, 0),
            'left': (0, -1),
            'right': (0, 1)
        }
        return directions.get(direction, (0, 0))
    
    def _is_movable_block_at(self, row, col):
        return (self.is_position_valid(row, col) and 
                self.grid[row][col] == MOVABLE)
    
    def _try_push_block(self, block_row, block_col, delta_row, delta_col):
        push_row = block_row + delta_row
        push_col = block_col + delta_col
        
        if not self.is_position_valid(push_row, push_col):
            return False
        
        target = self.grid[push_row][push_col]
        
        if (target == EMPTY or 
             self.water[push_row][push_col] or 
             self.lava[push_row][push_col]):
            
            self.grid[block_row][block_col] = EMPTY
            self.grid[push_row][push_col] = MOVABLE
            self.water[push_row][push_col] = False
            self.lava[push_row][push_col] = False
            self.movable_blocks.remove((block_row, block_col))
            self.movable_blocks.add((push_row, push_col))
            return True
        
        return False
    
    def _handle_win_interaction(self, row, col):
        cell = self.grid[row][col]
        
        if cell == PURPLE:
            self.purple_collected += 1
            self.grid[row][col] = EMPTY
        
        if cell == GOAL and self.purple_collected >= self.purple_total:
            self.won = True
            self.game_over = True
    
    def _finish_turn(self):
        self.move_count += 1
        self._update_timed_blocks()
        self._spread_all_liquids()
        self._check_player_death()
    
    def _update_timed_blocks(self):
        expired = []
        
        for pos, block in self.timed_blocks.items():
            if block.countdown():
                expired.append(pos)
        
        for pos in expired:
            row, col = pos
            self.grid[row][col] = EMPTY
            del self.timed_blocks[pos]
    
    def _spread_all_liquids(self):
        water_new_positions = self._calculate_liquid_spread(self.water)
        lava_new_positions = self._calculate_liquid_spread(self.lava)
        
        collision_positions = water_new_positions & lava_new_positions
        for row, col in collision_positions:
            self.grid[row][col] = WALL
            self.movable_blocks.add((row, col))
            water_new_positions.discard((row, col))
            lava_new_positions.discard((row, col))
        
        for row, col in water_new_positions:
            self.water[row][col] = True
        
        for row, col in lava_new_positions:
            self.lava[row][col] = True
    
    def _calculate_liquid_spread(self, liquid_grid):
        current_positions = []
        for row in range(self.height):
            for col in range(self.width):
                if liquid_grid[row][col]:
                    current_positions.append((row, col))
        
        new_positions = set()
        for row, col in current_positions:
            for delta_row, delta_col in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                new_row = row + delta_row
                new_col = col + delta_col
                
                if self.can_liquid_flow_to(new_row, new_col):
                    if liquid_grid is self.water :
                        new_positions.add((new_row, new_col))
                    elif liquid_grid is self.lava and not self.water[new_row][new_col]:
                        new_positions.add((new_row, new_col))
                    elif not self.water[new_row][new_col] and not self.lava[new_row][new_col]:
                        new_positions.add((new_row, new_col))
        
        return new_positions
    
    def _check_player_death(self):
        player_row, player_col = self.player_pos

        if self.lava[player_row][player_col] or self.grid[player_row][player_col] == WALL:
            self.game_over = True
            self.won = False

    def copy(self):
        new_game = GameEngine.__new__(GameEngine)

        new_game.width = self.width
        new_game.height = self.height
        new_game.grid = copy.deepcopy(self.grid)
        new_game.water = copy.deepcopy(self.water)
        new_game.lava = copy.deepcopy(self.lava)
        new_game.timed_blocks = copy.deepcopy(self.timed_blocks)
        new_game.movable_blocks = copy.deepcopy(self.movable_blocks)

        new_game.player_pos = self.player_pos
        new_game.goal_pos = self.goal_pos
        new_game.purple_total = self.purple_total

        new_game.move_count = self.move_count
        new_game.purple_collected = self.purple_collected
        new_game.game_over = self.game_over
        new_game.won = self.won

        return new_game

    def get_state_tuple(self):
        return (
            self.player_pos,
            self.purple_collected,
            self.move_count,
            tuple(tuple(row) for row in self.grid),
            tuple(tuple(row) for row in self.water),
            tuple(tuple(row) for row in self.lava),
            tuple((pos, block.turns_remaining) for pos, block in self.timed_blocks.items()),
            tuple(self.movable_blocks),
            self.goal_pos,
            self.purple_total,
            self.game_over,
            self.won
        )

    def __hash__(self):
        return hash(self.get_state_tuple())

    def __eq__(self, other):
        if not isinstance(other, GameEngine):
            return False
        return self.get_state_tuple() == other.get_state_tuple()


    def get_valid_moves(self):

        if self.game_over:
            return []

        valid_moves = []
        directions = ['right', 'down', 'left','up' ]

        for direction in directions:
            row, col = self.player_pos
            delta_row, delta_col = self._get_direction_delta(direction)
            new_row = row + delta_row
            new_col = col + delta_col

            can_move = False

            if self._is_movable_block_at(new_row, new_col):
                push_row = new_row + delta_row
                push_col = new_col + delta_col
                if self.is_position_valid(push_row, push_col):
                    target = self.grid[push_row][push_col]
                    if (target == EMPTY or
                        self.water[push_row][push_col] or
                        self.lava[push_row][push_col]):
                        can_move = True
            elif self.can_player_enter(new_row, new_col):
                can_move = True

            if can_move:
                valid_moves.append(direction)

        return valid_moves

    def is_goal_unlocked(self):
        return self.purple_collected >= self.purple_total


    def transmission_function(self,direction):
        return self.try_move_player(direction)