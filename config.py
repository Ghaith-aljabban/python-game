"""
Game configuration and constants
"""

# Game symbols used in map files
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

# Display settings
TILE_SIZE = 40
UI_HEIGHT = 100
FPS = 60

# Colors for rendering
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
