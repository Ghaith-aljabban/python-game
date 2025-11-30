import collections
import game_engine as GE


def DFS(GE):
    visited= set()
    startState = GE.copy()
    Queue = collections.deque()
    Queue.append(startState)
    visited.add(startState)
    while(Queue):
        currentState1 = Queue.pop()
        # currentState1 = Queue.popleft()
        moves = currentState1.get_valid_moves()
        for move in moves:
            newstate1 = currentState1.copy()
            newstate1.try_move_player(move)
            if newstate1.won:
                return 'solution found'
            if not newstate1 in visited:
                Queue.append(newstate1)
                visited.add(newstate1)
    return 'no solution found'