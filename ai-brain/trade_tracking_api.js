// Trade Tracking API
// This module provides a bridge between Node.js and the Python trade tracking system

const { spawn } = require('child_process');
const path = require('path');

/**
 * Log a new trade entry
 * @param {Object} tradeData - Trade data including index, signal, entry_price, etc.
 * @returns {Promise<Object>} The logged trade with its ID
 */
function logTrade(tradeData) {
  return new Promise((resolve, reject) => {
    // Convert the trade data to a JSON string to pass to Python
    const tradeDataStr = JSON.stringify(tradeData);
    
    // Spawn a Python process
    const pythonProcess = spawn('python3', [
      path.join(__dirname, 'trade_tracking', 'log_trade_api.py'),
      tradeDataStr
    ]);
    
    let dataString = '';
    let errorString = '';
    
    pythonProcess.stdout.on('data', (data) => {
      dataString += data.toString();
    });
    
    pythonProcess.stderr.on('data', (data) => {
      errorString += data.toString();
    });
    
    pythonProcess.on('close', (code) => {
      if (code !== 0) {
        console.error(`Python process exited with code ${code}`);
        console.error(`Error: ${errorString}`);
        return reject(new Error(`Failed to log trade: ${errorString}`));
      }
      
      try {
        const result = JSON.parse(dataString);
        resolve(result);
      } catch (error) {
        reject(new Error(`Failed to parse Python output: ${error.message}`));
      }
    });
  });
}

/**
 * Update an existing trade
 * @param {string} tradeId - ID of the trade to update
 * @param {Object} updateData - Data to update (exit_price, status, etc.)
 * @returns {Promise<Object>} Updated trade data
 */
function updateTrade(tradeId, updateData) {
  return new Promise((resolve, reject) => {
    // Create the update payload
    const payload = {
      trade_id: tradeId,
      ...updateData
    };
    
    // Convert the payload to a JSON string
    const payloadStr = JSON.stringify(payload);
    
    // Spawn a Python process
    const pythonProcess = spawn('python3', [
      path.join(__dirname, 'trade_tracking', 'update_trade_api.py'),
      payloadStr
    ]);
    
    let dataString = '';
    let errorString = '';
    
    pythonProcess.stdout.on('data', (data) => {
      dataString += data.toString();
    });
    
    pythonProcess.stderr.on('data', (data) => {
      errorString += data.toString();
    });
    
    pythonProcess.on('close', (code) => {
      if (code !== 0) {
        console.error(`Python process exited with code ${code}`);
        console.error(`Error: ${errorString}`);
        return reject(new Error(`Failed to update trade: ${errorString}`));
      }
      
      try {
        const result = JSON.parse(dataString);
        resolve(result);
      } catch (error) {
        reject(new Error(`Failed to parse Python output: ${error.message}`));
      }
    });
  });
}

/**
 * Generate a performance dashboard
 * @param {Object} options - Options for dashboard generation
 * @param {string} [options.index] - Filter by index
 * @param {string} [options.startDate] - Start date (YYYY-MM-DD)
 * @param {string} [options.endDate] - End date (YYYY-MM-DD)
 * @param {string} [options.outputDir] - Output directory
 * @returns {Promise<Object>} Dashboard data and paths
 */
function generateDashboard(options = {}) {
  return new Promise((resolve, reject) => {
    // Build arguments for the Python script
    const args = [path.join(__dirname, 'trade_tracking', 'generate_dashboard.py')];
    
    if (options.index) {
      args.push('--index', options.index);
    }
    
    if (options.startDate) {
      args.push('--start', options.startDate);
    }
    
    if (options.endDate) {
      args.push('--end', options.endDate);
    }
    
    if (options.outputDir) {
      args.push('--output-dir', options.outputDir);
    }
    
    // Spawn a Python process
    const pythonProcess = spawn('python3', args);
    
    let dataString = '';
    let errorString = '';
    
    pythonProcess.stdout.on('data', (data) => {
      dataString += data.toString();
    });
    
    pythonProcess.stderr.on('data', (data) => {
      errorString += data.toString();
    });
    
    pythonProcess.on('close', (code) => {
      if (code !== 0) {
        console.error(`Python process exited with code ${code}`);
        console.error(`Error: ${errorString}`);
        return reject(new Error(`Failed to generate dashboard: ${errorString}`));
      }
      
      try {
        const result = JSON.parse(dataString);
        resolve(result);
      } catch (error) {
        reject(new Error(`Failed to parse Python output: ${error.message}`));
      }
    });
  });
}

/**
 * Get summary performance metrics
 * @param {Object} options - Options for metrics calculation
 * @returns {Promise<Object>} Performance metrics
 */
function getPerformanceMetrics(options = {}) {
  return new Promise((resolve, reject) => {
    // Build arguments for the Python script
    const args = [path.join(__dirname, 'trade_tracking', 'get_metrics_api.py')];
    
    // Convert options to a JSON string
    const optionsStr = JSON.stringify(options);
    args.push(optionsStr);
    
    // Spawn a Python process
    const pythonProcess = spawn('python3', args);
    
    let dataString = '';
    let errorString = '';
    
    pythonProcess.stdout.on('data', (data) => {
      dataString += data.toString();
    });
    
    pythonProcess.stderr.on('data', (data) => {
      errorString += data.toString();
    });
    
    pythonProcess.on('close', (code) => {
      if (code !== 0) {
        console.error(`Python process exited with code ${code}`);
        console.error(`Error: ${errorString}`);
        return reject(new Error(`Failed to get metrics: ${errorString}`));
      }
      
      try {
        const result = JSON.parse(dataString);
        resolve(result);
      } catch (error) {
        reject(new Error(`Failed to parse Python output: ${error.message}`));
      }
    });
  });
}

module.exports = {
  logTrade,
  updateTrade,
  generateDashboard,
  getPerformanceMetrics
};