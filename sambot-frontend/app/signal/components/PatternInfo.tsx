// File: sambot-frontend/app/signal/components/PatternInfo.tsx
'use client'
import { motion, AnimatePresence } from 'framer-motion';

interface PatternInfoProps {
  isVisible: boolean;
}

export default function PatternInfo({ isVisible }: PatternInfoProps) {
  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          exit={{ opacity: 0, height: 0 }}
          className="overflow-hidden"
        >
          <div className="mt-3 bg-white border border-indigo-100 rounded-lg p-3 text-xs text-gray-600">
            <p className="font-medium text-indigo-700 mb-1">What are candlestick patterns?</p>
            <p>Candlestick patterns are visual formations created by price movements on a chart. They help traders identify potential reversals, continuations, or market sentiment shifts.</p>
            <div className="mt-2 space-y-1">
              <p><span className="font-medium text-gray-800">Bullish Engulfing:</span> A larger bullish candle completely engulfs the previous bearish candle, suggesting a potential upward reversal.</p>
              <p><span className="font-medium text-gray-800">Hammer:</span> A bullish reversal pattern with a small body and long lower shadow, indicating buying pressure after a decline.</p>
              <p><span className="font-medium text-gray-800">Doji:</span> Candles with very small bodies, suggesting indecision in the market.</p>
              <p><span className="font-medium text-gray-800">Morning Star:</span> A three-candle bullish reversal pattern with a small middle candle, signaling a potential trend change.</p>
              <p><span className="font-medium text-gray-800">Shooting Star:</span> A bearish reversal pattern with a small body and long upper shadow, suggesting selling pressure after an advance.</p>
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}