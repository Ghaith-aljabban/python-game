"""
Map loading functionality
"""

from config import *
from game_objects import TimedBlock


class MapLoader:
    """Loads and parses game maps from text files"""
    
    @staticmethod
    def load_from_file(map_file):
        """
        Load a map from a text file.
        Returns a dictionary with all map data.
        """
        with open(map_file, 'r') as f:
            lines = f.readlines()
        
        height = len(lines)
        width = max(len(line.rstrip()) for line in lines)
        
        # Initialize all map layers
        map_data = {
            'width': width,
            'height': height,
            'grid': [[EMPTY for _ in range(width)] for _ in range(height)],
            'water': [[False for _ in range(width)] for _ in range(height)],
            'lava': [[False for _ in range(width)] for _ in range(height)],
            'timed_blocks': {},
            'player_pos': None,
            'goal_pos': None,
            'purple_total': 0,
            'movable_blocks': set()
        }
        
        # Parse each character in the map
        for row, line in enumerate(lines):
            for col, char in enumerate(line.rstrip()):
                MapLoader._parse_tile(char, row, col, map_data)
        
        if map_data['player_pos'] is None:
            raise ValueError("Map must have a player starting position (P)")
        
        return map_data
    
    @staticmethod
    def _parse_tile(char, row, col, map_data):
        """Parse a single tile character and update map data"""
        
        if char == PLAYER:
            map_data['player_pos'] = (row, col)
            map_data['grid'][row][col] = EMPTY
            
        elif char == WATER:
            map_data['water'][row][col] = True
            map_data['grid'][row][col] = EMPTY
            
        elif char == LAVA:
            map_data['lava'][row][col] = True
            map_data['grid'][row][col] = EMPTY
            
        elif char == GOAL:
            map_data['goal_pos'] = (row, col)
            map_data['grid'][row][col] = GOAL
            
        elif char == PURPLE:
            map_data['grid'][row][col] = PURPLE
            map_data['purple_total'] += 1
            
        elif char == MOVABLE:
            map_data['grid'][row][col] = MOVABLE
            map_data['movable_blocks'].add((row, col))
            
        elif char.startswith('T'):
            # Parse timed block (format: T:5 means disappears after 5 turns)
            parts = char.split(':')
            turns = int(parts[1]) if len(parts) > 1 else 3
            map_data['timed_blocks'][(row, col)] = TimedBlock(turns)
            map_data['grid'][row][col] = TIMED
            
        else:
            # Regular tiles (walls, barriers, empty spaces)
            map_data['grid'][row][col] = char
