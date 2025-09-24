from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from cachetools import TTLCache
from datetime import datetime, timezone
from typing import Dict
import asyncio

from .config import settings
from .models import Quote, Headline, NewsResponse
from .finnhub import FinnhubClient

app = FastAPI(title="MIDAS Quotes & News", version="0.1.0")

if settings.origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

quotes_cache = TTLCache(maxsize=256, ttl=30)   # 30s per symbol
news_cache = TTLCache(maxsize=256, ttl=600)    # 10min per symbol
_locks: Dict[str, asyncio.Lock] = {}

def _lock_for(key: str) -> asyncio.Lock:
    if key not in _locks:
        _locks[key] = asyncio.Lock()
    return _locks[key]

def _clean_symbol(symbol: str) -> str:
    s = symbol.strip().upper()
    if not s:
        raise HTTPException(status_code=400, detail="Symbol required")
    return s

@app.get("/health")
async def health():
    return {"ok": True, "ts": datetime.now(timezone.utc).isoformat()}

@app.get("/quote", response_model=Quote)
async def quote(symbol: str = Query(..., description="Ticker e.g. AAPL")):
    symbol = _clean_symbol(symbol)
    if not settings.FINNHUB_API_KEY or settings.FINNHUB_API_KEY.lower() == "your_key_here":
        raise HTTPException(status_code=503, detail="FINNHUB_API_KEY not configured")

    if symbol in quotes_cache:
        return quotes_cache[symbol]

    lock = _lock_for(f"q:{symbol}")
    async with lock:
        if symbol in quotes_cache:
            return quotes_cache[symbol]

        client = FinnhubClient(settings.FINNHUB_API_KEY)
        try:
            data = await client.get_quote(symbol)
        finally:
            await client.close()

        q = Quote(
            symbol=symbol,
            last=float(data.get("c") or 0.0),
            open=float(data.get("o") or 0.0),
            prev_close=float(data.get("pc") or 0.0),
            high=float(data.get("h") or 0.0),
            low=float(data.get("l") or 0.0),
            ts=int(data.get("t") or 0),
        )
        quotes_cache[symbol] = q
        return q

@app.get("/news", response_model=NewsResponse)
async def news(symbol: str, limit: int = Query(3, ge=1, le=10)):
    symbol = _clean_symbol(symbol)
    if not settings.FINNHUB_API_KEY or settings.FINNHUB_API_KEY.lower() == "your_key_here":
        raise HTTPException(status_code=503, detail="FINNHUB_API_KEY not configured")

    if symbol in news_cache:
        return NewsResponse(symbol=symbol, items=news_cache[symbol][:limit])

    lock = _lock_for(f"n:{symbol}")
    async with lock:
        if symbol in news_cache:
            return NewsResponse(symbol=symbol, items=news_cache[symbol][:limit])

        client = FinnhubClient(settings.FINNHUB_API_KEY)
        try:
            data = await client.get_company_news(symbol, days=5)
        finally:
            await client.close()

        items = []
        for it in data:
            try:
                ts = it.get("datetime") or it.get("time") or it.get("publishedTime")
                dt = (datetime.fromtimestamp(int(ts), tz=timezone.utc)
                      if isinstance(ts, (int, float, str)) and str(ts).isdigit()
                      else datetime.fromisoformat(str(ts).replace("Z", "+00:00")))
            except Exception:
                dt = datetime.now(timezone.utc)

            items.append(Headline(
                symbol=symbol,
                source=str(it.get("source") or it.get("site") or "unknown"),
                headline=str(it.get("headline") or it.get("title") or ""),
                url=str(it.get("url") or ""),
                datetime=dt,
            ))

        items.sort(key=lambda x: x.datetime, reverse=True)
        news_cache[symbol] = items
        return NewsResponse(symbol=symbol, items=items[:limit])
