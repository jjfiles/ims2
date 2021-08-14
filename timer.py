import time

class Timer:
    """Keep track of an objects "cooldown" state by measuring it's last call time vs the current time
    """    
    def __init__(self):
        """initialize local variables
        """        
        self.timer = None
        self.cd = 5
        
    def start(self):
        """start timer
        """        
        self.timer = time.perf_counter()
    
    def check(self):
        """check if the object has passed it's cooldown periord

        Returns:
            bool: returns true if the object is off cooldown
        """    
        if (time.perf_counter() - self.timer) > self.cd:
            self.timer = None
            return True
        
        else:
            return False

    def __del__(self):
        """delete objects
        """
        self.timer = None
        self.cd = None