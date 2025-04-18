import { OpenAI } from 'openai';
import dotenv from 'dotenv';

dotenv.config();

// Initialize OpenAI client
const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY || ''
});

/**
 * Get trading signal using OpenAI's LLM
 * @param {Object} marketData - Market data and indicators
 * @returns {Promise<Object>} - LLM decision and reasoning
 */
export async function getLLMSignal(marketData) {
  // Validate OpenAI key
  if (!process.env.OPENAI_API_KEY) {
    console.warn("⚠️ OpenAI API key not found, using mock LLM response");
    return mockLLMResponse(marketData);
  }

  // Format patterns for prompt
  const patterns = marketData.patterns || [];
  const patternText = patterns.length > 0 
    ? patterns.map(p => `- ${p}`).join('\n') 
    : '- No specific patterns detected';

  // Build a detailed prompt
  const prompt = `
You are an expert options trader for the Indian markets, specializing in ${marketData.index || 'NIFTY'}.
Based on this market data, recommend either BUY CALL, BUY PUT, or WAIT. Be precise and justify your choice.

Market Conditions:
- Current Price: ${marketData.price}
- RSI: ${marketData.rsi} ${marketData.rsi > 70 ? '(Overbought)' : marketData.rsi < 30 ? '(Oversold)' : '(Neutral)'}
- MACD: ${marketData.macd > marketData.macd_signal ? 'Bullish' : 'Bearish'} (${marketData.macd.toFixed(2)} vs ${marketData.macd_signal.toFixed(2)})
- Volume: ${marketData.volume}
- VWAP Position: ${marketData.price > marketData.vwap ? 'Above VWAP' : 'Below VWAP'}

Detected Patterns:
${patternText}

Market Trend: ${marketData.trend || 'UNKNOWN'}

Only reply with one of: BUY CALL, BUY PUT, or WAIT as the first line.
Then explain your reasoning in one concise sentence.
`;

  try {
    // Call OpenAI API
    const completion = await openai.chat.completions.create({
      model: process.env.OPENAI_MODEL || 'gpt-3.5-turbo',
      messages: [{ role: 'user', content: prompt }],
      temperature: 0.3,
      max_tokens: 150
    });

    // Parse response
    const response = completion.choices[0].message.content;
    
    // Extract decision and reason
    const lines = response.split('\n').filter(line => line.trim() !== '');
    const decisionLine = lines[0].trim();
    const reasonLines = lines.slice(1);
    
    // Normalize decision
    let decision = '';
    if (decisionLine.includes('BUY CALL')) decision = 'BUY CALL';
    else if (decisionLine.includes('BUY PUT')) decision = 'BUY PUT';
    else decision = 'WAIT';
    
    // Determine confidence based on language
    let confidence = 0.75; // Default
    const reasonText = reasonLines.join(' ');
    
    // Adjust confidence based on certainty markers in the text
    const highConfidenceWords = ['clearly', 'strong', 'definitely', 'evident', 'obvious'];
    const lowConfidenceWords = ['might', 'could', 'possibly', 'uncertain', 'mixed'];
    
    highConfidenceWords.forEach(word => {
      if (reasonText.toLowerCase().includes(word)) confidence += 0.05;
    });
    
    lowConfidenceWords.forEach(word => {
      if (reasonText.toLowerCase().includes(word)) confidence -= 0.05;
    });
    
    // Cap confidence
    confidence = Math.min(Math.max(confidence, 0.5), 0.95);
    
    return {
      decision,
      reason: reasonText,
      confidence: parseFloat(confidence.toFixed(2)),
      model: process.env.OPENAI_MODEL || 'gpt-3.5-turbo'
    };
  } catch (error) {
    console.error("❌ OpenAI API Error:", error.message);
    return {
      decision: "WAIT",
      reason: "Error contacting AI service. Defaulting to WAIT for safety.",
      confidence: 0.5,
      error: error.message
    };
  }
}

/**
 * Generate mock LLM response for testing without API calls
 * @param {Object} marketData - Market data
 * @returns {Object} - Mock LLM response
 */
function mockLLMResponse(marketData) {
  // Simple logic based on RSI
  if (marketData.rsi > 70) {
    return {
      decision: "BUY PUT",
      reason: "RSI is overbought indicating potential reversal.",
      confidence: 0.8,
      model: "mock-model"
    };
  } else if (marketData.rsi < 30) {
    return {
      decision: "BUY CALL",
      reason: "RSI is oversold indicating potential upward movement.",
      confidence: 0.8,
      model: "mock-model"
    };
  } else {
    // Check MACD
    if (marketData.macd > marketData.macd_signal) {
      return {
        decision: "BUY CALL",
        reason: "MACD is above signal line showing bullish momentum.",
        confidence: 0.7,
        model: "mock-model"
      };
    } else {
      return {
        decision: "BUY PUT",
        reason: "MACD is below signal line showing bearish momentum.",
        confidence: 0.7,
        model: "mock-model"
      };
    }
  }
}

/**
 * Analyze market sentiment from news headlines
 * @param {Array<string>} headlines - Array of recent news headlines
 * @returns {Promise<Object>} - Sentiment analysis
 */
export async function analyzeMarketSentiment(headlines) {
  // Validate input and API key
  if (!headlines || headlines.length === 0) {
    return { sentiment: 'neutral', score: 0.5 };
  }
  
  if (!process.env.OPENAI_API_KEY) {
    console.warn("⚠️ OpenAI API key not found, using mock sentiment analysis");
    return { sentiment: 'neutral', score: 0.5, confidence: 0.5 };
  }
  
  const prompt = `
As a financial market sentiment analyzer for Indian markets, review these recent headlines:

${headlines.map((h, i) => `${i+1}. ${h}`).join('\n')}

Analyze the overall market sentiment from these headlines.
Rate the sentiment from -1 (extremely bearish) to +1 (extremely bullish).

Respond with ONLY a JSON object with these fields:
- sentiment: "bearish", "neutral", or "bullish"
- score: a number between -1 and 1
- reasoning: brief explanation (1-2 sentences)
- confidence: a number between 0 and 1
`;

  try {
    const completion = await openai.chat.completions.create({
      model: process.env.OPENAI_MODEL || 'gpt-3.5-turbo',
      messages: [{ role: 'user', content: prompt }],
      temperature: 0.3,
      response_format: { type: "json_object" }
    });
    
    // Parse JSON response
    return JSON.parse(completion.choices[0].message.content);
  } catch (error) {
    console.error("❌ OpenAI API Error:", error.message);
    return { 
      sentiment: 'neutral', 
      score: 0,
      confidence: 0.5,
      error: error.message
    };
  }
}

export default {
  getLLMSignal,
  analyzeMarketSentiment
};