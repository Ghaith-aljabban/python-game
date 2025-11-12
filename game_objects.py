"""
Game objects and entities
"""

class TimedBlock:
    """A block that disappears after a certain number of turns"""
    
    def __init__(self, turns_remaining):
        self.turns_remaining = turns_remaining
    
    def countdown(self):
        """
        Reduce the timer by one turn.
        Returns True if the block should disappear.
        """
        self.turns_remaining -= 1
        return self.turns_remaining <= 0
    
    def __str__(self):
        return f"TimedBlock({self.turns_remaining} turns left)"
