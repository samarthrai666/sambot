import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from joblib import dump
import ta  # For technical indicators

# Load data
df = pd.read_csv('nifty_labeled.csv')

# Calculate technical indicators
df['rsi'] = ta.momentum.RSIIndicator(df['close']).rsi()
macd = ta.trend.MACD(df['close'])
df['macd'] = macd.macd()
df['macd_signal'] = macd.macd_signal()
df['vwap'] = ta.volume.VolumeWeightedAveragePrice(
    high=df['high'], low=df['low'], close=df['close'], volume=df['volume']
).vwap

# Fill missing data
df = df.fillna(0)

# Define features
X = df[[
    "open", "high", "low", "close",
    "bullish_engulfing", "bearish_engulfing",
    "doji", "hammer", "shooting_star",
    "rsi", "macd", "macd_signal",
    "vwap", "volume"
]]

# Labels
y = df["label"]

# Train model
model = RandomForestClassifier()
model.fit(X, y)

# Save model
dump(model, 'sambot_model.joblib')
print("✅ Model trained with 14 features (RSI, MACD, VWAP, Volume)")
