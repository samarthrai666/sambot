// File: sambot-frontend/app/signal/components/SignalDetails.tsx
'use client'
import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  ArrowUpRight, ArrowDownRight, Target, Shield, Zap, Play, 
  Layers, Info, Activity, LineChart, Brain
} from 'lucide-react';
import OptionChain from './OptionChain';
import PatternInfo from './PatternInfo';
import PriceChart from './PriceChart';

interface SignalDetailsProps {
  index: string;
  signal: any; // Ideally this would have a proper type
  autoExecute: boolean;
  executionLogs: string[];
  onToggleAutoExecute: () => void;
  onExecuteManually: () => void;
}

export default function SignalDetails({
  index,
  signal,
  autoExecute,
  executionLogs,
  onToggleAutoExecute,
  onExecuteManually
}: SignalDetailsProps) {
  const [optionChainVisible, setOptionChainVisible] = useState(false);
  const [showPatternInfo, setShowPatternInfo] = useState(false);

  const toggleOptionChain = () => {
    setOptionChainVisible(!optionChainVisible);
  };

  const togglePatternInfo = () => {
    setShowPatternInfo(!showPatternInfo);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.3 }}
      className="mb-8"
    >
      <div className="bg-white rounded-xl shadow-md border border-gray-200 overflow-hidden">
        {/* Header with Signal Type */}
        <div className={`py-4 px-6 border-b border-gray-100 bg-gradient-to-r ${
          signal.signal === 'BUY CALL'
            ? 'from-green-50 to-emerald-50'
            : signal.signal === 'BUY PUT'
              ? 'from-red-50 to-rose-50'
              : 'from-gray-50 to-slate-50'
        }`}>
          <div className="flex flex-col md:flex-row md:items-center md:justify-between">
            <div className="flex items-center">
              <div className={`h-10 w-10 rounded-lg flex items-center justify-center ${
                signal.signal === 'BUY CALL'
                  ? 'bg-green-100'
                  : signal.signal === 'BUY PUT'
                    ? 'bg-red-100'
                    : 'bg-gray-100'
              }`}>
                {signal.signal === 'BUY CALL' ? (
                  <ArrowUpRight className={`h-6 w-6 text-green-600`} />
                ) : signal.signal === 'BUY PUT' ? (
                  <ArrowDownRight className={`h-6 w-6 text-red-600`} />
                ) : (
                  <Activity className={`h-6 w-6 text-gray-600`} />
                )}
              </div>
              <div className="ml-4">
                <div className="flex items-center">
                  <h2 className="text-xl font-bold text-gray-900">{index}</h2>
                  <div className={`ml-3 px-2.5 py-0.5 rounded text-xs font-medium ${
                    signal.signal === 'BUY CALL'
                      ? 'bg-green-100 text-green-800'
                      : signal.signal === 'BUY PUT'
                        ? 'bg-red-100 text-red-800'
                        : 'bg-gray-100 text-gray-800'
                  }`}>
                    {signal.signal}
                  </div>
                </div>
                <p className="text-sm text-gray-600 mt-0.5">
                  Last updated: {new Date().toLocaleTimeString()}
                </p>
              </div>
            </div>
            
            <div className="mt-4 md:mt-0 flex flex-wrap gap-2">
              {/* Auto-Execute Toggle */}
              <button
                onClick={onToggleAutoExecute}
                className={`py-2 px-4 rounded-lg text-sm font-medium flex items-center transition-colors ${
                  autoExecute
                    ? 'bg-green-600 text-white hover:bg-green-700'
                    : 'bg-white border border-gray-200 text-gray-700 hover:bg-gray-50'
                }`}
              >
                <Zap className={`h-4 w-4 ${autoExecute ? 'text-white' : 'text-gray-500'} mr-1.5`} />
                {autoExecute ? 'Auto: ON' : 'Auto: OFF'}
              </button>
              
              {/* Manual Execute Button */}
              {signal.signal !== 'WAIT' && (
                <button
                  onClick={onExecuteManually}
                  className={`py-2 px-4 rounded-lg text-sm font-medium flex items-center ${
                    signal.signal === 'BUY CALL'
                      ? 'bg-green-600 text-white hover:bg-green-700'
                      : 'bg-red-600 text-white hover:bg-red-700'
                  }`}
                >
                  <Play className="h-4 w-4 text-white mr-1.5" />
                  Execute Now
                </button>
              )}
              
              {/* Option Chain Toggle */}
              <button
                onClick={toggleOptionChain}
                className="py-2 px-4 rounded-lg text-sm font-medium flex items-center bg-white border border-gray-200 text-gray-700 hover:bg-gray-50"
              >
                <Layers className="h-4 w-4 text-gray-500 mr-1.5" />
                {optionChainVisible ? 'Hide Chain' : 'Show Chain'}
              </button>
            </div>
          </div>
        </div>
        
        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-0">
          {/* Left Panel - Signal Details & Chart */}
          <div className="col-span-2 p-6 border-b lg:border-b-0 lg:border-r border-gray-200">
            {/* Price Levels */}
            <div className="mb-6">
              <h3 className="text-sm font-medium text-gray-500 mb-3">PRICE LEVELS</h3>
              <div className="grid grid-cols-3 gap-4">
                {/* Stop Loss */}
                <div className="bg-red-50 rounded-lg p-3 border border-red-100">
                  <div className="flex items-center text-xs text-red-600 mb-1">
                    <Shield className="h-3.5 w-3.5 mr-1" />
                    STOP LOSS
                  </div>
                  <div className="text-lg font-bold text-red-700">{signal.stop_loss}</div>
                  <div className="text-xs text-red-600 mt-1">
                    {Math.abs(((signal.entry - signal.stop_loss) / signal.entry) * 100).toFixed(1)}% away
                  </div>
                </div>
                
                {/* Entry */}
                <div className="bg-blue-50 rounded-lg p-3 border border-blue-100">
                  <div className="flex items-center text-xs text-blue-600 mb-1">
                    <Target className="h-3.5 w-3.5 mr-1" />
                    ENTRY
                  </div>
                  <div className="text-lg font-bold text-blue-700">{signal.entry}</div>
                  <div className="text-xs text-blue-600 mt-1">
                    Current Price
                  </div>
                </div>
                
                {/* Target */}
                <div className="bg-green-50 rounded-lg p-3 border border-green-100">
                  <div className="flex items-center text-xs text-green-600 mb-1">
                    <Target className="h-3.5 w-3.5 mr-1" />
                    TARGET
                  </div>
                  <div className="text-lg font-bold text-green-700">{signal.target}</div>
                  <div className="text-xs text-green-600 mt-1">
                    {Math.abs(((signal.target - signal.entry) / signal.entry) * 100).toFixed(1)}% potential
                  </div>
                </div>
              </div>
            </div>
            
            {/* Price Chart */}
            <PriceChart />
            
            {/* Pattern Detection */}
            <div className="mb-6">
              <div className="flex justify-between items-center mb-3">
                <h3 className="text-sm font-medium text-gray-500">PATTERN DETECTION</h3>
                <button 
                  onClick={togglePatternInfo}
                  className="text-xs text-indigo-600 flex items-center"
                >
                  <Info className="h-3.5 w-3.5 mr-1" />
                  {showPatternInfo ? 'Hide Info' : 'Show Info'}
                </button>
              </div>
              
              <div className="space-y-2">
                {signal.patterns_detected && signal.patterns_detected.map((pattern: string, idx: number) => (
                  <div 
                    key={idx}
                    className="bg-indigo-50 px-3 py-2 rounded-lg text-sm flex items-center border border-indigo-100"
                  >
                    <div className="w-2 h-2 bg-indigo-500 rounded-full mr-2"></div>
                    <span className="text-gray-800">{pattern}</span>
                  </div>
                ))}
              </div>
              
              {/* Pattern Information */}
              <PatternInfo isVisible={showPatternInfo} />
            </div>
            
            {/* Option Chain */}
            <OptionChain 
              isVisible={optionChainVisible} 
              selectedStrike={signal.strike} 
            />
            
            {/* Execution Logs */}
            {executionLogs?.length > 0 && (
              <div>
                <h3 className="text-sm font-medium text-gray-500 mb-3">EXECUTION LOG</h3>
                <div className="bg-gray-50 rounded-lg border border-gray-200 p-3">
                  <ul className="space-y-2 text-sm">
                    {executionLogs.map((log, i) => (
                      <motion.li 
                        key={i}
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: i * 0.05 }}
                        className="text-gray-700 flex items-center"
                      >
                        <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                        {log}
                      </motion.li>
                    ))}
                  </ul>
                </div>
              </div>
            )}
          </div>
          
          {/* Right Panel - AI Analysis */}
          <div className="p-6">
            {/* Confidence Score */}
            <div className="mb-6">
              <h3 className="text-sm font-medium text-gray-500 mb-3">CONFIDENCE SCORE</h3>
              <div className="flex flex-col items-center bg-indigo-50 rounded-lg p-4 border border-indigo-100">
                {/* Circular Progress */}
                <div className="relative h-28 w-28 mb-2">
                  <svg className="h-full w-full" viewBox="0 0 100 100">
                    {/* Background Circle */}
                    <circle 
                      cx="50" cy="50" r="40" 
                      fill="none" 
                      stroke="#e0e7ff" 
                      strokeWidth="8"
                    />
                    
                    {/* Progress Circle */}
                    <circle 
                      cx="50" cy="50" r="40" 
                      fill="none" 
                      stroke="#4f46e5" 
                      strokeWidth="8"
                      strokeDasharray="251.2"
                      strokeDashoffset={251.2 - (251.2 * 0.85)}
                      transform="rotate(-90 50 50)"
                    />
                  </svg>
                  <div className="absolute inset-0 flex items-center justify-center flex-col">
                    <span className="text-2xl font-bold text-indigo-700">85%</span>
                    <span className="text-xs text-indigo-600">Confidence</span>
                  </div>
                </div>
                
                <p className="text-sm text-gray-700 text-center">
                  Based on pattern strength, market conditions, and historical performance.
                </p>
              </div>
            </div>
            
            {/* AI Reasoning */}
            <div className="mb-6">
              <h3 className="text-sm font-medium text-gray-500 mb-3">AI REASONING</h3>
              <div className="bg-gradient-to-br from-indigo-50 to-purple-50 rounded-lg p-4 border border-indigo-100">
                <div className="flex items-start mb-3">
                  <div className="h-8 w-8 rounded-full bg-indigo-100 flex items-center justify-center flex-shrink-0">
                    <Brain className="h-5 w-5 text-indigo-600" />
                  </div>
                  <div className="ml-3">
                    <h4 className="text-sm font-medium text-gray-900">Signal Analysis</h4>
                    <p className="text-xs text-gray-600">Based on multiple factors</p>
                  </div>
                </div>
                
                <p className="text-sm text-gray-700 mb-3">
                  {signal.confidence_reason || `
                    Pattern analysis indicates strong ${signal.signal === 'BUY CALL' ? 'bullish' : 'bearish'} momentum, 
                    supported by increasing volume and favorable technical indicators. 
                    RSI at 58.2 shows room for continued movement without immediate reversal risk.
                  `}
                </p>
                
                {/* Key Indicators visualization would go here */}
              </div>
            </div>
            
            {/* Strategy Details */}
            <div className="mb-6">
              <h3 className="text-sm font-medium text-gray-500 mb-3">STRATEGY DETAILS</h3>
              <div className="bg-white rounded-lg p-4 border border-gray-200">
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-700">Signal Type:</span>
                    <span className={`text-sm font-medium ${
                      signal.signal === 'BUY CALL'
                        ? 'text-green-700'
                        : 'text-red-700'
                    }`}>{signal.signal}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-700">Strike Price:</span>
                    <span className="text-sm font-medium text-gray-900">{signal.strike}</span>
                  </div>
                  {/* Additional strategy details here */}
                </div>
              </div>
            </div>
            
            {/* Market Events */}
            <div>
              <h3 className="text-sm font-medium text-gray-500 mb-3">UPCOMING EVENTS</h3>
              <div className="bg-amber-50 rounded-lg p-4 border border-amber-100">
                <div className="flex items-start">
                  <Info className="h-5 w-5 text-amber-500 flex-shrink-0" />
                  <div className="ml-3">
                    <h4 className="text-sm font-medium text-gray-900">Market Events</h4>
                    <p className="text-xs text-gray-700 mt-1">
                      RBI Monetary Policy announcement at 11:45 AM today may impact market volatility.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
}