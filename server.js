import express from 'express';
import cors from 'cors';
import { exec } from 'child_process';
import { promises as fs } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';
import { getLLMSignal } from './getLLMSignal.js';
import morgan from 'morgan';
import dotenv from 'dotenv';
import fetch from 'node-fetch';
import fetchCookie from 'fetch-cookie';
import { CookieJar } from 'tough-cookie';

// Load environment variables
dotenv.config();

// Set up app
const app = express();
const PORT = process.env.PORT || 5050;
const __dirname = dirname(fileURLToPath(import.meta.url));

// Middleware
app.use(cors());
app.use(express.json());
app.use(morgan('dev')); // Logging
const { spawn } = require('child_process');


// Cookie setup for NSE scraping
const jar = new CookieJar();
const fetchWithCookies = fetchCookie(fetch, jar);

// Cache for option chain data to avoid frequent API calls
const optionChainCache = {
  data: null,
  timestamp: 0,
  expiry: 5 * 60 * 1000 // 5 minutes
};

/**
 * Fetch option chain data from NSE
 * @param {number} strike - ATM strike price
 * @returns {Promise<Object>} - Option chain data
 */
async function fetchOptionChain(strike) {
  try {
    // Check cache first
    const now = Date.now();
    if (optionChainCache.data && (now - optionChainCache.timestamp < optionChainCache.expiry)) {
      console.log('Using cached option chain data');
      return optionChainCache.data.find(r => r.strikePrice === strike) || null;
    }

    // Initialize session with NSE
    await fetchWithCookies('https://www.nseindia.com', {
      headers: {
        'User-Agent': 'Mozilla/5.0',
        'Accept': 'text/html',
        'Accept-Language': 'en-US,en;q=0.9'
      }
    });

    // Fetch option chain data
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
    
    if (!data || !data.records || !data.records.data) {
      throw new Error('Invalid data format from NSE API');
    }

    // Update cache
    optionChainCache.data = data.records.data;
    optionChainCache.timestamp = now;

    // Return specific strike data
    return data.records.data.find(r => r.strikePrice === strike) || null;
  } catch (err) {
    console.error("Option Chain Fetch Error:", err);
    return null;
  }
}

/**
 * Execute the ML prediction script
 * @param {Object} candles - Candle data
 * @returns {Promise<Object>} - ML prediction results
 */
async function runMLPrediction(candles) {
  return new Promise((resolve, reject) => {
    const { c1, c2 } = candles;
    const args = `${c1.open} ${c1.high} ${c1.low} ${c1.close} ${c2.open} ${c2.high} ${c2.low} ${c2.close}`;
    
    exec(`python3 ./ai-brain/predict_ml_signal.py ${args}`, (error, stdout, stderr) => {
      if (error) {
        console.error(`❌ ML Prediction failed: ${error.message}`);
        console.error(`stderr: ${stderr}`);
        return reject(new Error(`ML Prediction failed: ${error.message}`));
      }
      
      try {
        const result = JSON.parse(stdout);
        resolve(result);
      } catch (e) {
        reject(new Error(`Failed to parse ML output: ${e.message}`));
      }
    });
  });
}

/**
 * Fuse ML and LLM signals for final decision
 * @param {string} mlSignal - ML model signal
 * @param {string} llmSignal - LLM signal
 * @returns {Object} - Fused signal with confidence score
 */
function fuseSignals(mlSignal, llmSignal) {
  // Simple fusion logic - can be enhanced
  const matchingSignals = mlSignal === llmSignal;
  const confidence = matchingSignals ? 0.85 : 0.65;
  
  const action = confidence > 0.75 ? 'EXECUTE TRADE' : 'SUGGEST TRADE';
  
  // Determine option type and order type
  let optionType = '';
  let orderType = 'MARKET';
  
  if (mlSignal === 'BUY CALL') {
    optionType = 'CALL';
  } else if (mlSignal === 'BUY PUT') {
    optionType = 'PUT';
  }
  
  // Calculate lot size - simple example
  const lots = Math.max(1, Math.floor(confidence * 3));
  
  return {
    action,
    confidence,
    lots,
    optionType,
    orderType
  };
}

/**
 * Log trade to database or file
 * @param {Object} trade - Trade details
 */
