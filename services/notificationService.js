// notification_service.js
import fetch from 'node-fetch';
import dotenv from 'dotenv';

dotenv.config();

// Telegram configuration
const TELEGRAM_BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN;
const TELEGRAM_CHAT_ID = process.env.TELEGRAM_CHAT_ID;

/**
 * Send a notification message to Telegram
 * @param {string} message - The message to send
 * @param {boolean} isUrgent - If true, adds 🚨 emoji to indicate urgency
 * @returns {Promise<Object>} - Response from Telegram API
 */
export async function sendTelegramAlert(message, isUrgent = false) {
  if (!TELEGRAM_BOT_TOKEN || !TELEGRAM_CHAT_ID) {
    console.error('❌ Telegram configuration missing. Please set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID env variables');
    return { success: false, error: 'Telegram configuration missing' };
  }

  // Format the message
  const prefix = isUrgent ? '🚨 URGENT: ' : '🤖 Sambot: ';
  const formattedMessage = `${prefix}${message}`;

  try {
    const telegramUrl = `https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage`;
    const response = await fetch(telegramUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        chat_id: TELEGRAM_CHAT_ID,
        text: formattedMessage,
        parse_mode: 'HTML', // Enables HTML formatting if needed
      }),
    });

    const data = await response.json();
    
    if (!data.ok) {
      console.error(`❌ Telegram API error: ${data.description}`);
      return { success: false, error: data.description };
    }

    console.log(`✅ Telegram notification sent: ${message.substring(0, 30)}...`);
    return { success: true, data };
  } catch (error) {
    console.error(`❌ Failed to send Telegram notification: ${error.message}`);
    return { success: false, error: error.message };
  }
}

/**
 * Send a trade signal notification
 * @param {Object} signal - The trading signal data
 */
export async function sendSignalAlert(signal) {
  const { index, signal: signalType, entry, stop_loss, target, strike, confidence } = signal;
  
  // Format message with signal details
  const message = `
<b>NEW SIGNAL: ${index} ${signalType}</b>

▶️ Entry: ${entry}
🎯 Target: ${target}
🛑 Stop Loss: ${stop_loss}
💰 Strike: ${strike}
🔍 Confidence: ${(confidence * 100).toFixed(1)}%

Time: ${new Date().toLocaleTimeString()}
`;

  return sendTelegramAlert(message, confidence > 0.85);
}

/**
 * Send trade execution notification
 * @param {Object} trade - The executed trade details
 */
export async function sendTradeExecutionAlert(trade) {
  const { index, signal, entry, lots, strike } = trade;
  
  const message = `
<b>TRADE EXECUTED: ${index} ${signal}</b>

▶️ Entry Price: ${entry}
📊 Lots: ${lots}
💰 Strike: ${strike}

Time: ${new Date().toLocaleTimeString()}
`;

  return sendTelegramAlert(message, true);
}

/**
 * Send trade exit notification
 * @param {Object} trade - The trade exit details
 */
export async function sendTradeExitAlert(trade) {
  const { index, signal, entry, exit, pnl, duration, lots } = trade;
  
  // Calculate profit/loss percentage
  const pnlPercentage = ((exit - entry) / entry * 100 * (signal.includes('PUT') ? -1 : 1)).toFixed(2);
  const isProfitable = pnl > 0;
  
  const message = `
<b>TRADE EXITED: ${index} ${signal}</b>

▶️ Entry: ${entry}
⏹️ Exit: ${exit}
💰 P&L: ${isProfitable ? '✅ +' : '❌ '}${pnl.toFixed(2)} (${pnlPercentage}%)
⏱️ Duration: ${duration}
📊 Lots: ${lots}

Time: ${new Date().toLocaleTimeString()}
`;

  return sendTelegramAlert(message, false);
}

/**
 * Send system status update
 * @param {string} status - The system status message
 * @param {boolean} isError - If true, marks as error condition
 */
export async function sendSystemAlert(status, isError = false) {
  const message = `
<b>${isError ? '❌ SYSTEM ERROR' : '✅ SYSTEM UPDATE'}</b>

${status}

Time: ${new Date().toLocaleTimeString()}
`;

  return sendTelegramAlert(message, isError);
}

export default {
  sendTelegramAlert,
  sendSignalAlert,
  sendTradeExecutionAlert,
  sendTradeExitAlert,
  sendSystemAlert
};