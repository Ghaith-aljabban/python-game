
class TimedBlock:
    
    def __init__(self, turns_remaining):
        self.turns_remaining = turns_remaining
    
    def countdown(self):
        self.turns_remaining -= 1
        return self.turns_remaining <= 0
    
    def __str__(self):
        return f"TimedBlock({self.turns_remaining} turns left)"
