import game_engine
from collections import deque 
import time

def BFS(gameEngine):
    counter = 0
    start_time = time.time()  
    iniState = gameEngine.copy()
    GeneratedStates = set()
    gameStatesQueue = deque()
    gameStatesQueue.append((iniState, []))  
    GeneratedStates.add(iniState)
    
    while gameStatesQueue:
        counter += 1
        currentState, moves_so_far = gameStatesQueue.popleft()
        availableMoves = currentState.get_valid_moves()
        if len(GeneratedStates) >= 150000 :
                print('overload')
                break
        for move in availableMoves:
            newState = currentState.copy()
            newState.try_move_player(move)
            
            if newState.won:
                end_time = time.time()
                elapsed_time = end_time - start_time
                print(f"solution found after searching in {len(GeneratedStates)} state within {elapsed_time:.4f} seconds")
                print(f"Visited  state {counter}")
                print(f"solution len {len(moves_so_far) + 1}")
                return moves_so_far + [move]
            
            if newState not in GeneratedStates:
                new_moves_path = moves_so_far + [move]
                gameStatesQueue.append((newState, new_moves_path))
                GeneratedStates.add(newState)
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"no solution found after searching in {len(GeneratedStates)} state within {elapsed_time:.4f} seconds")
    return  []  


def DFS(gameEngine):
    counter = 0
    start_time = time.time()  
    iniState = gameEngine.copy()
    GeneratedStates = set()
    gameStatesQueue = []
    gameStatesQueue.append((iniState, []))  
    GeneratedStates.add(iniState)
    
    while gameStatesQueue:
        counter += 1
        currentState, moves_so_far = gameStatesQueue.pop()
        availableMoves = currentState.get_valid_moves()
        if len(GeneratedStates) >= 150000 :
                print('overload')
                break
        for move in availableMoves:
            newState = currentState.copy()
            newState.try_move_player(move)
            
            if newState.won:
                end_time = time.time()
                elapsed_time = end_time - start_time
                print(f"solution found after searching in {len(GeneratedStates)} state within {elapsed_time:.4f} seconds")
                print(f"Visited  state {counter}")
                print(f"solution len {len(moves_so_far) + 1}")
                return moves_so_far + [move]
            
            if newState not in GeneratedStates:
                new_moves_path = moves_so_far + [move]
                gameStatesQueue.append((newState, new_moves_path))
                GeneratedStates.add(newState)
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"no solution found after searching in {len(GeneratedStates)} state within {elapsed_time:.4f} seconds")
    return  []  