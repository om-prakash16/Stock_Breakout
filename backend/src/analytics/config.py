from dataclasses import dataclass, field
from typing import Dict

@dataclass
class BreakoutConfig:
    # Timeframe Name -> Lookback N (days)
    # Important: 'TODAY' breakout implies Close > Yesterday's High.
    # Actually, usually 'Daily Breakout' implies Close > Prev Day High.
    # The requirement says "excludes current candle from lookback".
    # So for Today Breakout, Lookback is 1 (Previous Day).
    
    LOOKBACKS: Dict[str, int] = field(default_factory=lambda: {
        'TODAY': 1,
        'D2': 2,
        'D10': 10,
        'D30': 30,
        'D50': 50,
        'D100': 100,
        'W52': 252, # Approx 52 weeks
        'ALL_TIME': -1 # Special flag for All Time
    })
    
    VOLUME_MULT: float = 1.5
    MIN_HISTORY_DAYS: int = 50 # Ignore stocks with very less history for long breakouts
    
    # Priority for sorting
    PRIORITY: Dict[str, int] = field(default_factory=lambda: {
        'ALL_TIME': 1,
        'W52': 2,
        'D100': 3,
        'D50': 4,
        'D30': 5,
        'D10': 6,
        'D2': 7,
        'TODAY': 8
    })

    def get_lookback(self, key: str) -> int:
        return self.LOOKBACKS.get(key, 0)
