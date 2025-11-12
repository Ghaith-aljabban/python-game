"""
Main entry point for Lava & Aqua Puzzle Game
"""

import pygame
import sys
from game_engine import GameEngine
from renderer import Renderer
from config import FPS


def main():
    """Main game loop"""
    # Check if a level file was provided
    if len(sys.argv) < 2:
        print("Usage: python main.py <level_file>")
        print("Example: python main.py level1.txt")
        return
    
    level_file = sys.argv[1]
    
    # Initialize pygame
    pygame.init()
    
    # Create game engine and renderer
    try:
        game = GameEngine(level_file)
        renderer = Renderer(game)
    except FileNotFoundError:
        print(f"Error: Level file '{level_file}' not found!")
        pygame.quit()
        return
    except Exception as e:
        print(f"Error loading level: {e}")
        pygame.quit()
        return
    
    # Set up game clock
    clock = pygame.time.Clock()
    
    # Main game loop
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.KEYDOWN:
                # Movement controls
                if event.key in [pygame.K_w, pygame.K_UP]:
                    game.try_move_player('up')
                elif event.key in [pygame.K_s, pygame.K_DOWN]:
                    game.try_move_player('down')
                elif event.key in [pygame.K_a, pygame.K_LEFT]:
                    game.try_move_player('left')
                elif event.key in [pygame.K_d, pygame.K_RIGHT]:
                    game.try_move_player('right')
                
                # Restart
                elif event.key == pygame.K_r:
                    game = GameEngine(level_file)
                    renderer = Renderer(game)
                
                # Quit
                elif event.key == pygame.K_q:
                    running = False
        
        # Draw the game
        renderer.draw_frame()
        
        # Limit framerate
        clock.tick(FPS)
    
    # Clean up
    pygame.quit()


if __name__ == "__main__":
    main()
