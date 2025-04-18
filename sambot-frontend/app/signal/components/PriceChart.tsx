// File: sambot-frontend/app/signal/components/PriceChart.tsx
'use client'
import { LineChart } from 'lucide-react';
import { useState } from 'react';

export default function PriceChart() {
  const [timeframe, setTimeframe] = useState('5m');
  
  const handleTimeframeChange = (tf: string) => {
    setTimeframe(tf);
  };

  return (
    <div className="mb-6">
      <div className="flex justify-between items-center mb-3">
        <h3 className="text-sm font-medium text-gray-500">PRICE CHART</h3>
        <div className="flex text-xs space-x-2">
          <button 
            className={`px-2 py-1 rounded ${timeframe === '5m' ? 'bg-indigo-100 text-indigo-700' : ''}`}
            onClick={() => handleTimeframeChange('5m')}
          >
            5m
          </button>
          <button 
            className={`px-2 py-1 rounded ${timeframe === '15m' ? 'bg-indigo-100 text-indigo-700' : ''}`}
            onClick={() => handleTimeframeChange('15m')}
          >
            15m
          </button>
          <button 
            className={`px-2 py-1 rounded ${timeframe === '1h' ? 'bg-indigo-100 text-indigo-700' : ''}`}
            onClick={() => handleTimeframeChange('1h')}
          >
            1h
          </button>
        </div>
      </div>
      <div className="h-64 bg-gray-50 rounded-lg border border-gray-200 flex items-center justify-center">
        {/* This would be replaced with an actual chart component like Recharts */}
        <div className="text-center p-4">
          <LineChart className="h-8 w-8 text-gray-400 mx-auto mb-2" />
          <p className="text-gray-500 text-sm">Price chart would render here</p>
          <p className="text-gray-400 text-xs mt-1">Using {timeframe} OHLC data</p>
        </div>
      </div>
    </div>
  );
}