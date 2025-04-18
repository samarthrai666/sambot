// File: sambot-frontend/app/signal/components/NoSignals.tsx
'use client'
import { motion } from 'framer-motion';
import { Activity, PlusCircle } from 'lucide-react';

interface NoSignalsProps {
  indices: string[];
  onActivateIndex: (index: string) => void;
}

export default function NoSignals({ indices, onActivateIndex }: NoSignalsProps) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="bg-white rounded-xl shadow-sm border border-gray-200 p-8 text-center"
    >
      <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-indigo-100 mb-4">
        <Activity className="h-8 w-8 text-indigo-500" />
      </div>
      <h3 className="text-lg font-medium text-gray-900 mb-2">No Active Signals</h3>
      <p className="text-gray-600 max-w-md mx-auto mb-6">
        Select an index above to start monitoring real-time trading signals powered by AI analysis.
      </p>
      <div className="flex flex-wrap gap-4 justify-center">
        {indices.map((index) => (
          <button
            key={index}
            onClick={() => onActivateIndex(index)}
            className="py-2 px-4 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 rounded-lg text-sm font-medium flex items-center transition-colors"
          >
            <PlusCircle className="h-4 w-4 mr-1.5" />
            Activate {index}
          </button>
        ))}
      </div>
    </motion.div>
  );
}