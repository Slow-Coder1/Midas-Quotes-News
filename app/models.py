from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class Quote(BaseModel):
    symbol: str
    last: float
    bid: Optional[float] = None
    ask: Optional[float] = None
    open: Optional[float] = None
    prev_close: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    ts: Optional[int] = None  # epoch seconds

class Headline(BaseModel):
    symbol: str
    source: str
    headline: str
    url: str
    datetime: datetime

class NewsResponse(BaseModel):
    symbol: str
    items: List[Headline]
