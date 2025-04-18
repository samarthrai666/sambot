// File: sambot-frontend/app/signal/components/PerformanceSummary.tsx
'use client'
import { Calendar, Check, ChevronsUp, ChevronsDown, BarChart } from 'lucide-react';

interface PerformanceData {
  signals: number;
  executed: number;
  wins: number;
  losses: number;
  pnl: number;
}

interface PerformanceSummaryProps {
  performance: PerformanceData;
}

export default function PerformanceSummary({ performance }: PerformanceSummaryProps) {
  return (
    <div className="mt-4 md:mt-0 flex flex-wrap gap-2 md:gap-3">
      <div className="flex items-center bg-white rounded-lg py-1.5 px-3 shadow-sm border border-gray-200">
        <Calendar className="w-4 h-4 text-gray-500 mr-1.5" />
        <span className="text-xs font-medium text-gray-900">Today's Signals: {performance.signals}</span>
      </div>
      
      <div className="flex items-center bg-white rounded-lg py-1.5 px-3 shadow-sm border border-gray-200">
        <Check className="w-4 h-4 text-indigo-500 mr-1.5" />
        <span className="text-xs font-medium text-gray-900">Executed: {performance.executed}</span>
      </div>
      
      <div className="flex items-center bg-white rounded-lg py-1.5 px-3 shadow-sm border border-gray-200">
        <ChevronsUp className="w-4 h-4 text-green-500 mr-1.5" />
        <span className="text-xs font-medium text-gray-900">Wins: {performance.wins}</span>
      </div>
      
      <div className="flex items-center bg-white rounded-lg py-1.5 px-3 shadow-sm border border-gray-200">
        <ChevronsDown className="w-4 h-4 text-red-500 mr-1.5" />
        <span className="text-xs font-medium text-gray-900">Losses: {performance.losses}</span>
      </div>
      
      <div className={`flex items-center rounded-lg py-1.5 px-3 shadow-sm border ${
        performance.pnl >= 0 
          ? 'bg-green-50 border-green-200 text-green-700' 
          : 'bg-red-50 border-red-200 text-red-700'
      }`}>
        <BarChart className="w-4 h-4 mr-1.5" />
        <span className="text-xs font-medium">P&L: ₹{performance.pnl}</span>
      </div>
    </div>
  );
}