async function logTrade(trade) {
  try {
    const logFilePath = join(__dirname, 'trade_logs.json');
    
    // Check if file exists, create if not
    try {
      await fs.access(logFilePath);
    } catch (e) {
      await fs.writeFile(logFilePath, '[]');
    }
    
    // Read existing logs
    const logsData = await fs.readFile(logFilePath, 'utf8');
    const logs = JSON.parse(logsData);
    
    // Add timestamp
    const logEntry = {
      ...trade,
      timestamp: new Date().toISOString()
    };
    
    // Add to logs array
    logs.push(logEntry);
    
    // Write back to file
    await fs.writeFile(logFilePath, JSON.stringify(logs, null, 2));
    
    console.log('✅ Trade logged:', logEntry);
    return true;
  } catch (error) {
    console.error('❌ Failed to log trade:', error);
    return false;
  }
}

/**
 * Execute order through broker API
 * @param {Object} order - Order details
 * @returns {Promise<Object>} - Order execution result
 */
async function executeOrder(order) {
  // In development/testing mode, just log the order
  if (process.env.NODE_ENV !== 'production') {
    console.log('🔄 Mock order execution:', order);
    return { success: true, orderId: `MOCK-${Date.now()}` };
  }
  
  // TODO: Implement real broker API integration here
  // Example:
  /*
  try {
    const response = await fetch('https://api.broker.com/order', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${process.env.BROKER_API_KEY}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(order)
    });
    
    const result = await response.json();
    return result;
  } catch (error) {
    console.error('Order execution failed:', error);
    return { success: false, error: error.message };
  }
  */
  
  return { success: true, orderId: `MOCK-${Date.now()}` };
}

/**
 * Get market data from live or mock source
 * @param {string} index - Index name (NIFTY, BANKNIFTY)
 * @returns {Promise<Object>} - Market data
 */
async function getMarketData(index = 'NIFTY') {
  if (process.env.USE_MOCK_DATA === 'true') {
    // Use mock data for testing
    const mockData = [
      { open: 22450, high: 22480, low: 22380, close: 22460 },
      { open: 22460, high: 22500, low: 22410, close: 22490 },
      { open: 22490, high: 22530, low: 22470, close: 22510 },
      { open: 22510, high: 22540, low: 22450, close: 22530 }
    ];
    
    return {
      candles: {
        c1: mockData[mockData.length - 2],
        c2: mockData[mockData.length - 1]
      },
      marketData: {
        rsi: 60,
        macd: 1.2,
        macd_signal: 0.9,
        volume: 500000,
        vwap: 22400,
        price: mockData[mockData.length - 1].close
      }
    };
  }
  
  // TODO: Implement live data fetching here using your fetch_live_data.py script
  // Example:
  /*
  return new Promise((resolve, reject) => {
    exec(`python3 ./ai-brain/fetch_live_data.py ${index}`, (error, stdout, stderr) => {
      if (error) {
        return reject(new Error(`Failed to fetch market data: ${error.message}`));
      }
      
      try {
        const data = JSON.parse(stdout);
        resolve(data);
      } catch (e) {
        reject(new Error(`Failed to parse market data: ${e.message}`));
      }
    });
  });
  */
  
  // For now, return mock data
  const mockData = [
    { open: 22450, high: 22480, low: 22380, close: 22460 },
    { open: 22460, high: 22500, low: 22410, close: 22490 },
    { open: 22490, high: 22530, low: 22470, close: 22510 },
    { open: 22510, high: 22540, low: 22450, close: 22530 }
  ];
  
  return {
    candles: {
      c1: mockData[mockData.length - 2],
      c2: mockData[mockData.length - 1]
    },
    marketData: {
      rsi: 60,
      macd: 1.2,
      macd_signal: 0.9,
      volume: 500000,
      vwap: 22400,
      price: mockData[mockData.length - 1].close
    }
  };
}

// API Endpoints

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'ok', time: new Date().toISOString() });
});

app.get('/api/performance', async (req, res) => {
  try {
    const options = {
      index: req.query.index,
      startDate: req.query.startDate,
      endDate: req.query.endDate,
      outputDir: path.join(__dirname, 'sambot-frontend/public/images')
    };
    
    const result = await tradeTrackingApi.generateDashboard(options);
    res.json(result);
  } catch (error) {
    console.error('Error generating dashboard:', error);
    res.status(500).json({ error: error.message });
  }
});

