// File: sambot-frontend/app/signal/components/MarketStatus.tsx
'use client'
import Link from 'next/link';
import { Clock } from 'lucide-react';

interface MarketStatusProps {
  currentTime: Date;
  status: string;  // 'open', 'closed', 'pre-market'
  sentiment: string;  // 'bullish', 'bearish', 'neutral'
  vix: number;
}

export default function MarketStatus({ 
  currentTime, 
  status, 
  sentiment, 
  vix 
}: MarketStatusProps) {
  const getSentimentColor = (sentiment: string) => {
    if (sentiment === 'bullish') return 'text-green-600';
    if (sentiment === 'bearish') return 'text-red-600';
    return 'text-amber-600';
  };

  return (
    <div className="flex items-center space-x-4">
      {/* Market Status */}
      <div className="hidden md:flex items-center space-x-4">
        <div className="flex items-center px-3 py-1.5 rounded-md border border-gray-200 bg-white">
          <Clock className="w-4 h-4 text-gray-500 mr-2" />
          <span className="text-sm font-medium text-gray-700">
            {currentTime.toLocaleTimeString()}
          </span>
        </div>
        
        <div className={`flex items-center px-3 py-1.5 rounded-md ${
          status === 'open' 
            ? 'bg-green-50 border border-green-200' 
            : status === 'closed'
              ? 'bg-red-50 border border-red-200'
              : 'bg-yellow-50 border border-yellow-200'
        }`}>
          <div className={`w-2 h-2 rounded-full mr-2 ${
            status === 'open' 
              ? 'bg-green-500 animate-pulse' 
              : status === 'closed'
                ? 'bg-red-500'
                : 'bg-yellow-500'
          }`}></div>
          <span className={`text-sm font-medium ${
            status === 'open' 
              ? 'text-green-700' 
              : status === 'closed'
                ? 'text-red-700'
                : 'text-yellow-700'
          }`}>
            Market {status === 'pre-market' ? 'Pre-Open' : status.charAt(0).toUpperCase() + status.slice(1)}
          </span>
        </div>
        
        <div className={`flex items-center px-3 py-1.5 rounded-md border border-gray-200 bg-white`}>
          <span className={`text-sm font-medium ${getSentimentColor(sentiment)}`}>
            {sentiment.charAt(0).toUpperCase() + sentiment.slice(1)} Sentiment
          </span>
          <div className="ml-2 w-1 h-4 bg-gray-200"></div>
          <span className="ml-2 text-sm font-medium text-gray-700">
            VIX {vix}
          </span>
        </div>
      </div>
      
      {/* Navigation Links */}
      <nav className="hidden md:flex space-x-1">
        <Link 
          href="/"
          className="px-3 py-2 text-sm font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors"
        >
          Dashboard
        </Link>
        <Link 
          href="/signal"
          className="px-3 py-2 text-sm font-medium text-indigo-700 bg-indigo-50 rounded-md transition-colors"
        >
          Signals
        </Link>
        <Link 
          href="/performance"
          className="px-3 py-2 text-sm font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors"
        >
          Performance
        </Link>
      </nav>
      
      {/* User Profile Link (placeholder) */}
      <div className="relative">
        <button className="h-8 w-8 rounded-full bg-indigo-100 flex items-center justify-center text-indigo-700 font-medium">
          S
        </button>
      </div>
    </div>
  );
}