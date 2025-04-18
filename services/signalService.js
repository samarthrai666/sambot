// File: services/signalService.js
import { exec } from 'child_process';
import { promises as fs } from 'fs';
import { getLLMSignal } from '../getLLMSignal.js';
import fetchCookie from 'fetch-cookie';
import { CookieJar } from 'tough-cookie';
import fetch from 'node-fetch';

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
export async function fetchOptionChain(strike) {
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
export async function runMLPrediction(candles) {
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
 * Run technical indicator analysis
 * @param {Object} candles - Candle data
 * @returns {Promise<Object>} - Indicator analysis results
 */
export async function runIndicatorAnalysis(candles) {
  return new Promise((resolve, reject) => {
    // Create CSV file with candle data for indicators
    const tempFile = `temp_${Date.now()}.csv`;
    const { c1, c2 } = candles;
    const csvData = 'timestamp,open,high,low,close,volume\n' + 
      `2023-01-01 09:15,${c1.open},${c1.high},${c1.low},${c1.close},100000\n` +
      `2023-01-01 09:20,${c2.open},${c2.high},${c2.low},${c2.close},120000\n`;
    
    fs.writeFile(tempFile, csvData)
      .then(() => {
        // Run indicator analysis
        exec(`python3 ./ai-brain/compute_indicators.py ${tempFile}`, (error, stdout, stderr) => {
          // Clean up temp file
          fs.unlink(tempFile).catch(() => {});
          
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
      })
      .catch(err => {
        reject(new Error(`Failed to create temp file: ${err.message}`));
      });
  });
}

/**
 * Run decision fusion to get final signal
 * @param {Object} fusionArgs - Arguments for decision fusion
 * @returns {Promise<Object>} - Final decision
 */
export async function runDecisionFusion(fusionArgs) {
  return new Promise((resolve, reject) => {
    // Write args to temp file to avoid command line length limits
    const fusionArgsFile = `fusion_args_${Date.now()}.json`;
    
    fs.writeFile(fusionArgsFile, JSON.stringify(fusionArgs))
      .then(() => {
        // Run decision fusion
        exec(`python3 ./ai-brain/decision_fusion.py --file ${fusionArgsFile}`, (error, stdout, stderr) => {
          // Clean up temp file
          fs.unlink(fusionArgsFile).catch(() => {});
          
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
      })
      .catch(err => {
        reject(new Error(`Failed to create fusion args file: ${err.message}`));
      });
  });
}

/**
 * Get market data from live or mock source
 * @param {string} index - Index name (NIFTY, BANKNIFTY)
 * @returns {Promise<Object>} - Market data
 */
export async function getMarketData(index = 'NIFTY') {
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