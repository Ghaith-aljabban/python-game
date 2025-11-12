======================================
    LAVA & AQUA PUZZLE GAME
======================================

DESCRIPTION:
Navigate through challenging puzzle levels where you must avoid spreading lava,
collect purple points, and reach the goal. Use movable blocks strategically to
control the spread of liquids!

HOW TO PLAY:
python lava_aqua_game.py <level_file>

Example: python lava_aqua_game_gui.py level1.txt

CONTROLS:
W - Move Up
S - Move Down
A - Move Left
D - Move Right
Q - Quit Game

GAME ELEMENTS:
P - Player (You) - Bright Green
# - Wall - Cannot pass through
. - Empty Space - Free to move
M - Movable Block - Can be pushed, blocks liquids (Yellow)
C - Purple Point - Collect to unlock the goal (Purple)
G - Goal - Reach after collecting all purple points (Magenta)
W - Water - Spreads each turn, safe to move through (Blue)
L - Lava - Spreads each turn, KILLS you! (Red)
* - Barrier - Liquids pass through, player cannot (Cyan)
T:X - Timed Block - Disappears after X moves (Orange, shows remaining turns)

RULES:
1. Collect ALL purple points (C) to unlock the goal (G)
2. Water and lava spread to adjacent cells each turn
3. Water is safe - you can walk through it
4. Lava kills you instantly - avoid it!
5. Movable blocks (M) can be pushed and block liquid spread
6. Barriers (*) let liquids through but block player movement
7. Timed blocks disappear after the specified number of moves
8. Plan your moves carefully - liquids spread after each move!

STRATEGY TIPS:
- Watch the lava spread patterns
- Use movable blocks to create barriers against lava
- Timed blocks can create temporary safe passages
- Sometimes you need to race against spreading lava
- Water can help by occupying space that lava might spread to

LEVELS:
level1.txt - Tutorial: Basic movement and water
level2.txt - Lava Chase: Escape spreading lava
level3.txt - Block Strategy: Use movable blocks to contain lava
level4.txt - Time Pressure: Navigate with timed blocks and barriers
level5.txt - Master Puzzle: Complex level with all mechanics

ENJOY THE CHALLENGE!

