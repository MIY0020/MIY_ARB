import asyncio, os, time
from typing import Optional, Dict, Tuple, List
import aiohttp
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart
from aiogram.client.default import DefaultBotProperties

from dotenv import load_dotenv
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "") 

BINANCE_EXCHANGE_INFO = "https://fapi.binance.com/fapi/v1/exchangeInfo"
BINANCE_FUNDING_URL = "https://fapi.binance.com/fapi/v1/premiumIndex"
BYBIT_SYMBOLS_URL = "https://api.bybit.com/v5/market/instruments-info?category=linear"
BYBIT_FUNDING_URL = "https://api.bybit.com/v5/market/funding/history"

POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "5"))

bot = Bot(token=TELEGRAM_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

tasks: Dict[int, asyncio.Task] = {}
states: Dict[int, Dict[Tuple[str, str], str]] = {}
user_threshold: Dict[int, float] = {}
debug_mode: Dict[int, bool] = {}
previous_rates: Dict[int, Dict[Tuple[str, str], float]] = {}
alex_mode: bool = False

kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Уведомлять от ±0.1%"), KeyboardButton(text="Уведомлять от ±0.5%")],
        [KeyboardButton(text="Отладка ВКЛ"), KeyboardButton(text="Отладка ВЫКЛ")],
        [KeyboardButton(text="Стоп")],
    ],
    resize_keyboard=True
)

def now():
    return time.strftime("%H:%M:%S")

def symbol_to_pair_lc(symbol: str) -> str:
    s = symbol.upper()
    if s.endswith("USDT"):
        base = s[:-4]
        return f"{base.lower()}/usdt"
    return f"{s.lower()}/usdt"

async def get_binance_symbols(session: aiohttp.ClientSession) -> List[str]:
    async with session.get(BINANCE_EXCHANGE_INFO, timeout=15) as r:
        j = await r.json()
        return [s["symbol"] for s in j.get("symbols", []) if s.get("contractType") == "PERPETUAL"]

async def get_bybit_symbols(session: aiohttp.ClientSession) -> List[str]:
    try:
        async with session.get(BYBIT_SYMBOLS_URL, timeout=15) as r:
            j = await r.json()
            res = j.get("result", {}).get("list", [])
            return [s["symbol"] for s in res if s.get("contractType") == "LinearPerpetual"]
    except Exception:
        return []

async def fetch_binance_rate(session: aiohttp.ClientSession, symbol: str) -> Optional[float]:
    try:
        async with session.get(BINANCE_FUNDING_URL, params={"symbol": symbol}, timeout=10) as r:
            if r.status != 200:
                return None
            data = await r.json()
            val = data.get("lastFundingRate")
            if val is None:
                return None
            return float(val)
    except Exception:
        return None

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

def status_for(rate_dec: float, thr: float) -> str:
    v = rate_dec * 100.0
    if v >= thr:
        return "over_pos"
    if v <= -thr:
        return "over_neg"
    return "inrange"

async def send_debug_info(chat_id: int, exchange: str, symbol: str, rate: float):
    rate_percent = rate * 100.0
    emoji = "🟢" if rate_percent >= 0 else "🔴"
    debug_line = f"{symbol_to_pair_lc(symbol)} | {emoji} {rate_percent:.4f}% | {exchange.lower()}"
    print(f"[DEBUG] {debug_line}")
    await bot.send_message(chat_id, debug_line)

def should_notify(chat_id: int, exchange: str, symbol: str, current_rate: float, threshold: float) -> bool:
    key = (exchange, symbol)
    previous_rate = previous_rates.get(chat_id, {}).get(key)
    
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

async def notify(chat_id: int, exchange: str, symbol: str, rate_dec: float, thr: float):
    v = rate_dec * 100.0
    emoji = "🟢" if v >= 0 else "🔴"
    line = f"{symbol_to_pair_lc(symbol)} | {emoji} {v:.1f}% | {exchange.lower()}"
    print(f"[DEBUG] Sending notification: {line}")
    await bot.send_message(chat_id, line)

