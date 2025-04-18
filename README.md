# 🤖 Sambot - AI-Powered Options Trading System 🇮🇳

Sambot is a modular, end-to-end AI-driven options trading engine built for the Indian stock market. It combines candlestick pattern detection, technical indicators, machine learning, and OpenAI's LLM for confidence-based signal generation and automated trade execution.

---

## 🚀 Features

- ✅ Live market data ingestion (5-min candles)
- 📊 Pattern recognition (Doji, Hammer, Engulfing, etc.)
- 📈 RSI, MACD, VWAP, ATR, and more
- 🧠 ML-based prediction with RandomForest
- 🤖 LLM-based contextual reasoning (via OpenAI)
- 🎯 Smart confidence fusion between ML & LLM
- 🔁 Auto-trade execution logic (Fyers/NSE)
- 📘 Trade journaling, logs, and performance feedback loop
- 🌐 Tailwind + React frontend with live signal dashboard

---

## 🧩 Project Structure

```bash
.
├── fetch_live_data.py         # 1️⃣ Fetches live OHLCV from NSE/Fyers
├── compute_indicators.py      # 2️⃣ Adds RSI, MACD, VWAP, etc.
├── detect_patterns.py         # 3️⃣ Detects candle patterns
├── predict_ml_signal.py       # 4️⃣ Predicts signal using ML
├── getLLMSignal.py            # 5️⃣ Uses OpenAI to analyze signal
├── decision_fusion.py         # 6️⃣ Combines ML+LLM with confidence scoring
├── order_executor.py          # 7️⃣ Executes order if confident
├── log_and_learn.py           # 8️⃣ Tracks trades, logs P&L
├── label_patterns.py          # (For training dataset labeling)
├── train.py                   # Trains and saves the RandomForest model
├── server.js                  # Exposes API `/signals` to frontend
├── sambot_model.joblib        # Saved trained model
├── nifty_data.csv             # Raw 5-min OHLCV data
├── nifty_labeled.csv          # Pattern-labeled data for training
├── sambot-frontend/           # Frontend app (React + Tailwind)
└── README.md                  # This file