// Add an endpoint for metrics only (faster)
app.get('/api/metrics', async (req, res) => {
  try {
    const options = {
      index: req.query.index,
      startDate: req.query.startDate,
      endDate: req.query.endDate,
      includePatterns: req.query.patterns === 'true',
      includePsychology: req.query.psychology === 'true'
    };
    
    const result = await tradeTrackingApi.getPerformanceMetrics(options);
    res.json(result);
  } catch (error) {
    console.error('Error getting metrics:', error);
    res.status(500).json({ error: error.message });
  }
});

// Add advanced strategy endpoint
app.post('/strategies', async (req, res) => {
  try {
    const { index, direction, expiry, width } = req.body;
    
    // This would call your Python code in production
    // const strategy = await executeStrategy(index, direction, expiry, width);
    
    // Mock response for development
    const strategy = {
      strategy: direction === 'BULL' ? 'BULL CALL SPREAD' : 'BEAR PUT SPREAD',
      index,
      buy_leg: `${index}${expiry}${index === 'NIFTY' ? '22500' : '48500'}${direction === 'BULL' ? 'CE' : 'PE'}`,
      sell_leg: `${index}${expiry}${index === 'NIFTY' ? '22600' : '48600'}${direction === 'BULL' ? 'CE' : 'PE'}`,
      max_profit: 2500,
      max_loss: 7500,
      breakeven: index === 'NIFTY' ? '22550' : '48550'
    };
    
    res.json(strategy);
  } catch (err) {
    console.error("Strategy generation error:", err);
    res.status(500).json({ error: err.message });
  }
});

// Update trade status endpoint
app.post('/api/trades/:tradeId/update', async (req, res) => {
  try {
    const tradeId = req.params.tradeId;
    const result = await tradeTrackingApi.updateTrade(tradeId, req.body);
    res.json(result);
  } catch (error) {
    console.error('Error updating trade:', error);
    res.status(500).json({ error: error.message });
  }
});

