import pandas as pd
from pattern_detector import (
    is_bullish_engulfing,
    is_bearish_engulfing,
    is_doji,
    is_hammer,
    is_shooting_star
)

# Load your raw candle data (from project root or ../nifty_data.csv)
df = pd.read_csv('nifty_data.csv')

# Create empty pattern rows
pattern_rows = []

for i in range(len(df)):
    if i < 2:
        pattern_rows.append({
            "bullish_engulfing": 0,
            "bearish_engulfing": 0,
            "doji": 0,
            "hammer": 0,
            "shooting_star": 0,
            "label": 0  # default wait
        })
        continue

    c1 = df.iloc[i - 2]
    c2 = df.iloc[i - 1]
    c3 = df.iloc[i]

    bullish = is_bullish_engulfing(c1, c2)
    bearish = is_bearish_engulfing(c1, c2)
    doji = is_doji(c3)
    hammer = is_hammer(c3)
    shooting = is_shooting_star(c3)

    # Very simple label logic: 1 = BUY CALL, -1 = BUY PUT, 0 = WAIT
    label = 1 if hammer or bullish else -1 if shooting or bearish else 0

    pattern_rows.append({
        "bullish_engulfing": int(bullish),
        "bearish_engulfing": int(bearish),
        "doji": int(doji),
        "hammer": int(hammer),
        "shooting_star": int(shooting),
        "label": label
    })

# Merge and save
patterns_df = pd.DataFrame(pattern_rows)
final_df = pd.concat([df.reset_index(drop=True), patterns_df], axis=1)
final_df.to_csv('nifty_labeled.csv', index=False)
print("✅ Patterns labeled and saved to 'nifty_labeled.csv'")
