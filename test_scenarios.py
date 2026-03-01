import asyncio
import aiohttp
import time
import random
from typing import Optional, List, Dict, Tuple

BYBIT_SYMBOLS_URL = "https://api.bybit.com/v5/market/instruments-info?category=linear"
BYBIT_FUNDING_URL = "https://api.bybit.com/v5/market/funding/history"

THRESHOLD_PCT = 0.1
POLL_INTERVAL = 5

previous_rates: Dict[str, float] = {}
notification_count = 0

def now() -> str:
    return time.strftime("%H:%M:%S")

def fmt(v: float) -> str:
    return f"{v:.4f}%"

def status_for(rate_dec: float, thr: float) -> str:
    v = rate_dec * 100.0
    if v >= thr:
        return "over_pos"
    if v <= -thr:
        return "over_neg"
    return "inrange"

def should_notify(symbol: str, current_rate: float, threshold: float) -> bool:
    global notification_count
    
    previous_rate = previous_rates.get(symbol)
    
    if previous_rate is None:
        return False
    
    current_status = status_for(current_rate, threshold)
    if current_status not in ("over_pos", "over_neg"):
        return False
    
    previous_status = status_for(previous_rate, threshold)
    if previous_status in ("over_pos", "over_neg"):
        rate_change = abs(current_rate - previous_rate)
        return rate_change > 0.0001
    else:
        return True

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

def check_trigger(symbol: str, rate: float, cycle: int):
    global notification_count
    
    pct = rate * 100.0
    prev_rate = previous_rates.get(symbol)
    prev_pct = prev_rate * 100.0 if prev_rate else None
    
    should_notify_flag = should_notify(symbol, rate, THRESHOLD_PCT / 100.0)
    
    if should_notify_flag:
        notification_count += 1
        print(f"[{now()}] 🔔 УВЕДОМЛЕНИЕ #{notification_count}: {symbol:10} {fmt(pct):>8} (было: {fmt(prev_pct) if prev_pct else 'N/A':>8})")
    elif abs(pct) >= THRESHOLD_PCT:
        print(f"[{now()}] 📊 ПРЕВЫШЕН ПОРОГ: {symbol:10} {fmt(pct):>8} (было: {fmt(prev_pct) if prev_pct else 'N/A':>8}) - НО НЕ УВЕДОМЛЯЕМ")
    else:
        print(f"[{now()}] 📈 {symbol:10} {fmt(pct):>8} (было: {fmt(prev_pct) if prev_pct else 'N/A':>8})")
    
    previous_rates[symbol] = rate

async def main():
    global notification_count
    
    headers = {"User-Agent": "Mozilla/5.0 (compatible; funding-watcher/1.0)"}
    async with aiohttp.ClientSession(headers=headers) as session:
        bybit_symbols = await get_bybit_symbols(session)
        
        test_symbols = bybit_symbols[:10]
        
        print(f"🧪 ТЕСТИРОВАНИЕ ЛОГИКИ УВЕДОМЛЕНИЙ")
        print(f"📊 Тестовых пар: {len(test_symbols)}")
        print(f"⏱️  Интервал: {POLL_INTERVAL} секунд")
        print(f"🎯 Порог: ±{THRESHOLD_PCT}%")
        print(f"🔍 Минимальное изменение для уведомления: 0.01%")
        print("=" * 80)
        
        cycle = 0
        while True:
            cycle += 1
            print(f"\n🔄 ЦИКЛ #{cycle} - {now()}")
            print("-" * 60)
            
            tasks = [fetch_bybit_rate(session, s) for s in test_symbols]
            bybit_rates = await asyncio.gather(*tasks, return_exceptions=True)
            
            valid_count = 0
            for s, r in zip(test_symbols, bybit_rates):
                if isinstance(r, Exception) or r is None:
                    continue
                valid_count += 1
                check_trigger(s, r, cycle)
            
            print(f"\n📊 ИТОГИ ЦИКЛА #{cycle}:")
            print(f"   ✅ Валидных rates: {valid_count}/{len(test_symbols)}")
            print(f"   🔔 Всего уведомлений: {notification_count}")
            print("=" * 80)
            
            await asyncio.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n🛑 Остановка тестирования. Всего уведомлений: {notification_count}")
