// trade_exit_handler.js
import { sendTradeExitAlert } from './notification_service.js';
import { log_trade } from './log_and_learn.js';

/**
 * Process a trade exit and send notifications
 * @param {Object} tradeData - The trade exit data
 */
export async function handleTradeExit(tradeData) {
  try {
    const {
      index,
      signal,
      entry,
      exit,
      lots = 1,
      strike,
      timestamp_entry,
      timestamp_exit = new Date()
    } = tradeData;
    
    // Calculate PnL
    const pointValue = 15; // Standard NIFTY multiplier
    const direction = signal.includes('CALL') ? 1 : -1;
    const pnl = (exit - entry) * direction * lots * pointValue;
    
    // Calculate duration
    const entryTime = timestamp_entry ? new Date(timestamp_entry) : new Date();
    const exitTime = new Date(timestamp_exit);
    const durationMs = exitTime - entryTime;
    const durationMinutes = Math.floor(durationMs / 60000);
    const durationHours = Math.floor(durationMinutes / 60);
    const remainingMinutes = durationMinutes % 60;
    const duration = durationHours > 0 
      ? `${durationHours}h ${remainingMinutes}m` 
      : `${durationMinutes}m`;
    
    // Log the trade in the system
    log_trade({
      index,
      signal,
      entry,
      exit,
      pnl,
      timestamp_entry: entryTime,
      timestamp_exit: exitTime,
      strike,
      lots
    });
    
    // Send Telegram notification
    await sendTradeExitAlert({
      index,
      signal,
      entry,
      exit,
      pnl,
      duration,
      lots
    });
    
    console.log(`📊 Trade exited: ${index} ${signal} with P&L ${pnl}`);
    
    return { success: true, pnl };
  } catch (error) {
    console.error('❌ Error handling trade exit:', error);
    return { success: false, error: error.message };
  }
}

export default handleTradeExit;