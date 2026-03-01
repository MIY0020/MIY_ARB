import time
from typing import Dict

previous_rates: Dict[str, float] = {}
notification_count = 0

THRESHOLD_PCT = 0.1

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

def simulate_cycle(symbol: str, rate: float, cycle: int):
    global notification_count
    
    pct = rate * 100.0
    prev_rate = previous_rates.get(symbol)
    prev_pct = prev_rate * 100.0 if prev_rate else None
    
    should_notify_flag = should_notify(symbol, rate, THRESHOLD_PCT / 100.0)
    
    if should_notify_flag:
        notification_count += 1
        print(f"УВЕДОМЛЕНИЕ #{notification_count}: {symbol:10} {fmt(pct):>8} (было: {fmt(prev_pct) if prev_pct else 'N/A':>8})")
    elif abs(pct) >= THRESHOLD_PCT:
        print(f"ПРЕВЫШЕН ПОРОГ: {symbol:10} {fmt(pct):>8} (было: {fmt(prev_pct) if prev_pct else 'N/A':>8}) - НО НЕ УВЕДОМЛЯЕМ")
    else:
        print(f"{symbol:10} {fmt(pct):>8} (было: {fmt(prev_pct) if prev_pct else 'N/A':>8})")
    
    previous_rates[symbol] = rate

def main():
    global notification_count
    
    print("ДЕМОНСТРАЦИЯ СЦЕНАРИЕВ УВЕДОМЛЕНИЙ")
    print("=" * 60)
    print(f"Порог: ±{THRESHOLD_PCT}%")
    print(f"Минимальное изменение для уведомления: 0.01%")
    print("=" * 60)
    
    print("\nСЦЕНАРИЙ 1: Первое значение")
    print("-" * 40)
    simulate_cycle("BTCUSDT", 0.12, 1)
    
    print("\nСЦЕНАРИЙ 2: Переход через порог")
    print("-" * 40)
    simulate_cycle("BTCUSDT", 0.05, 2)
    simulate_cycle("BTCUSDT", 0.12, 3)
    
    print("\nСЦЕНАРИЙ 3: Одинаковое значение")
    print("-" * 40)
    simulate_cycle("BTCUSDT", 0.12, 4)
    
    print("\nСЦЕНАРИЙ 4: Незначительное изменение")
    print("-" * 40)
    simulate_cycle("BTCUSDT", 0.1205, 5)
    
    print("\nСЦЕНАРИЙ 5: Значительное изменение")
    print("-" * 40)
    simulate_cycle("BTCUSDT", 0.15, 6)
    
    print("\nСЦЕНАРИЙ 6: Падение ниже порога")
    print("-" * 40)
    simulate_cycle("BTCUSDT", 0.05, 7)
    
    print("\nСЦЕНАРИЙ 7: Снова превышение порога")
    print("-" * 40)
    simulate_cycle("BTCUSDT", 0.12, 8)
    
    print("\nСЦЕНАРИЙ 8: Негативный funding rate")
    print("-" * 40)
    simulate_cycle("ETHUSDT", -0.15, 9)
    simulate_cycle("ETHUSDT", -0.15, 10)
    simulate_cycle("ETHUSDT", -0.18, 11)
    
    print("\n" + "=" * 60)
    print(f"ИТОГО УВЕДОМЛЕНИЙ: {notification_count}")
    print("=" * 60)
    
    print("\nВЫВОДЫ:")
    print("+ Уведомляем при первом превышении порога")
    print("+ Уведомляем при значительных изменениях (>0.01%)")
    print("- НЕ уведомляем при одинаковых значениях")
    print("- НЕ уведомляем при незначительных изменениях")
    print("- НЕ уведомляем при первом значении")

if __name__ == "__main__":
    main()
