#
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

#Quotes Model 
class Quote(BaseModel):
    symbol: str # Ticker Symbol
    last: float #Current price
    bid: Optional[float] = None
    ask: Optional[float] = None
    open: Optional[float] = None
    prev_close: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    ts: Optional[int] = None  # epoch seconds

#news article headline
class Headline(BaseModel):
    symbol: str
    source: str
    headline: str
    url: str
    datetime: datetime
#Wraps a list of headlines for east API response.
class NewsResponse(BaseModel):
    symbol: str
    items: List[Headline] #list of recent news items