def get_previous_state(chat_id: int, exchange: str, symbol: str) -> str:
    key = (exchange, symbol)
    return states.get(chat_id, {}).get(key, "unknown")

async def monitor(chat_id: int, thr: float):
    headers = {"User-Agent": "Mozilla/5.0 (compatible; funding-bot/1.0)"}
    states.setdefault(chat_id, {})
    previous_rates.setdefault(chat_id, {})
    async with aiohttp.ClientSession(headers=headers) as session:
        binance_syms = await get_binance_symbols(session)
        bybit_syms = await get_bybit_symbols(session)
        debug_status = "ВКЛЮЧЕНА" if debug_mode.get(chat_id, False) else "ВЫКЛЮЧЕНА"
        await bot.send_message(chat_id, f"Загружено пар: Binance {len(binance_syms)}, Bybit {len(bybit_syms)}.\nПорог: ±{thr:.1f}%.\n🔍 Отладка: {debug_status}")
        sem = asyncio.Semaphore(25)
        cycle_count = 0
        while True:
            if user_threshold.get(chat_id) != thr:
                return
            try:
                cycle_count += 1
                print(f"[DEBUG] Cycle {cycle_count} for chat {chat_id}, threshold: {thr}")
                bn_tasks = []
                for s in binance_syms:
                    async def _bn(sym=s):
                        async with sem:
                            return sym, await fetch_binance_rate(session, sym)
                    bn_tasks.append(asyncio.create_task(_bn()))
                by_tasks = []
                for s in bybit_syms:
                    async def _by(sym=s):
                        async with sem:
                            return sym, await fetch_bybit_rate(session, sym)
                    by_tasks.append(asyncio.create_task(_by()))

                bn_res = await asyncio.gather(*bn_tasks, return_exceptions=True)
                by_res = await asyncio.gather(*by_tasks, return_exceptions=True)

                notifications_sent = 0
                debug_sent = 0
                
                if debug_mode.get(chat_id, False):
                    await bot.send_message(chat_id, f"🔍 <b>Отладка Binance (цикл {cycle_count}):</b>")
                
                for sym, val in [x for x in bn_res if not isinstance(x, Exception)]:
                    if val is None:
                        continue
                    st = status_for(val, thr)
                    key = ("binance", sym)
                    prev = states[chat_id].get(key, "unknown")
                    
                    if debug_mode.get(chat_id, False):
                        await send_debug_info(chat_id, "binance", sym, val)
                        debug_sent += 1
                    
                    if should_notify(chat_id, "binance", sym, val, thr):
                        print(f"[DEBUG] Binance {sym}: rate changed to {val*100:.3f}% (prev: {previous_rates[chat_id].get(key, 'N/A')*100:.3f}%)")
                        await notify(chat_id, "binance", sym, val, thr)
                        notifications_sent += 1
                    
                    states[chat_id][key] = st
                    previous_rates[chat_id][key] = val

                if debug_mode.get(chat_id, False):
                    await bot.send_message(chat_id, f"🔍 <b>Отладка Bybit (цикл {cycle_count}):</b>")
                
                for sym, val in [x for x in by_res if not isinstance(x, Exception)]:
                    if val is None:
                        continue
                    st = status_for(val, thr)
                    key = ("bybit", sym)
                    prev = states[chat_id].get(key, "unknown")
                    
                    if debug_mode.get(chat_id, False):
                        await send_debug_info(chat_id, "bybit", sym, val)
                        debug_sent += 1
                    
                    if should_notify(chat_id, "bybit", sym, val, thr):
                        print(f"[DEBUG] Bybit {sym}: rate changed to {val*100:.3f}% (prev: {previous_rates[chat_id].get(key, 'N/A')*100:.3f}%)")
                        await notify(chat_id, "bybit", sym, val, thr)
                        notifications_sent += 1
                    
                    states[chat_id][key] = st
                    previous_rates[chat_id][key] = val

                print(f"[DEBUG] Cycle {cycle_count} completed. Notifications sent: {notifications_sent}, Debug messages sent: {debug_sent}")
                
                if debug_mode.get(chat_id, False):
                    await bot.send_message(chat_id, f"✅ <b>Цикл {cycle_count} завершен:</b>\n📊 Уведомлений: {notifications_sent}\n🔍 Отладочных сообщений: {debug_sent}")

            except Exception as e:
                print(f"[DEBUG] Exception in cycle {cycle_count}: {e}")
            await asyncio.sleep(POLL_INTERVAL)

