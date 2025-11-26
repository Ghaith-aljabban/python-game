import game_engine
from collections import deque

staticmethod
def BFS(gameEngine):
    iniState =gameEngine.copy()
    visitedStates = set()
    gameStatesQueue = deque()
    gameStatesQueue.append(iniState)
    visitedStates.add(iniState)
    while gameStatesQueue:
        print(f"{gameStatesQueue} \n")
        currentState = gameStatesQueue.popleft()
        availableMoves = currentState.get_valid_moves()
        for move in availableMoves:
            newState = currentState.copy()
            newState.try_move_player(move)
            if newState.won:
                print("Solution found!")
                return newState
            if not newState in visitedStates:
                gameStatesQueue.append(newState)
    return