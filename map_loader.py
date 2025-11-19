
from config import *
from game_objects import TimedBlock


class MapLoader:

    @staticmethod
    def load_from_file(map_file):

        with open(map_file, 'r') as f:
            lines = f.readlines()
        
        height = len(lines)
        
        tokenized_lines = []
        max_width = 0
        for line in lines:
            tokens = MapLoader._tokenize_line(line.rstrip())
            tokenized_lines.append(tokens)
            max_width = max(max_width, len(tokens))
        
        width = max_width
        
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
        
        for row, tokens in enumerate(tokenized_lines):
            for col, token in enumerate(tokens):
                MapLoader._parse_tile(token, row, col, map_data)
        
        if map_data['player_pos'] is None:
            raise ValueError("Map must have a player starting position (P)")
        
        return map_data
    
    @staticmethod
    def _tokenize_line(line):
        tokens = []
        i = 0
        while i < len(line):
            char = line[i]
            if char == 'T' and i + 1 < len(line) and line[i + 1] == ':':
                j = i + 2
                while j < len(line) and line[j].isdigit():
                    j += 1
                tokens.append(line[i:j])
                i = j
            else:
                tokens.append(char)
                i += 1
        return tokens
    
    @staticmethod
    def _parse_tile(char, row, col, map_data):
        
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
            parts = char.split(':')
            turns = int(parts[1]) if len(parts) > 1 else 3
            map_data['timed_blocks'][(row, col)] = TimedBlock(turns)
            map_data['grid'][row][col] = TIMED
            
        else:
            map_data['grid'][row][col] = char
