'use client'

import { useEffect, useState } from 'react';
import Header from '@/components/Header';
import { LineChart, BarChart, Percent, TrendingUp, TrendingDown, DollarSign, Activity, Calendar, Clock, ArrowRight, Users, Brain } from 'lucide-react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { useRouter } from 'next/navigation';

export default function PerformanceClient() {
  const [mounted, setMounted] = useState(false);
  const [performanceData, setPerformanceData] = useState({
    total_trades: 0,
    wins: 0,
    losses: 0,
    win_rate: 0,
    net_pnl: 0
  });
  const [timeframe, setTimeframe] = useState('week');
  const [tradeHistory, setTradeHistory] = useState([]);
  const router = useRouter();

  useEffect(() => {
    const isLoggedIn = localStorage.getItem('sambot-auth');
    if (!isLoggedIn) {
      router.push('/login');
    }

    setMounted(true);
    
    // Load saved performance data
    const savedPerf = localStorage.getItem('sambot-performance');
    if (savedPerf) {
      setPerformanceData(JSON.parse(savedPerf));
    } else {
      // Sample performance data
      const samplePerf = {
        total_trades: 24,
        wins: 16,
        losses: 8,
        win_rate: 66.67,
        net_pnl: 14250
      };
      setPerformanceData(samplePerf);
      localStorage.setItem('sambot-performance', JSON.stringify(samplePerf));
    }

    // Generate sample trade history
    generateSampleTradeHistory();
  }, [router]);

  const generateSampleTradeHistory = () => {
    const history = [];
    const indices = ['NIFTY', 'BANKNIFTY', 'SENSEX', 'MIDCAPNIFTY'];
    const signals = ['BUY CALL', 'BUY PUT'];
    
    // Generate 20 sample trades
    for (let i = 0; i < 20; i++) {
      const index = indices[Math.floor(Math.random() * indices.length)];
      const signal = signals[Math.floor(Math.random() * signals.length)];
      const isProfit = Math.random() > 0.4;
      const pnl = isProfit 
        ? Math.round(Math.random() * 1500) + 500 
        : -1 * (Math.round(Math.random() * 1000) + 300);
      
      // Random date in the last 30 days
      const date = new Date();
      date.setDate(date.getDate() - Math.floor(Math.random() * 30));
      
      history.push({
        id: i + 1,
        timestamp: date.toISOString(),
        index,
        signal,
        entry: Math.round(22000 + Math.random() * 1000),
        exit: Math.round(22000 + Math.random() * 1000),
        pnl,
        confidence: Math.round(Math.random() * 30) + 70
      });
    }
    
    // Sort by timestamp, most recent first
    history.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
    setTradeHistory(history);
  };

  const getChartData = () => {
    // This would normally come from an API
    return {
      labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Today'],
      data: [2500, -1200, 3400, 1800, -800, 4000]
    };
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-indigo-50 to-blue-50 text-gray-800">
      <Header />
      
      {/* Background elements */}
      <div className="fixed inset-0 z-0">
        <div className="absolute top-0 right-0 w-96 h-96 bg-indigo-200 rounded-full filter blur-3xl opacity-20"></div>
        <div className="absolute bottom-0 left-0 w-96 h-96 bg-blue-200 rounded-full filter blur-3xl opacity-20"></div>
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPjxwYXR0ZXJuIGlkPSJncmlkIiB3aWR0aD0iODAiIGhlaWdodD0iODAiIHBhdHRlcm5Vbml0cz0idXNlclNwYWNlT25Vc2UiPjxwYXRoIGQ9Ik0gODAgMCBMIDAgMCAwIDgwIiBmaWxsPSJub25lIiBzdHJva2U9IiNlNWU3ZWIiIHN0cm9rZS13aWR0aD0iMC41Ii8+PC9wYXR0ZXJuPjxyZWN0IHdpZHRoPSIxMDAlIiBoZWlnaHQ9IjEwMCUiIGZpbGw9InVybCgjZ3JpZCkiLz48L3N2Zz4=')] opacity-30"></div>
      </div>
      
      <main className="relative z-10 max-w-7xl mx-auto p-6 pt-12">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <h1 className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-700 to-indigo-700 mb-2">
            Performance Dashboard
          </h1>
          <p className="text-indigo-600/70 mb-10">
            Track your trading performance and optimize your strategy
          </p>
        </motion.div>
        
        {/* Stats Cards */}
        <motion.div 
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-10"
          variants={{
            hidden: { opacity: 0 },
            show: {
              opacity: 1,
              transition: { staggerChildren: 0.1 }
            }
          }}
          initial="hidden"
          animate="show"
        >
          <motion.div
            variants={{
              hidden: { opacity: 0, y: 20 },
              show: { opacity: 1, y: 0 }
            }}
            className="bg-white rounded-xl shadow-lg p-6 border border-indigo-100"
          >
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-medium text-indigo-800">Total Trades</h3>
              <Activity className="w-5 h-5 text-indigo-500" />
            </div>
            <p className="text-3xl font-bold text-gray-900">{performanceData.total_trades}</p>
            <div className="mt-2 text-xs text-indigo-600/70">
              Last 30 days
            </div>
          </motion.div>
          
          <motion.div
            variants={{
              hidden: { opacity: 0, y: 20 },
              show: { opacity: 1, y: 0 }
            }}
            className="bg-white rounded-xl shadow-lg p-6 border border-indigo-100"
          >
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-medium text-green-800">Win Rate</h3>
              <Percent className="w-5 h-5 text-green-500" />
            </div>
            <p className="text-3xl font-bold text-gray-900">{performanceData.win_rate}%</p>
            <div className="mt-2 flex items-center text-xs text-green-600">
              <TrendingUp className="w-3 h-3 mr-1" />
              <span>+3.2% vs previous period</span>
            </div>
          </motion.div>
          
          <motion.div
            variants={{
              hidden: { opacity: 0, y: 20 },
              show: { opacity: 1, y: 0 }
            }}
            className="bg-white rounded-xl shadow-lg p-6 border border-indigo-100"
          >
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-medium text-indigo-800">Win/Loss Ratio</h3>
              <div className="flex bg-indigo-100 rounded-full p-1">
                <TrendingUp className="w-4 h-4 text-green-500" />
                <TrendingDown className="w-4 h-4 text-red-500" />
              </div>
            </div>
            <p className="text-3xl font-bold text-gray-900">{(performanceData.wins / (performanceData.losses || 1)).toFixed(2)}</p>
            <div className="mt-2 text-xs text-indigo-600/70">
              {performanceData.wins} wins / {performanceData.losses} losses
            </div>
          </motion.div>
          
          <motion.div
            variants={{
              hidden: { opacity: 0, y: 20 },
              show: { opacity: 1, y: 0 }
            }}
            className={`bg-white rounded-xl shadow-lg p-6 border ${
              performanceData.net_pnl >= 0 ? 'border-green-100' : 'border-red-100'
            }`}
          >
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-medium text-gray-800">Net P&L</h3>
              <DollarSign className={`w-5 h-5 ${
                performanceData.net_pnl >= 0 ? 'text-green-500' : 'text-red-500'
              }`} />
            </div>
            <p className={`text-3xl font-bold ${
              performanceData.net_pnl >= 0 ? 'text-green-600' : 'text-red-600'
            }`}>
              ₹{performanceData.net_pnl.toLocaleString()}
            </p>
            <div className="mt-2 flex items-center text-xs text-gray-600">
              <Clock className="w-3 h-3 mr-1" />
              <span>Updated just now</span>
            </div>
          </motion.div>
        </motion.div>
        
        {/* Chart Section */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="md:col-span-2 bg-white rounded-xl shadow-lg p-6 border border-indigo-100"
          >
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-lg font-medium text-gray-800">P&L Performance</h3>
              
              <div className="flex bg-indigo-50 rounded-lg overflow-hidden">
                {['week', 'month', 'year'].map((period) => (
                  <button
                    key={period}
                    onClick={() => setTimeframe(period)}
                    className={`px-3 py-1 text-xs font-medium ${
                      timeframe === period 
                        ? 'bg-indigo-600 text-white' 
                        : 'text-indigo-600 hover:bg-indigo-100'
                    }`}
                  >
                    {period.charAt(0).toUpperCase() + period.slice(1)}
                  </button>
                ))}
              </div>
            </div>
            
            <div className="h-64 flex items-center justify-center">
              {/* This would be a real chart component */}
              <div className="w-full h-full relative">
                <div className="absolute inset-x-0 bottom-0 h-px bg-gray-200"></div>
                <div className="absolute inset-y-0 left-0 w-px bg-gray-200"></div>
                
                <div className="relative h-full flex items-end justify-between">
                  {getChartData().data.map((value, i) => (
                    <div key={i} className="flex flex-col items-center">
                      <div 
                        className={`w-10 rounded-t-md ${value >= 0 ? 'bg-green-500' : 'bg-red-500'}`}
                        style={{ 
                          height: `${Math.abs(value) / 50}px`,
                          maxHeight: '200px'
                        }}
                      ></div>
                      <span className="text-xs mt-1 text-gray-600">{getChartData().labels[i]}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </motion.div>
          
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="bg-white rounded-xl shadow-lg p-6 border border-indigo-100"
          >
            <h3 className="text-lg font-medium text-gray-800 mb-4">Trade Distribution</h3>
            
            <div className="space-y-4">
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-indigo-800">NIFTY</span>
                  <span className="font-medium">48%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2.5">
                  <div className="bg-indigo-600 h-2.5 rounded-full" style={{ width: '48%' }}></div>
                </div>
              </div>
              
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-indigo-800">BANKNIFTY</span>
                  <span className="font-medium">32%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2.5">
                  <div className="bg-indigo-600 h-2.5 rounded-full" style={{ width: '32%' }}></div>
                </div>
              </div>
              
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-indigo-800">SENSEX</span>
                  <span className="font-medium">12%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2.5">
                  <div className="bg-indigo-600 h-2.5 rounded-full" style={{ width: '12%' }}></div>
                </div>
              </div>
              
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-indigo-800">MIDCAPNIFTY</span>
                  <span className="font-medium">8%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2.5">
                  <div className="bg-indigo-600 h-2.5 rounded-full" style={{ width: '8%' }}></div>
                </div>
              </div>
            </div>
            
            <div className="mt-6 pt-4 border-t border-gray-100">
              <h4 className="text-sm font-medium text-gray-700 mb-2">Signal Types</h4>
              <div className="flex gap-4">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                  <span className="text-xs text-gray-600">BUY CALL: 58%</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                  <span className="text-xs text-gray-600">BUY PUT: 42%</span>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
        
        {/* Trade History */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="bg-white rounded-xl shadow-lg p-6 border border-indigo-100 mb-10"
        >
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-lg font-medium text-gray-800">Recent Trades</h3>
            <button className="text-sm text-indigo-600 hover:text-indigo-800 flex items-center">
              <span>View all</span>
              <ArrowRight className="w-4 h-4 ml-1" />
            </button>
          </div>
          
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 px-2 text-sm font-medium text-gray-500">Date</th>
                  <th className="text-left py-3 px-2 text-sm font-medium text-gray-500">Index</th>
                  <th className="text-left py-3 px-2 text-sm font-medium text-gray-500">Signal</th>
                  <th className="text-left py-3 px-2 text-sm font-medium text-gray-500">Entry</th>
                  <th className="text-left py-3 px-2 text-sm font-medium text-gray-500">Exit</th>
                  <th className="text-left py-3 px-2 text-sm font-medium text-gray-500">P&L</th>
                  <th className="text-left py-3 px-2 text-sm font-medium text-gray-500">Confidence</th>
                </tr>
              </thead>
              <tbody>
                {tradeHistory.slice(0, 5).map((trade) => (
                  <tr key={trade.id} className="border-b border-gray-50 hover:bg-indigo-50/30">
                    <td className="py-3 px-2 text-sm text-gray-600">
                      {new Date(trade.timestamp).toLocaleDateString()}
                    </td>
                    <td className="py-3 px-2 text-sm font-medium text-gray-900">{trade.index}</td>
                    <td className="py-3 px-2">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        trade.signal === 'BUY CALL' 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {trade.signal}
                      </span>
                    </td>
                    <td className="py-3 px-2 text-sm text-gray-600">{trade.entry}</td>
                    <td className="py-3 px-2 text-sm text-gray-600">{trade.exit}</td>
                    <td className={`py-3 px-2 text-sm font-medium ${
                      trade.pnl >= 0 ? 'text-green-600' : 'text-red-600'
                    }`}>
                      ₹{trade.pnl}
                    </td>
                    <td className="py-3 px-2">
                      <div className="flex items-center">
                        <div className="w-full bg-gray-200 rounded-full h-1.5 mr-2">
                          <div 
                            className={`h-1.5 rounded-full ${
                              trade.confidence > 80 ? 'bg-green-500' : 
                              trade.confidence > 70 ? 'bg-yellow-500' : 'bg-red-500'
                            }`} 
                            style={{ width: `${trade.confidence}%` }}
                          ></div>
                        </div>
                        <span className="text-xs text-gray-600">{trade.confidence}%</span>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </motion.div>
        
        {/* Additional Insights */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-10">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
            className="bg-white rounded-xl shadow-lg p-6 border border-indigo-100"
          >
            <h3 className="text-lg font-medium text-gray-800 mb-4">Best Performing Patterns</h3>
            <div className="space-y-4">
              <div className="flex justify-between items-center p-3 bg-green-50 rounded-lg">
                <div>
                  <h4 className="font-medium text-green-800">Bullish Engulfing</h4>
                  <p className="text-xs text-green-600">24 trades, 82% success rate</p>
                </div>
                <span className="text-lg font-bold text-green-600">+₹8,450</span>
              </div>
              
              <div className="flex justify-between items-center p-3 bg-green-50 rounded-lg">
                <div>
                  <h4 className="font-medium text-green-800">Hammer</h4>
                  <p className="text-xs text-green-600">12 trades, 75% success rate</p>
                </div>
                <span className="text-lg font-bold text-green-600">+₹5,280</span>
              </div>
              
              <div className="flex justify-between items-center p-3 bg-indigo-50 rounded-lg">
                <div>
                  <h4 className="font-medium text-indigo-800">Morning Star</h4>
                  <p className="text-xs text-indigo-600">8 trades, 62% success rate</p>
                </div>
                <span className="text-lg font-bold text-indigo-600">+₹2,750</span>
              </div>
            </div>
          </motion.div>
          
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.7 }}
            className="bg-white rounded-xl shadow-lg p-6 border border-indigo-100"
          >
            <h3 className="text-lg font-medium text-gray-800 mb-4">Performance Over Time</h3>
            
            <div className="flex items-center justify-center h-64">
              {/* Placeholder for line chart */}
              <div className="w-full h-48 relative">
                <div className="absolute inset-x-0 bottom-0 h-px bg-gray-200"></div>
                <div className="absolute inset-y-0 left-0 w-px bg-gray-200"></div>
                
                {/* Line chart simulation */}
                <svg viewBox="0 0 300 100" className="w-full h-full overflow-visible">
                  <linearGradient id="gradient" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" stopColor="rgba(79, 70, 229, 0.2)" />
                    <stop offset="100%" stopColor="rgba(79, 70, 229, 0)" />
                  </linearGradient>
                  
                  {/* Area */}
                  <path 
                    d="M0,70 L50,60 L100,80 L150,30 L200,40 L250,20 L300,50 L300,100 L0,100 Z" 
                    fill="url(#gradient)" 
                  />
                  
                  {/* Line */}
                  <path 
                    d="M0,70 L50,60 L100,80 L150,30 L200,40 L250,20 L300,50" 
                    fill="none" 
                    stroke="#4f46e5" 
                    strokeWidth="2" 
                  />
                  
                  {/* Points */}
                  {[
                    [0, 70], [50, 60], [100, 80], [150, 30], 
                    [200, 40], [250, 20], [300, 50]
                  ].map(([x, y], i) => (
                    <circle 
                      key={i} 
                      cx={x} 
                      cy={y} 
                      r="3" 
                      fill="white" 
                      stroke="#4f46e5" 
                      strokeWidth="2" 
                    />
                  ))}
                </svg>
              </div>
            </div>
            
            <div className="flex justify-between mt-2 text-xs text-gray-500">
              <span>Apr 1</span>
              <span>Apr 8</span>
              <span>Apr 15</span>
              <span>Today</span>
            </div>
          </motion.div>
        </div>
        
        {/* AI Insights */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8 }}
          className="bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl shadow-lg p-6 mb-10 text-white"
        >
          <div className="flex items-start justify-between mb-4">
            <h3 className="text-lg font-medium">AI-Powered Insights</h3>
            <Brain className="w-5 h-5 text-indigo-200" />
          </div>
          
          <div className="space-y-4">
            <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4">
              <h4 className="font-medium mb-2 text-indigo-100">Trading Pattern Analysis</h4>
              <p className="text-sm text-indigo-50">
                Your win rate increases by 18% when trading NIFTY options during the first hour of market open. 
                Consider focusing more on morning momentum strategies.
              </p>
            </div>
            
            <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4">
              <h4 className="font-medium mb-2 text-indigo-100">Risk Management</h4>
              <p className="text-sm text-indigo-50">
                Your average loss (-₹950) is higher than your average win (+₹780).
                Consider tightening stop-losses to improve your risk-reward ratio.
              </p>
            </div>
            
            <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4">
              <h4 className="font-medium mb-2 text-indigo-100">Market Correlation</h4>
              <p className="text-sm text-indigo-50">
                Your performance shows a strong correlation with market volatility (VIX).
                Lower VIX environments are yielding significantly better results for your strategy.
              </p>
            </div>
          </div>
        </motion.div>
      </main>
    </div>
  );
}