@dp.message(CommandStart())
async def on_start(m: Message):
    if alex_mode:
        return
    await m.answer("Выбери режим уведомлений:", reply_markup=kb)

@dp.message(F.text == "Уведомлять от ±0.1%")
async def on_thr01(m: Message):
    if alex_mode:
        return
    chat_id = m.chat.id
    user_threshold[chat_id] = 0.1
    if chat_id in tasks and not tasks[chat_id].done():
        tasks[chat_id].cancel()
    tasks[chat_id] = asyncio.create_task(monitor(chat_id, 0.1))
    await m.answer("Мониторинг запущен: порог ±0.1%.", reply_markup=kb)

@dp.message(F.text == "Уведомлять от ±0.5%")
async def on_thr05(m: Message):
    if alex_mode:
        return
    chat_id = m.chat.id
    user_threshold[chat_id] = 0.5
    if chat_id in tasks and not tasks[chat_id].done():
        tasks[chat_id].cancel()
    tasks[chat_id] = asyncio.create_task(monitor(chat_id, 0.5))
    await m.answer("Мониторинг запущен: порог ±0.5%.", reply_markup=kb)

@dp.message(F.text == "Отладка ВКЛ")
async def on_debug_on(m: Message):
    if alex_mode:
        return
    chat_id = m.chat.id
    debug_mode[chat_id] = True
    print(f"[DEBUG] Debug mode enabled for chat {chat_id}")
    await m.answer("🔍 Отладочный режим включен. Будут показаны все фьючерсы и их funding rates.", reply_markup=kb)

@dp.message(F.text == "Отладка ВЫКЛ")
async def on_debug_off(m: Message):
    if alex_mode:
        return
    chat_id = m.chat.id
    debug_mode[chat_id] = False
    print(f"[DEBUG] Debug mode disabled for chat {chat_id}")
    await m.answer("🔍 Отладочный режим выключен.", reply_markup=kb)

@dp.message(F.text == "Стоп")
async def on_stop(m: Message):
    if alex_mode:
        return
    chat_id = m.chat.id
    user_threshold.pop(chat_id, None)
    debug_mode.pop(chat_id, None)
    states.pop(chat_id, None)
    previous_rates.pop(chat_id, None)
    if chat_id in tasks and not tasks[chat_id].done():
        tasks[chat_id].cancel()
    await m.answer("Мониторинг остановлен.", reply_markup=kb)

@dp.message(F.text == "/alex")
async def on_alex_command(m: Message):
    global alex_mode
    alex_mode = True
    
    for chat_id in list(tasks.keys()):
        if chat_id in tasks and not tasks[chat_id].done():
            tasks[chat_id].cancel()
        user_threshold.pop(chat_id, None)
        debug_mode.pop(chat_id, None)
        states.pop(chat_id, None)
        previous_rates.pop(chat_id, None)
    
    tasks.clear()
    user_threshold.clear()
    debug_mode.clear()
    states.clear()
    previous_rates.clear()
    
    print(f"[ALEX] Alex mode activated by user {m.chat.id}. All monitoring stopped.")
    await m.answer("🛑 Режим Alex активирован. Все мониторинги остановлены. Бот игнорирует пользователей.", reply_markup=kb)

@dp.message(F.text == "/alex_off")
async def on_alex_off_command(m: Message):
    global alex_mode
    alex_mode = False
    print(f"[ALEX] Alex mode deactivated by user {m.chat.id}. Bot restored.")
    await m.answer("✅ Режим Alex отключен. Бот восстановлен.", reply_markup=kb)

async def main():
    if not TELEGRAM_TOKEN or ":" not in TELEGRAM_TOKEN:
        print("❌ TELEGRAM_TOKEN не найден или некорректен. Добавь его в .env или $env:TELEGRAM_TOKEN")
        return
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass