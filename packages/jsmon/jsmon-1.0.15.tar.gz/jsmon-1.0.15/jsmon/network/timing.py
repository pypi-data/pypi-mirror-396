import asyncio
import random

class HumanLikeTiming:
    """Simulates human behavior with delays."""
    def __init__(self, min_delay=1.0, max_delay=3.0):
        self.min_delay = min_delay
        self.max_delay = max_delay
        
    async def get_delay(self):
        """Calculates and waits for a random delay."""
        delay = random.uniform(self.min_delay, self.max_delay)
        
        # 10% chance of a longer pause (thinking)
        if random.random() < 0.1:
            delay += random.uniform(2.0, 5.0)
            
        await asyncio.sleep(delay)
