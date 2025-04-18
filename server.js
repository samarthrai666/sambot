import express from 'express';
import cors from 'cors';
import { exec } from 'child_process';
import { getLLMSignal } from './getLLMSignal.js';
import dotenv from 'dotenv';
import fetch from 'node-fetch';
import fetchCookie from 'fetch-cookie';
import { CookieJar } from 'tough-cookie';
import fuseSignals from './decision_fusion.js';
import executeOrder from './order_executor.js';
import logTrade from './log_and_learn.js';

dotenv.config();

const app = express();
const PORT = 5050;
app.use(cors());

// 🍪 Cookie setup for NSE scraping (temporary)
const jar = new CookieJar();
const fetchWithCookies = fetchCookie(fetch, jar);

const fetchOptionChain = async (strike) => {
  try {
    await fetchWithCookies('https://www.nseindia.com', {
      headers: {
        'User-Agent': 'Mozilla/5.0',
        'Accept': 'text/html',
        'Accept-Language': 'en-US,en;q=0.9'
      }
    });

    const response = await fetchWithCookies(
      'https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY',
      {
        headers: {
          'User-Agent': 'Mozilla/5.0',
          'Accept': 'application/json',
          'Accept-Language': 'en-US,en;q=0.9',
          'Referer': 'https://www.nseindia.com/'
        }
      }
    );

    const data = await response.json();
    return data?.records?.data?.find(r => r.strikePrice === strike) || null;

  } catch (err) {
    console.error("Option Chain Fetch Error:", err);
    return null;
  }
};

app.get('/signals', async (req, res) => {
  try {
    const c1 = { open: 22450, high: 22500, low: 22400, close: 22470 };
    const c2 = { open: 22480, high: 22530, low: 22460, close: 22510 };
    const args = `${c1.open} ${c1.high} ${c1.low} ${c1.close} ${c2.open} ${c2.high} ${c2.low} ${c2.close}`;

    exec(`python3 ./ai-brain/predict_ml_signal.py ${args}`, async (error, stdout) => {
      if (error) {
        console.error(`❌ ML Prediction failed: ${error.message}`);
        return res.json({ signal: "ERROR", reason: error.message });
      }

      const modelOutput = JSON.parse(stdout);
      const mlSignal = modelOutput.signal;

      const marketData = {
        rsi: 60,
        macd: 1.2,
        macd_signal: 0.9,
        volume: 500000,
        vwap: 22400,
        price: c2.close,
        patterns: modelOutput.patterns_detected || [],
        trend: modelOutput.trend
      };

      const llm = await getLLMSignal(marketData);

      const fused = fuseSignals(mlSignal, llm.decision);

      const {
        action, confidence, lots, optionType, orderType
      } = fused;

      const currentPrice = c2.close;
      const entry = action === 'EXECUTE TRADE' ? modelOutput.entry : null;
      const stop_loss = action === 'EXECUTE TRADE' ? modelOutput.stop_loss : null;
      const target = action === 'EXECUTE TRADE' ? modelOutput.target : null;
      const strike = action === 'EXECUTE TRADE' ? modelOutput.strike : null;
      const pnl = entry ? (currentPrice - entry) * lots * 15 : 0;

      let optionData = null;
      if (action === 'EXECUTE TRADE') {
        optionData = await fetchOptionChain(strike);
        executeOrder({ type: orderType, optionType, lots, strike, entry });
        logTrade({ time: new Date().toLocaleTimeString(), entry, cmp: currentPrice, pnl });
      }

      const response = {
        ...modelOutput,
        llm_decision: llm.decision,
        llm_reason: llm.reason,
        confidence,
        action,
        option_type: optionType,
        order_type: orderType,
        lots,
        cmp: currentPrice,
        entry,
        stop_loss,
        target,
        strike,
        pnl,
        option_chain: optionData
      };

      console.log("🧠 ML:", mlSignal, ", 🤖 LLM:", llm.decision, ", Confidence:", confidence);
      res.json(response);
    });

  } catch (err) {
    console.error("🔥 Error in /signals route:", err);
    res.status(500).json({ signal: "ERROR", reason: err.message });
  }
});

app.listen(PORT, () => {
  console.log(`🚀 Sambot server running on http://localhost:${PORT}`);
});
