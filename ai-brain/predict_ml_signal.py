# 🧪 This file is only for manual CLI testing of Sambot's pipeline end-to-end

import json
from fetch_live_data import fetch_csv_data
from compute_indicators import add_technical_indicators
from detect_patterns import detect_candlestick_patterns
from predict_ml_signal import predict_signal

try:
    df = fetch_csv_data('nifty_data.csv')
    df = add_technical_indicators(df)
    df = detect_candlestick_patterns(df)

    result = predict_signal(df)
    print(json.dumps(result, indent=2))

except Exception as e:
    print(json.dumps({ "error": str(e) }))
