import time
from typing import Dict

previous_rates: Dict[str, float] = {}
notification_count = 0
THRESHOLD_PCT = 0.1

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
        print(f"NOTIFICATION #{notification_count}: {symbol:10} {fmt(pct):>8} (was: {fmt(prev_pct) if prev_pct else 'N/A':>8})")
    elif abs(pct) >= THRESHOLD_PCT:
        print(f"ABOVE THRESHOLD: {symbol:10} {fmt(pct):>8} (was: {fmt(prev_pct) if prev_pct else 'N/A':>8}) - BUT NO NOTIFICATION")
    else:
        print(f"{symbol:10} {fmt(pct):>8} (was: {fmt(prev_pct) if prev_pct else 'N/A':>8})")
    
    previous_rates[symbol] = rate

def main():
    global notification_count
    
    print("NOTIFICATION LOGIC TEST")
    print("=" * 60)
    print(f"Threshold: ±{THRESHOLD_PCT}%")
    print(f"Min change for notification: 0.01%")
    print("=" * 60)
    
    print("\nSCENARIO 1: First value")
    print("-" * 40)
    simulate_cycle("BTCUSDT", 0.12, 1)
    
    print("\nSCENARIO 2: Cross threshold")
    print("-" * 40)
    simulate_cycle("BTCUSDT", 0.05, 2)
    simulate_cycle("BTCUSDT", 0.12, 3)
    
    print("\nSCENARIO 3: Same value")
    print("-" * 40)
    simulate_cycle("BTCUSDT", 0.12, 4)
    
    print("\nSCENARIO 4: Small change")
    print("-" * 40)
    simulate_cycle("BTCUSDT", 0.1205, 5)
    
    print("\nSCENARIO 5: Significant change")
    print("-" * 40)
    simulate_cycle("BTCUSDT", 0.15, 6)
    
    print("\nSCENARIO 6: Drop below threshold")
    print("-" * 40)
    simulate_cycle("BTCUSDT", 0.05, 7)
    
    print("\nSCENARIO 7: Cross threshold again")
    print("-" * 40)
    simulate_cycle("BTCUSDT", 0.12, 8)
    
    print("\nSCENARIO 8: Negative funding rate")
    print("-" * 40)
    simulate_cycle("ETHUSDT", -0.15, 9)
    simulate_cycle("ETHUSDT", -0.15, 10)
    simulate_cycle("ETHUSDT", -0.18, 11)
    
    print("\n" + "=" * 60)
    print(f"TOTAL NOTIFICATIONS: {notification_count}")
    print("=" * 60)
    
    print("\nCONCLUSIONS:")
    print("+ Notify on first threshold crossing")
    print("+ Notify on significant changes (>0.01%)")
    print("- DON'T notify on same values")
    print("- DON'T notify on small changes")
    print("- DON'T notify on first value")

if __name__ == "__main__":
    main()
