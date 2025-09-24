import httpx
from datetime import datetime, timedelta, timezone

FINNHUB_BASE = "https://finnhub.io/api/v1"

class FinnhubClient:
    def __init__(self, api_key: str, timeout: float = 10.0):
        self.api_key = api_key
        self._client = httpx.AsyncClient(timeout=timeout)

    async def close(self):
        await self._client.aclose()

    async def get_quote(self, symbol: str):
        url = f"{FINNHUB_BASE}/quote"
        params = {"symbol": symbol, "token": self.api_key}
        r = await self._client.get(url, params=params)
        r.raise_for_status()
        return r.json()

    async def get_company_news(self, symbol: str, days: int = 5):
        to_dt = datetime.now(timezone.utc).date()
        from_dt = to_dt - timedelta(days=days)
        url = f"{FINNHUB_BASE}/company-news"
        params = {
            "symbol": symbol,
            "from": from_dt.isoformat(),
            "to": to_dt.isoformat(),
            "token": self.api_key,
        }
        r = await self._client.get(url, params=params)
        r.raise_for_status()
        return r.json()
