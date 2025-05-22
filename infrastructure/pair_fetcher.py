import os
# !/usr/bin/env python3
"""Module documentation follows."""

API_URL   = "https://public.bitbank.cc/tickers"
PRICE_DIR = pathlib.Path("rin_user_data/price_data")
PRICE_DIR.mkdir(parents=True, exist_ok=True)

def main():
    res  = requests.get(API_URL, timeout=10).json()["data"]
    ts   = datetime.datetime.utcnow().isoformat() + "Z"
    for item in res:
        pair  = item["pair"]
        price = item["sell"]        # または平均/終値など任意
        csv_path = PRICE_DIR / f"{pair}.csv"
        is_new  = not csv_path.exists()
        with csv_path.open("a", newline="") as f:
            w = csv.writer(f)
            if is_new:
                w.writerow(["timestamp", "price"])
            w.writerow([ts, price])
    print(f"{len(res)} tickers saved.")

if __name__ == "__main__":
    main()
