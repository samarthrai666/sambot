// components/OngoingTrades.jsx
'use client'

import { useState } from 'react';
import { TrendingUp, TrendingDown, DollarSign, Clock, AlertCircle, X } from 'lucide-react';

export default function OngoingTrades({ index, onExitTrade }) {
  const [trades, setTrades] = useState([
    // Mock data - in production this would come from your API
    {
      id: 'trade-1',
      index: 'NIFTY',
      type: 'BUY CALL',
      strike: 22500,
      entry: 22450,
      entryTime: '10:15 AM',
      currentPrice: 22530,
      pnl: 1200,
      pnlPercent: 5.3,
      expiry: '27-APR-2025'
    },
    {
      id: 'trade-2',
      index: 'BANKNIFTY',
      type: 'BUY PUT',
      strike: 48500,
      entry: 48650,
      entryTime: '11:30 AM',
      currentPrice: 48400,
      pnl: 3750,
      pnlPercent: 7.8,
      expiry: '27-APR-2025'
    }
  ]);
  
  // Filter trades for the current index if provided
  const filteredTrades = index ? trades.filter(trade => trade.index === index) : trades;
  
  const handleExitTrade = (trade) => {
    // Remove trade from the list
    setTrades(trades.filter(t => t.id !== trade.id));
    
    // Call the parent handler
    onExitTrade(trade);
  };
  
  if (filteredTrades.length === 0) return null;
  
  return (
    <div className="mb-6">
      <div className="flex justify-between items-center mb-3">
        <h3 className="text-sm font-medium text-gray-500">ONGOING TRADES</h3>
        <span className="text-xs text-gray-500">{filteredTrades.length} active position{filteredTrades.length !== 1 ? 's' : ''}</span>
      </div>
      
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <ul className="divide-y divide-gray-100">
          {filteredTrades.map((trade) => (
            <li key={trade.id} className="p-4">
              <div className="flex justify-between">
                <div>
                  <div className="flex items-center">
                    <div className={`h-8 w-8 rounded-lg flex items-center justify-center ${
                      trade.type === 'BUY CALL' ? 'bg-green-100' : 'bg-red-100'
                    }`}>
                      {trade.type === 'BUY CALL' ? (
                        <TrendingUp className="h-5 w-5 text-green-600" />
                      ) : (
                        <TrendingDown className="h-5 w-5 text-red-600" />
                      )}
                    </div>
                    <div className="ml-3">
                      <h4 className="text-sm font-medium text-gray-900">
                        {trade.index} {trade.type} {trade.strike}
                      </h4>
                      <div className="flex items-center mt-0.5 text-xs text-gray-500">
                        <Clock className="h-3 w-3 mr-1" />
                        Entered at {trade.entryTime}
                      </div>
                    </div>
                  </div>
                  
                  <div className="mt-2 grid grid-cols-2 gap-2 text-xs">
                    <div className="flex items-center">
                      <span className="text-gray-500 mr-1">Entry:</span>
                      <span className="font-medium">{trade.entry}</span>
                    </div>
                    <div className="flex items-center">
                      <span className="text-gray-500 mr-1">Current:</span>
                      <span className="font-medium">{trade.currentPrice}</span>
                    </div>
                    <div className="flex items-center">
                      <span className="text-gray-500 mr-1">Expiry:</span>
                      <span className="font-medium">{trade.expiry}</span>
                    </div>
                  </div>
                </div>
                
                <div className="flex flex-col items-end justify-between">
                  <div className={`px-3 py-1.5 rounded-lg text-sm font-medium ${
                    trade.pnl >= 0 
                      ? 'bg-green-50 text-green-700'
                      : 'bg-red-50 text-red-700'
                  }`}>
                    <div className="flex items-center">
                      <DollarSign className="h-3.5 w-3.5 mr-1" />
                      ₹{Math.abs(trade.pnl).toLocaleString()}
                    </div>
                    <div className="text-xs text-center mt-0.5">
                      {trade.pnl >= 0 ? '+' : '-'}{Math.abs(trade.pnlPercent)}%
                    </div>
                  </div>
                  
                  <button
                    onClick={() => handleExitTrade(trade)}
                    className="mt-auto px-3 py-1.5 border border-gray-200 rounded-md text-xs text-gray-700 hover:bg-gray-50 flex items-center"
                  >
                    <X className="h-3.5 w-3.5 mr-1.5" />
                    Exit Position
                  </button>
                </div>
              </div>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}