// Main signals endpoint
app.get('/signals', async (req, res) => {
  try {
    const { index = 'NIFTY', risk_profile = 'moderate' } = req.query;
    console.log(`🔍 Getting signals for ${index} with risk profile ${risk_profile}...`);
    
    // Step 1: Get market data
    const marketData = await getMarketData(index);
    
    // Extract candle data for ML prediction
    const c1 = marketData.candles.c1;
    const c2 = marketData.candles.c2;
    const args = `${c1.open} ${c1.high} ${c1.low} ${c1.close} ${c2.open} ${c2.high} ${c2.low} ${c2.close}`;
    
    // Step 2: Run ML prediction
    const mlPredictionPromise = new Promise((resolve, reject) => {
      exec(`python3 ./ai-brain/predict_ml_signal.py ${args}`, (error, stdout, stderr) => {
        if (error) {
          console.error(`❌ ML Prediction failed: ${error.message}`);
          console.error(`stderr: ${stderr}`);
          return reject(new Error(`ML Prediction failed: ${error.message}`));
        }
        
        try {
          const result = JSON.parse(stdout);
          resolve(result);
        } catch (e) {
          reject(new Error(`Failed to parse ML output: ${e.message}`));
        }
      });
    });
    
    // Step 3: Run indicator analysis
    const indicatorAnalysisPromise = new Promise((resolve, reject) => {
      // Create CSV file with candle data for indicators
      const tempFile = `temp_${Date.now()}.csv`;
      const csvData = 'timestamp,open,high,low,close,volume\n' + 
        `2023-01-01 09:15,${c1.open},${c1.high},${c1.low},${c1.close},100000\n` +
        `2023-01-01 09:20,${c2.open},${c2.high},${c2.low},${c2.close},120000\n`;
      
      fs.writeFile(tempFile, csvData, async (err) => {
        if (err) return reject(new Error(`Failed to create temp file: ${err.message}`));
        
        // Run indicator analysis
        exec(`python3 ./ai-brain/compute_indicators.py ${tempFile}`, (error, stdout, stderr) => {
          // Clean up temp file
          fs.unlink(tempFile, () => {});
          
          if (error) {
            console.error(`❌ Indicator analysis failed: ${error.message}`);
            console.error(`stderr: ${stderr}`);
            return reject(new Error(`Indicator analysis failed: ${error.message}`));
          }
          
          try {
            const result = JSON.parse(stdout);
            resolve(result);
          } catch (e) {
            reject(new Error(`Failed to parse indicator output: ${e.message}`));
          }
        });
      });
    });
    
    // Step 4: Get LLM signal using OpenAI
    const llmPromise = getLLMSignal({
      ...marketData.marketData,
      patterns: [],  // Will be filled from ML prediction
      index: index
    });
    
    // Wait for all promises to resolve
    const [mlResult, indicatorResult, llmResult] = await Promise.all([
      mlPredictionPromise,
      indicatorAnalysisPromise,
      llmPromise
    ]);
    
    // Add patterns from ML prediction to LLM result for reference
    llmResult.patterns = mlResult.patterns_detected || [];
    
    // Step 5: Run decision fusion to get final signal
    const decisionFusionPromise = new Promise((resolve, reject) => {
      // Prepare arguments for decision fusion
      const fusionArgs = {
        ml_signal: mlResult,
        indicator_signal: indicatorResult,
        llm_signal: llmResult,
        risk_profile: risk_profile
      };
      
      // Write args to temp file to avoid command line length limits
      const fusionArgsFile = `fusion_args_${Date.now()}.json`;
      fs.writeFile(fusionArgsFile, JSON.stringify(fusionArgs), async (err) => {
        if (err) return reject(new Error(`Failed to create fusion args file: ${err.message}`));
        
        // Run decision fusion
        exec(`python3 ./ai-brain/decision_fusion.py --file ${fusionArgsFile}`, (error, stdout, stderr) => {
          // Clean up temp file
          fs.unlink(fusionArgsFile, () => {});
          
          if (error) {
            console.error(`❌ Decision fusion failed: ${error.message}`);
            console.error(`stderr: ${stderr}`);
            return reject(new Error(`Decision fusion failed: ${error.message}`));
          }
          
          try {
            const result = JSON.parse(stdout);
            resolve(result);
          } catch (e) {
            reject(new Error(`Failed to parse decision fusion output: ${e.message}`));
          }
        });
      });
    });
    
    // Get decision fusion result
    const decisionResult = await decisionFusionPromise;
    
    // Step 6: Get option chain data if signal is actionable
    let optionData = null;
    if (decisionResult.signal !== 'WAIT') {
      try {
        optionData = await fetchOptionChain(decisionResult.strike);
      } catch (error) {
        console.warn(`Warning: Failed to fetch option chain: ${error.message}`);
      }
    }
    
    // Step 7: Execute order if in auto-execute mode and decision is executable
    if (process.env.AUTO_EXECUTE === 'true' && decisionResult.action === 'EXECUTE TRADE') {
      try {
        const orderResult = await executeOrder({
          index: index,
          strike: decisionResult.strike,
          direction: decisionResult.signal,
          lots: decisionResult.lots,
          entry: decisionResult.current_price
        });
        
        // Log the executed trade
        await logTrade({
          index: index,
          signal: decisionResult.signal,
          entry: decisionResult.current_price,
          exit_price: 0,  // Not yet exited
          stop_loss: decisionResult.stop_loss || 0,
          target: decisionResult.target || 0,
          strike: decisionResult.strike,
          pnl: 0,  // Not yet known
          confidence: decisionResult.confidence
        });
        
        decisionResult.order_executed = orderResult;
      } catch (error) {
        console.error(`❌ Order execution failed: ${error.message}`);
        decisionResult.order_executed = { 
          success: false, 
          error: error.message 
        };
      }
    }
    
    // Step 8: Prepare and send the final response
    const response = {
      ...decisionResult,
      option_chain: optionData,
      ml_prediction: {
        signal: mlResult.signal,
        confidence: mlResult.confidence,
        patterns_detected: mlResult.patterns_detected || []
      },
      indicator_analysis: {
        signal: indicatorResult.signal,
        confidence: indicatorResult.confidence,
        bullish_signals: indicatorResult.bullish_signals || [],
        bearish_signals: indicatorResult.bearish_signals || []
      },
      llm_analysis: {
        decision: llmResult.decision,
        confidence: llmResult.confidence,
        reason: llmResult.reason
      },
      index: index,
      timestamp: new Date().toISOString()
    };
    
    console.log(`✅ Signal for ${index}: ${decisionResult.signal} (${decisionResult.confidence.toFixed(2)})`);
    res.json(response);
    
  } catch (err) {
    console.error("🔥 Error in /signals route:", err);
    res.status(500).json({ 
      signal: "ERROR", 
      reason: err.message,
      timestamp: new Date().toISOString()
    });
  }
});

