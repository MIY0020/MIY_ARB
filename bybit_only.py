import asyncio
import aiohttp
import time
from typing import Optional, List

BYBIT_SYMBOLS_URL = "https://api.bybit.com/v5/market/instruments-info?category=linear"
BYBIT_FUNDING_URL = "https://api.bybit.com/v5/market/funding/history"

THRESHOLD_PCT = 0.1
POLL_INTERVAL = 5
alex_mode = False  # Режим остановки

def now() -> str:
    return time.strftime("%H:%M:%S")

def fmt(v: float) -> str:
    return f"{v:.4f}%"

async def get_bybit_symbols(session: aiohttp.ClientSession) -> List[str]:
    try:
        async with session.get(BYBIT_SYMBOLS_URL, timeout=15) as r:
            j = await r.json()
            res = j.get("result", {}).get("list", [])
            return [s["symbol"] for s in res if s.get("contractType") == "LinearPerpetual"]
    except Exception:
        return []

async def fetch_bybit_rate(session: aiohttp.ClientSession, symbol: str) -> Optional[float]:
    try:
        params = {"symbol": symbol, "limit": 1, "category": "linear"}
        async with session.get(BYBIT_FUNDING_URL, params=params, timeout=10) as r:
            if r.status != 200:
                return None
            j = await r.json()
            if j.get("retCode") != 0:
                return None
            arr = j.get("result", {}).get("list", [])
            if not arr:
                return None
            rate_s = arr[0].get("fundingRate")
            if rate_s is None:
                return None
            return float(rate_s)
    except Exception:
        return None

def check_trigger(exchange: str, symbol: str, rate: float):
    pct = rate * 100.0
    if abs(pct) >= THRESHOLD_PCT:
        print(f"[{now()}] >>> {exchange.upper():7} {symbol:10} {fmt(pct):>8}  TRIGGER ±{THRESHOLD_PCT}%")
    else:
        print(f"[{now()}] {exchange.upper():7} {symbol:10} {fmt(pct):>8}")

async def main():
    global alex_mode
    headers = {"User-Agent": "Mozilla/5.0 (compatible; funding-watcher/1.0)"}
    async with aiohttp.ClientSession(headers=headers) as session:
        bybit_symbols = await get_bybit_symbols(session)
        print(f"Bybit найдено: {len(bybit_symbols)} пар")
        print(f"Интервал обновления: {POLL_INTERVAL} секунд")
        print(f"Порог уведомления: ±{THRESHOLD_PCT}%")
        print("----------------------------------------------------------------")
        print("Введите 'alex' для остановки мониторинга")

        while True:
            if alex_mode:
                print(f"[{now()}] 🛑 Режим Alex активирован. Мониторинг остановлен.")
                break
                
            print(f"[{now()}] Проверка Bybit funding rate...")
            
            tasks = [fetch_bybit_rate(session, s) for s in bybit_symbols]
            bybit_rates = await asyncio.gather(*tasks, return_exceptions=True)
            
            valid_count = 0
            for s, r in zip(bybit_symbols, bybit_rates):
                if isinstance(r, Exception) or r is None:
                    continue
                valid_count += 1
                check_trigger("bybit", s, r)
            
            print(f"[{now()}] Bybit: получено {valid_count} валидных rates из {len(bybit_symbols)}")
            print("----------------------------------------------------------------")
            await asyncio.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nОстановка мониторинга.")
