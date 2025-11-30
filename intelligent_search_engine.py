import game_engine
from collections import deque 
import time

def BFS_with_moves(gameEngine):
    start_time = time.time()  
    iniState = gameEngine.copy()
    visitedStates = set()
    gameStatesQueue = deque()
    gameStatesQueue.append((iniState, []))  
    visitedStates.add(iniState)
    
    while gameStatesQueue:
        currentState, moves_so_far = gameStatesQueue.popleft()
        availableMoves = currentState.get_valid_moves()
        
        for move in availableMoves:
            newState = currentState.copy()
            newState.try_move_player(move)
            
            if newState.won:
                end_time = time.time()
                elapsed_time = end_time - start_time
                print(f"solution found after searching in {len(visitedStates)} state within {elapsed_time:.4f} seconds")

                return newState, moves_so_far + [move]
            
            if newState not in visitedStates:
                new_moves_path = moves_so_far + [move]
                gameStatesQueue.append((newState, new_moves_path))
                visitedStates.add(newState)
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"no solution found after searching in {len(visitedStates)} state within {elapsed_time:.4f} seconds")
    return None, []  



def DFS_with_moves(gameEngine):
    start_time = time.time()  
    iniState = gameEngine.copy()
    visitedStates = set()
    gameStatesQueue = deque()
    gameStatesQueue.append((iniState, []))  
    visitedStates.add(iniState)

    while gameStatesQueue:
        currentState, moves_so_far = gameStatesQueue.pop()
        availableMoves = currentState.get_valid_moves()
        
        for move in availableMoves:
            newState = currentState.copy()
            newState.try_move_player(move)
            
            if newState.won:
                end_time = time.time()
                elapsed_time = end_time - start_time
                print(f"solution found after searching in {len(visitedStates)} state within {elapsed_time:.4f} seconds")

                return newState, moves_so_far + [move]
            
            if newState not in visitedStates:
                new_moves_path = moves_so_far + [move]
                gameStatesQueue.append((newState, new_moves_path))
                visitedStates.add(newState)
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"no solution found after searching in {len(visitedStates)} state within {elapsed_time:.4f} seconds")
    return None, []  
