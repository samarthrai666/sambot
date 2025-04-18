const { execSync } = require('child_process');

function getTradeSignal(candleData) {
  try {
    // Grab last two candles
    const c1 = candleData.at(-2);
    const c2 = candleData.at(-1);

    // Format input string for Python script
    const input = [
      c1.open, c1.high, c1.low, c1.close,
      c2.open, c2.high, c2.low, c2.close
    ].join(' ');

    console.log("🧠 Input to predict.py:", input);

    // Call the Python script
    const output = execSync(`python3 ./ai-brain/predict.py ${input}`).toString().trim();

    console.log("✅ Output from predict.py:", output);

    // Parse and return the JSON result from Python
    return JSON.parse(output);

  } catch (err) {
    console.error("❌ Prediction failed:", err.message);
    return {
      signal: "ERROR",
      trend: "UNKNOWN",
      patterns_detected: [],
      confidence_reason: "Prediction script failed"
    };
  }
}

module.exports = { getTradeSignal };