// Get historical signals
app.get('/signals/history', async (req, res) => {
  try {
    const logFilePath = join(__dirname, 'trade_logs.json');
    
    try {
      await fs.access(logFilePath);
    } catch (e) {
      return res.json({ signals: [] });
    }
    
    const logsData = await fs.readFile(logFilePath, 'utf8');
    const logs = JSON.parse(logsData);
    
    res.json({ signals: logs });
  } catch (err) {
    console.error("Error fetching signal history:", err);
    res.status(500).json({ error: err.message });
  }
});

// Get performance metrics
app.get('/performance', async (req, res) => {
  try {
    const logFilePath = join(__dirname, 'trade_logs.json');
    
    try {
      await fs.access(logFilePath);
    } catch (e) {
      return res.json({ 
        total_trades: 0,
        win_rate: 0,
        avg_profit: 0,
        success: true
      });
    }
    
    const logsData = await fs.readFile(logFilePath, 'utf8');
    const logs = JSON.parse(logsData);
    
    // Calculate basic metrics
    const totalTrades = logs.length;
    const wins = logs.filter(log => log.pnl > 0).length;
    const winRate = totalTrades > 0 ? (wins / totalTrades * 100) : 0;
    const totalPnl = logs.reduce((acc, log) => acc + (log.pnl || 0), 0);
    const avgProfit = totalTrades > 0 ? (totalPnl / totalTrades) : 0;
    
    res.json({
      total_trades: totalTrades,
      win_rate: Math.round(winRate * 100) / 100,
      avg_profit: Math.round(avgProfit * 100) / 100,
      total_pnl: Math.round(totalPnl * 100) / 100,
      success: true
    });
  } catch (err) {
    console.error("Error calculating performance metrics:", err);
    res.status(500).json({ error: err.message, success: false });
  }
});

// Start the server
app.listen(PORT, () => {
  console.log(`🚀 SAMBOT server running on http://localhost:${PORT}`);
  console.log(`📈 Get trading signals at http://localhost:${PORT}/signals`);
  
  if (process.env.NODE_ENV !== 'production') {
    console.log('⚠️ Running in development mode with mock data');
  }
  
  if (process.env.AUTO_EXECUTE === 'true') {
    console.log('🤖 Auto-execution mode is ENABLED');
  } else {
    console.log('🧮 Auto-execution mode is DISABLED');
  }
});


// server.js (add to your existing server code)
const notificationService = require('./services/notificationService');

// Add this to your signal endpoint
app.get('/signals', async (req, res) => {
  try {
    // Your existing signal generation code...
    
    // If a new signal is detected that wasn't present before
    if (isNewSignal) {
      await notificationService.sendSignalAlert(
        signal.index,
        signal.signal,
        signal.entry,
        signal.stop_loss,
        signal.target
      );
    }
    
    res.json(signal);
  } catch (err) {
    console.error("Error in /signals route:", err);
    res.status(500).json({ error: err.message });
  }
});

// Add to your order execution endpoint
app.post('/execute', async (req, res) => {
  try {
    const { index, signal, entry, qty } = req.body;
    
    // Your existing order execution code...
    
    // After successful execution
    await notificationService.sendExecutionAlert(index, signal, entry, qty);
    
    res.json({ status: 'success', message: 'Order executed' });
  } catch (err) {
    console.error("Error in /execute route:", err);
    res.status(500).json({ error: err.message });
  }
});

// Add to your exit position endpoint
app.post('/exit', async (req, res) => {
  try {
    const { index, signal, entry, exit, pnl } = req.body;
    
    // Your existing position exit code...
    
    // After successful exit
    await notificationService.sendExitAlert(index, signal, entry, exit, pnl);
    
    res.json({ status: 'success', message: 'Position exited' });
  } catch (err) {
    console.error("Error in /exit route:", err);
    res.status(500).json({ error: err.message });
  }
});

// Handle graceful shutdown
process.on('SIGTERM', () => {
  console.log('SIGTERM received, shutting down gracefully');
  process.exit(0);
});

process.on('SIGINT', () => {
  console.log('SIGINT received, shutting down gracefully');
  process.exit(0);
});