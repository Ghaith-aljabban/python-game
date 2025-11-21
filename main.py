import pygame
import sys
from game_engine import GameEngine
from renderer import Renderer
from config import FPS


def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <level_file>")
        print("Example: python main.py level1.txt")
        return
    
    level_file = sys.argv[1]
    
    pygame.init()
    
    try:
        game_stack = list()
        game = GameEngine(level_file)
        renderer = Renderer(game)
        game_stack.append(game.copy())
    except FileNotFoundError:
        print(f"Error: Level file '{level_file}' not found!")
        pygame.quit()
        return
    except Exception as e:
        print(f"Error loading level: {e}")
        pygame.quit()
        return
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    game.try_move_player('up')
                    game_stack.append(game.copy())
                    print(GameEngine.get_valid_moves(game))
                elif event.key == pygame.K_s:
                    game.try_move_player('down')
                    game_stack.append(game.copy())
                    print(GameEngine.get_valid_moves(game))
                elif event.key == pygame.K_a:
                    game.try_move_player('left')
                    game_stack.append(game.copy())
                    print(GameEngine.get_valid_moves(game))
                elif event.key == pygame.K_d:
                    game.try_move_player('right')
                    game_stack.append(game.copy())
                    print(GameEngine.get_valid_moves(game))

                elif event.key == pygame.K_r:
                    game = GameEngine(level_file)
                    renderer = Renderer(game)
                    game_stack.clear()

                elif event.key == pygame.K_q:
                    running = False
                elif event.key == pygame.K_z:
                    if len(game_stack) > 1:
                        game_stack.pop()
                        game = game_stack[-1].copy()
                        renderer = Renderer(game)
        
        renderer.draw_frame()
    
    pygame.quit()


if __name__ == "__main__":
    main()
