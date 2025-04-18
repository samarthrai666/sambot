import { OpenAI } from 'openai';
import dotenv from 'dotenv';

dotenv.config();

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY
});

export async function getLLMSignal(marketData) {
  const prompt = `
You are an expert options trader. Based on this market data, recommend either BUY CALL, BUY PUT, or WAIT. Be precise and justify your choice.

Market Conditions:
- RSI: ${marketData.rsi}
- MACD: ${marketData.macd > marketData.macd_signal ? 'Bullish' : 'Bearish'}
- Volume: ${marketData.volume}
- VWAP Position: ${marketData.price > marketData.vwap ? 'Above' : 'Below'}
- Pattern: ${marketData.patterns.join(', ')}
- Trend: ${marketData.trend}

Only reply with one of: BUY CALL, BUY PUT, or WAIT
Then explain your reasoning in one short sentence.
`;

  const completion = await openai.chat.completions.create({
    model: 'gpt-3.5-turbo',
    messages: [{ role: 'user', content: prompt }],
    temperature: 0.3
  });

  const response = completion.choices[0].message.content;
  const [decisionLine, ...rest] = response.split('\n');
  return {
    decision: decisionLine.trim(),
    reason: rest.join(' ').trim()
  };
}
