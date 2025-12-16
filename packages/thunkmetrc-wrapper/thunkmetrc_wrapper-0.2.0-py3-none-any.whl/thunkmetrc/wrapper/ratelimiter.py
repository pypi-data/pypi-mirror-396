import asyncio
import time
from typing import Optional, Dict

class RateLimiterConfig:
    def __init__(self, 
                 enabled: bool = False,
                 max_get_per_second_per_facility: float = 50,
                 max_get_per_second_integrator: float = 150,
                 max_concurrent_get_per_facility: int = 10,
                 max_concurrent_get_integrator: int = 30):
        self.enabled = enabled
        self.max_get_per_second_per_facility = max_get_per_second_per_facility
        self.max_get_per_second_integrator = max_get_per_second_integrator
        self.max_concurrent_get_per_facility = max_concurrent_get_per_facility
        self.max_concurrent_get_integrator = max_concurrent_get_integrator

class TokenBucket:
    def __init__(self, rate: float, capacity: float):
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.last_refill = time.monotonic()
        self.lock = asyncio.Lock()

    async def wait(self):
        async with self.lock:
            now = time.monotonic()
            elapsed = now - self.last_refill
            self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
            self.last_refill = now

            if self.tokens >= 1:
                self.tokens -= 1
                return
            
            # Wait time
            missing = 1.0 - self.tokens
            wait_time = missing / self.rate
        
        await asyncio.sleep(wait_time)
        await self.wait() # Recurse to re-check

class MetrcRateLimiter:
    def __init__(self, config: Optional[RateLimiterConfig] = None):
        if config is None:
            config = RateLimiterConfig()
        self.config = config
        
        self.integrator_rate = TokenBucket(config.max_get_per_second_integrator, config.max_get_per_second_integrator)
        self.integrator_sem = asyncio.Semaphore(config.max_concurrent_get_integrator)
        
        self.facility_rates: Dict[str, TokenBucket] = {}
        self.facility_sems: Dict[str, asyncio.Semaphore] = {}
        self.lock = asyncio.Lock()

    async def execute(self, facility: Optional[str], is_get: bool, op):
        if not self.config.enabled or not is_get:
            return await op()

        async with self.integrator_sem:
            async with self.get_facility_sem(facility):
                await self.integrator_rate.wait()
                if facility:
                    await self.get_facility_rate(facility).wait()
                
                # Retry loop
                while True:
                    try:
                        return await op()
                    except Exception as e:
                        if "429" in str(e): # Checking generic error string, assume client raises exceptions
                             # TODO: Parse retry after
                             await asyncio.sleep(1.0)
                             continue
                        raise e

    def get_facility_rate(self, facility: str) -> TokenBucket:
        if facility not in self.facility_rates:
             self.facility_rates[facility] = TokenBucket(self.config.max_get_per_second_per_facility, self.config.max_get_per_second_per_facility)
        return self.facility_rates[facility]

    def get_facility_sem(self, facility: Optional[str]) -> asyncio.Semaphore:
        if not facility:
             # Return dummy semaphore or context manager
             return asyncio.Semaphore(9999) 
        if facility not in self.facility_sems:
             self.facility_sems[facility] = asyncio.Semaphore(self.config.max_concurrent_get_per_facility)
        return self.facility_sems[facility]
