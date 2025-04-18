// File: sambot-frontend/app/signal/components/IndexSelector.tsx
'use client'
import { motion } from 'framer-motion';
import { Activity, Power } from 'lucide-react';

interface IndexSelectorProps {
  index: string;
  isActive: boolean;
  isLoading: boolean;
  signalType?: string;
  entry?: number;
  onClick: () => void;
}

export default function IndexSelector({
  index,
  isActive,
  isLoading,
  signalType,
  entry,
  onClick
}: IndexSelectorProps) {
  const getSignalIcon = (signal: string) => {
    if (signal === 'BUY CALL') return <ArrowUpRight className="w-5 h-5" />;
    if (signal === 'BUY PUT') return <ArrowDownRight className="w-5 h-5" />;
    return <Activity className="w-5 h-5" />;
  };

  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      className={`relative overflow-hidden rounded-xl shadow-sm cursor-pointer transition-all border ${
        isActive
          ? 'border-indigo-300 shadow-lg shadow-indigo-100/50'
          : 'border-gray-200 hover:border-indigo-200'
      }`}
    >
      <button
        onClick={onClick}
        className={`w-full h-full p-4 transition ${
          isActive
            ? 'bg-gradient-to-br from-white to-indigo-50'
            : 'bg-white hover:bg-gray-50'
        }`}
        disabled={isLoading}
      >
        {/* Top Section with Index Name */}
        <div className="flex justify-between items-start mb-2">
          <div>
            <h3 className="text-base font-bold text-gray-900">{index}</h3>
            <p className="text-xs text-gray-500">
              {isActive 
                ? 'Signal Active' 
                : isLoading ? 'Loading...' : 'Click to Activate'}
            </p>
          </div>
          <div className={`h-5 w-5 rounded-full flex items-center justify-center ${
            isActive 
              ? 'bg-indigo-500 text-white' 
              : 'bg-gray-200 text-gray-500'
          }`}>
            <Power className="h-3 w-3" />
          </div>
        </div>
        
        {/* Signal Type Display */}
        {isActive && signalType && (
          <div className="mt-4">
            <div className={`inline-flex items-center px-2.5 py-1.5 rounded-md text-xs font-semibold ${
              signalType === 'BUY CALL'
                ? 'bg-green-100 text-green-800 border border-green-200'
                : signalType === 'BUY PUT'
                  ? 'bg-red-100 text-red-800 border border-red-200'
                  : 'bg-gray-100 text-gray-800 border border-gray-200'
            }`}>
              {getSignalIcon(signalType)}
              <span className="ml-1">{signalType}</span>
            </div>
            
            {/* Entry Point */}
            {signalType !== 'WAIT' && entry && (
              <div className="mt-2 flex justify-between items-center">
                <div className="text-xs text-gray-500">Entry:</div>
                <div className="text-sm font-semibold">{entry}</div>
              </div>
            )}
          </div>
        )}
        
        {/* Loading Indicator */}
        {isLoading && (
          <div className="absolute inset-0 flex items-center justify-center bg-white bg-opacity-80">
            <div className="h-8 w-8 rounded-full border-2 border-indigo-500 border-t-transparent animate-spin"></div>
          </div>
        )}
      </button>
    </motion.div>
  );
}