// File: sambot-frontend/app/signal/components/OptionChain.tsx
'use client'
import { motion, AnimatePresence } from 'framer-motion';
import { Info } from 'lucide-react';
import { useState, useEffect } from 'react';

interface OptionChainProps {
  isVisible: boolean;
  selectedStrike: number;
}

interface OptionData {
  strike: number;
  calls: {
    oi: number;
    change: number;
    ltp: number;
  };
  puts: {
    oi: number;
    change: number;
    ltp: number;
  };
}

export default function OptionChain({ isVisible, selectedStrike }: OptionChainProps) {
  const [optionChainData, setOptionChainData] = useState<OptionData[]>([]);

  // Load mock data for now - in production this would be fetched from an API
  useEffect(() => {
    const mockData = [
      { strike: 22400, calls: { oi: 1045, change: 128, ltp: 150.25 }, puts: { oi: 987, change: -45, ltp: 95.75 } },
      { strike: 22450, calls: { oi: 1240, change: 220, ltp: 120.50 }, puts: { oi: 1120, change: -120, ltp: 110.25 } },
      { strike: 22500, calls: { oi: 1645, change: 345, ltp: 98.75 }, puts: { oi: 1320, change: -188, ltp: 135.50 } },
      { strike: 22550, calls: { oi: 1345, change: 210, ltp: 80.25 }, puts: { oi: 1562, change: -98, ltp: 165.25 } },
      { strike: 22600, calls: { oi: 1120, change: 178, ltp: 65.50 }, puts: { oi: 1890, change: -35, ltp: 195.75 } }
    ];
    setOptionChainData(mockData);
  }, []);

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          exit={{ opacity: 0, height: 0 }}
          className="overflow-hidden"
        >
          <div className="mb-6">
            <h3 className="text-sm font-medium text-gray-500 mb-3">OPTION CHAIN</h3>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">CALLS</th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">OI Chg</th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">LTP</th>
                    <th scope="col" className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">STRIKE</th>
                    <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">LTP</th>
                    <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">OI Chg</th>
                    <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">PUTS</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {optionChainData.map((row, index) => (
                    <tr key={index} className={row.strike === selectedStrike ? 'bg-indigo-50' : ''}>
                      <td className="px-6 py-2 whitespace-nowrap text-sm text-gray-600">{row.calls.oi}</td>
                      <td className={`px-6 py-2 whitespace-nowrap text-sm ${row.calls.change > 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {row.calls.change > 0 ? '+' : ''}{row.calls.change}
                      </td>
                      <td className="px-6 py-2 whitespace-nowrap text-sm text-gray-900">{row.calls.ltp}</td>
                      <td className={`px-6 py-2 whitespace-nowrap text-sm font-medium text-center ${row.strike === selectedStrike ? 'text-indigo-700 bg-indigo-100 rounded' : 'text-gray-900'}`}>
                        {row.strike}
                      </td>
                      <td className="px-6 py-2 whitespace-nowrap text-sm text-gray-900 text-right">{row.puts.ltp}</td>
                      <td className={`px-6 py-2 whitespace-nowrap text-sm text-right ${row.puts.change > 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {row.puts.change > 0 ? '+' : ''}{row.puts.change}
                      </td>
                      <td className="px-6 py-2 whitespace-nowrap text-sm text-gray-600 text-right">{row.puts.oi}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="mt-2 text-xs text-gray-500 flex items-center justify-end">
              <Info className="h-3 w-3 mr-1" />
              Highlighted row indicates the recommended strike price.
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}