'use client'
import { useEffect, useState } from 'react';
import { 
  Power, AlertTriangle, ArrowUpRight, ArrowDownRight, Activity, 
  Target, Shield, Zap, Clock, TrendingUp, TrendingDown, 
  BarChart2, Eye, X, AlertCircle, ChevronDown, ChevronUp,
  PieChart, Check, BarChart, Calendar, ChevronsUp, ChevronsDown,
  Layers, LineChart, Play, Circle, PlusCircle, Info, Brain
} from 'lucide-react';
import Link from 'next/link';
import { motion, AnimatePresence } from 'framer-motion';
import { useRouter } from 'next/navigation';
import OngoingTrades from '@/components/OngoingTrades';


const indices = ['NIFTY', 'BANKNIFTY', 'SENSEX', 'MIDCAPNIFTY'];

export default function SignalClient() {
  const [signals, setSignals] = useState({});
  const [loadingIndices, setLoadingIndices] = useState([]);
  const [autoExecute, setAutoExecute] = useState({});
  const [executionLogs, setExecutionLogs] = useState({});
  const [selectedTab, setSelectedTab] = useState(null);
  const [showPerformance, setShowPerformance] = useState(false);
  const [marketStatus, setMarketStatus] = useState('open'); // 'open', 'closed', 'pre-market'
  const [optionChainVisible, setOptionChainVisible] = useState(false);
  const [showPatternInfo, setShowPatternInfo] = useState(false);
  const [performanceData, setPerformanceData] = useState({
    total_trades: 0,
    wins: 0,
    losses: 0,
    win_rate: 0,
    net_pnl: 0
  });
  const [marketData, setMarketData] = useState({
    vix: 14.8,
    change: 0.75, 
    sentiment: 'bullish', // 'bullish', 'bearish', 'neutral'
    trend_strength: 68,
  });

  const [activeTrades, setActiveTrades] = useState({});

  const executeManually = (index) => {
    if (!signals[index]) return;
    
    const signal = signals[index];
    const time = new Date().toLocaleTimeString();
    const log = `${time} — Manually executed ${signal.signal} @ ${signal.entry}`;
    
    // Add to execution logs
    setExecutionLogs(prev => ({
      ...prev,
      [index]: [...(prev[index] || []), log]
    }));
    
    // Add to active trades
    const newTrade = {
      id: `trade-${Date.now()}`,
      index: index,
      type: signal.signal,
      strike: signal.strike,
      entry: signal.entry,
      entryTime: time,
      currentPrice: signal.entry,
      pnl: 0,
      pnlPercent: 0,
      expiry: '27-APR-2025'
    };
    
    setActiveTrades(prev => ({
      ...prev,
      [index]: [...(prev[index] || []), newTrade]
    }));
    
    // Update today's performance
    setTodaysPerformance(prev => ({
      ...prev,
      executed: prev.executed + 1
    }));

    // Send notification (add this code)
  fetch('http://localhost:5050/execute', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      index,
      signal: signal.signal,
      entry: signal.entry,
      qty: 1 // Or whatever quantity you want
    })
  }).catch(error => {
    console.error('Error sending execution notification:', error);
    // Continue with the trade even if notification fails
  });
  };
  // Function to handle exiting a trade
  const handleExitTrade = (trade) => {
    // Remove trade from active trades
    setActiveTrades(prev => {
      const updated = { ...prev };
      updated[trade.index] = (updated[trade.index] || []).filter(t => t.id !== trade.id);
      return updated;
    });
    
    // Log the exit
    const time = new Date().toLocaleTimeString();
    const exitPrice = trade.currentPrice;
    const pnl = trade.pnl;
    const log = `${time} — Exited ${trade.type} ${trade.strike} @ ${exitPrice} | P&L: ${pnl >= 0 ? '+' : ''}${pnl}`;
    
    setExecutionLogs(prev => ({
      ...prev,
      [trade.index]: [...(prev[trade.index] || []), log]
    }));

    fetch('http://localhost:5050/exit', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        index: trade.index,
        signal: trade.type,
        entry: trade.entry,
        exit: exitPrice,
        pnl: trade.pnl
      })
    }).catch(error => {
      console.error('Error sending exit notification:', error);
    });
  };

  // Function to handle new trade execution

  const [todaysPerformance, setTodaysPerformance] = useState({
    signals: 5,
    executed: 3,
    wins: 2,
    losses: 1,
    pnl: 1250
  });
  const router = useRouter();

  useEffect(() => {
    const isLoggedIn = localStorage.getItem('sambot-auth');
    if (!isLoggedIn) {
      router.push('/login');
    }
    
    // Initialize current time updater
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);

    return () => clearInterval(timer);
  }, [router]);

  const [currentTime, setCurrentTime] = useState(new Date());
  
  useEffect(() => {
    const savedSignals = localStorage.getItem('sambot-signals');
    const savedExec = localStorage.getItem('sambot-auto-execute');
    const savedLogs = localStorage.getItem('sambot-logs');
    const savedPerf = localStorage.getItem('sambot-performance');
    
    if (savedSignals) setSignals(JSON.parse(savedSignals));
    if (savedExec) setAutoExecute(JSON.parse(savedExec));
    if (savedLogs) setExecutionLogs(JSON.parse(savedLogs));
    if (savedPerf) setPerformanceData(JSON.parse(savedPerf));
    else {
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
  }, []);

  useEffect(() => {
    localStorage.setItem('sambot-signals', JSON.stringify(signals));
  }, [signals]);

  useEffect(() => {
    localStorage.setItem('sambot-auto-execute', JSON.stringify(autoExecute));
  }, [autoExecute]);

  useEffect(() => {
    localStorage.setItem('sambot-logs', JSON.stringify(executionLogs));
  }, [executionLogs]);
  
  // Mock option chain data
  const optionChainData = [
    { strike: 22400, calls: { oi: 1045, change: 128, ltp: 150.25 }, puts: { oi: 987, change: -45, ltp: 95.75 } },
    { strike: 22450, calls: { oi: 1240, change: 220, ltp: 120.50 }, puts: { oi: 1120, change: -120, ltp: 110.25 } },
    { strike: 22500, calls: { oi: 1645, change: 345, ltp: 98.75 }, puts: { oi: 1320, change: -188, ltp: 135.50 } },
    { strike: 22550, calls: { oi: 1345, change: 210, ltp: 80.25 }, puts: { oi: 1562, change: -98, ltp: 165.25 } },
    { strike: 22600, calls: { oi: 1120, change: 178, ltp: 65.50 }, puts: { oi: 1890, change: -35, ltp: 195.75 } },
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      const activeIndices = Object.keys(signals);
      activeIndices.forEach(index => {
        // Comment this out and use mock updates instead
        if (Math.random() > 0.7) { // Occasionally update the data
          const updatedMock = getMockSignalData(index);
          setSignals(prev => ({ ...prev, [index]: updatedMock }));
          
          if (autoExecute[index] && (updatedMock.signal === 'BUY CALL' || updatedMock.signal === 'BUY PUT')) {
            const time = new Date().toLocaleTimeString();
            const log = `${time} — Executed ${updatedMock.signal} @ ${updatedMock.entry}`;
            setExecutionLogs(prev => ({
              ...prev,
              [index]: [...(prev[index] || []), log]
            }));
            
            // Update performance data (mock)
            if (Math.random() > 0.5) {  // Simulate win/loss
              setPerformanceData(prev => ({
                ...prev,
                total_trades: prev.total_trades + 1,
                wins: prev.wins + 1,
                win_rate: Math.round(((prev.wins + 1) / (prev.total_trades + 1)) * 100 * 100) / 100,
                net_pnl: prev.net_pnl + Math.round(Math.random() * 1000)
              }));
            } else {
              setPerformanceData(prev => ({
                ...prev,
                total_trades: prev.total_trades + 1,
                losses: prev.losses + 1,
                win_rate: Math.round((prev.wins / (prev.total_trades + 1)) * 100 * 100) / 100,
                net_pnl: prev.net_pnl - Math.round(Math.random() * 800)
              }));
            }
          }
        }
        
        /* Real API implementation - uncomment when backend is ready
        fetch(`http://localhost:5050/signals?index=${index}`)
          .then(res => res.json())
          .then(json => {
            setSignals(prev => ({ ...prev, [index]: json }));
            if (autoExecute[index] && (json.signal === 'BUY CALL' || json.signal === 'BUY PUT')) {
              const time = new Date().toLocaleTimeString();
              const log = `${time} — Executed ${json.signal} @ ${json.entry}`;
              setExecutionLogs(prev => ({
                ...prev,
                [index]: [...(prev[index] || []), log]
              }));
              
              // Update performance data (mock)
              if (Math.random() > 0.5) {  // Simulate win/loss
                setPerformanceData(prev => ({
                  ...prev,
                  total_trades: prev.total_trades + 1,
                  wins: prev.wins + 1,
                  win_rate: Math.round(((prev.wins + 1) / (prev.total_trades + 1)) * 100 * 100) / 100,
                  net_pnl: prev.net_pnl + Math.round(Math.random() * 1000)
                }));
              } else {
                setPerformanceData(prev => ({
                  ...prev,
                  total_trades: prev.total_trades + 1,
                  losses: prev.losses + 1,
                  win_rate: Math.round((prev.wins / (prev.total_trades + 1)) * 100 * 100) / 100,
                  net_pnl: prev.net_pnl - Math.round(Math.random() * 800)
                }));
              }
            }
          })
          .catch(err => console.error(`Error fetching signal for ${index}:`, err));
        */
      });
    }, 30000);
    return () => clearInterval(interval);
  }, [autoExecute, signals]);

  // Mock signal data for when API is unavailable
  const getMockSignalData = (index) => {
    // Generate different data based on index for variety
    const isBullish = index === 'NIFTY' || index === 'SENSEX';
    const basePrice = index === 'NIFTY' ? 22500 : 
                     index === 'BANKNIFTY' ? 48500 : 
                     index === 'SENSEX' ? 75200 : 24100;
    
    return {
      signal: isBullish ? 'BUY CALL' : 'BUY PUT',
      entry: basePrice,
      stop_loss: isBullish ? basePrice - 120 : basePrice + 130,
      target: isBullish ? basePrice + 240 : basePrice - 250,
      strike: Math.round(basePrice / 50) * 50,
      confidence_reason: `${isBullish ? 'Bullish' : 'Bearish'} momentum detected with ${isBullish ? 'positive' : 'negative'} convergence on multiple timeframes. Strong ${isBullish ? 'support' : 'resistance'} at current levels with increasing volume suggesting continuation.`,
      patterns_detected: [
        isBullish ? 'Bullish Engulfing' : 'Bearish Engulfing',
        isBullish ? 'Golden Cross' : 'Death Cross',
        index === 'NIFTY' ? 'Hammer' : 'Shooting Star'
      ],
      trend: isBullish ? 'Strong uptrend with higher highs and higher lows' : 'Downtrend with lower highs and lower lows'
    };
  };

  const handleIndexClick = (index) => {
    if (signals[index]) {
      const updated = { ...signals };
      delete updated[index];
      setSignals(updated);
      setAutoExecute(prev => ({ ...prev, [index]: false }));
      if (selectedTab === index) setSelectedTab(null);
      return;
    }

    if (loadingIndices.includes(index)) return;
    setLoadingIndices(prev => [...prev, index]);

    // Use mock data directly (comment this out and uncomment the fetch when API is ready)
    setTimeout(() => {
      const mockData = getMockSignalData(index);
      setSignals(prev => ({ ...prev, [index]: mockData }));
      setLoadingIndices(prev => prev.filter(i => i !== index));
      setSelectedTab(index);
      console.log('Using mock data for development');
    }, 800); // Small delay to simulate network request

    // Real API implementation - uncomment when backend is ready
    /*
    fetch(`http://localhost:5050/signals?index=${index}`)
      .then(res => res.json())
      .then(json => {
        setSignals(prev => ({ ...prev, [index]: json }));
        setLoadingIndices(prev => prev.filter(i => i !== index));
        setSelectedTab(index);
      })
      .catch(err => {
        console.error('Fetch error:', err);
        // Use mock data instead when API fails
        const mockData = getMockSignalData(index);
        setSignals(prev => ({ ...prev, [index]: mockData }));
        setLoadingIndices(prev => prev.filter(i => i !== index));
        setSelectedTab(index);
        console.log('Using mock data due to API unavailability');
      });
    */
  };

  const toggleAutoExecute = (index) => {
    setAutoExecute(prev => ({ ...prev, [index]: !prev[index] }));
  };


  const getSignalIcon = (signal) => {
    if (signal === 'BUY CALL') return <ArrowUpRight className="w-5 h-5" />;
    if (signal === 'BUY PUT') return <ArrowDownRight className="w-5 h-5" />;
    return <Activity className="w-5 h-5" />;
  };

  const getSignalColor = (signal) => {
    if (signal === 'BUY CALL') return 'from-green-500 to-emerald-600';
    if (signal === 'BUY PUT') return 'from-red-500 to-rose-600';
    return 'from-yellow-500 to-amber-600';
  };

  const getSentimentColor = (sentiment) => {
    if (sentiment === 'bullish') return 'text-green-600';
    if (sentiment === 'bearish') return 'text-red-600';
    return 'text-amber-600';
  };

  const togglePerformanceView = () => {
    setShowPerformance(!showPerformance);
  };

  const toggleOptionChain = () => {
    setOptionChainVisible(!optionChainVisible);
  };

  const togglePatternInfo = () => {
    setShowPatternInfo(!showPatternInfo);
  };

  return (
    <div className="bg-gradient-to-br from-slate-50 via-gray-50 to-zinc-50 text-gray-800 min-h-screen overflow-hidden">
      {/* Subtle grid background */}
      <div className="fixed inset-0 z-0">
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPjxwYXR0ZXJuIGlkPSJncmlkIiB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHBhdHRlcm5Vbml0cz0idXNlclNwYWNlT25Vc2UiPjxwYXRoIGQ9Ik0gNDAgMCBMIDAgMCAwIDQwIiBmaWxsPSJub25lIiBzdHJva2U9IiNlNWU3ZWIiIHN0cm9rZS13aWR0aD0iMC41Ii8+PC9wYXR0ZXJuPjxyZWN0IHdpZHRoPSIxMDAlIiBoZWlnaHQ9IjEwMCUiIGZpbGw9InVybCgjZ3JpZCkiLz48L3N2Zz4=')] opacity-30"></div>
        
        {/* Subtle gradient accents */}
        <div className="absolute -top-20 -right-20 w-96 h-96 bg-blue-100 rounded-full filter blur-3xl opacity-20"></div>
        <div className="absolute top-1/2 -left-20 w-96 h-96 bg-purple-100 rounded-full filter blur-3xl opacity-20"></div>
        <div className="absolute -bottom-20 right-1/3 w-96 h-96 bg-emerald-100 rounded-full filter blur-3xl opacity-20"></div>
      </div>

      {/* Header */}
      <header className="relative z-10 bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <Link href="/" className="flex items-center">
                <div className="w-9 h-9 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center shadow-md">
                  <Activity className="w-5 h-5 text-white" />
                </div>
                <div className="ml-3">
                  <h1 className="text-xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600">
                    SAMBOT
                  </h1>
                  <p className="text-xs text-gray-500 -mt-1">Signal Monitor</p>
                </div>
              </Link>
            </div>
            
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
                  marketStatus === 'open' 
                    ? 'bg-green-50 border border-green-200' 
                    : marketStatus === 'closed'
                      ? 'bg-red-50 border border-red-200'
                      : 'bg-yellow-50 border border-yellow-200'
                }`}>
                  <div className={`w-2 h-2 rounded-full mr-2 ${
                    marketStatus === 'open' 
                      ? 'bg-green-500 animate-pulse' 
                      : marketStatus === 'closed'
                        ? 'bg-red-500'
                        : 'bg-yellow-500'
                  }`}></div>
                  <span className={`text-sm font-medium ${
                    marketStatus === 'open' 
                      ? 'text-green-700' 
                      : marketStatus === 'closed'
                        ? 'text-red-700'
                        : 'text-yellow-700'
                  }`}>
                    Market {marketStatus === 'pre-market' ? 'Pre-Open' : marketStatus.charAt(0).toUpperCase() + marketStatus.slice(1)}
                  </span>
                </div>
                
                <div className={`flex items-center px-3 py-1.5 rounded-md border border-gray-200 bg-white`}>
                  <span className={`text-sm font-medium ${getSentimentColor(marketData.sentiment)}`}>
                    {marketData.sentiment.charAt(0).toUpperCase() + marketData.sentiment.slice(1)} Sentiment
                  </span>
                  <div className="ml-2 w-1 h-4 bg-gray-200"></div>
                  <span className="ml-2 text-sm font-medium text-gray-700">
                    VIX {marketData.vix}
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
          </div>
        </div>
      </header>

      <main className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Page Title & Today's Summary */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Real-Time Trading Signals</h1>
            <p className="text-gray-600 mt-1">Monitor and execute AI-powered signals for optimal trading</p>
          </div>
          
          {/* Today's Performance Summary */}
          <div className="mt-4 md:mt-0 flex flex-wrap gap-2 md:gap-3">
            <div className="flex items-center bg-white rounded-lg py-1.5 px-3 shadow-sm border border-gray-200">
              <Calendar className="w-4 h-4 text-gray-500 mr-1.5" />
              <span className="text-xs font-medium text-gray-900">Today's Signals: {todaysPerformance.signals}</span>
            </div>
            
            <div className="flex items-center bg-white rounded-lg py-1.5 px-3 shadow-sm border border-gray-200">
              <Check className="w-4 h-4 text-indigo-500 mr-1.5" />
              <span className="text-xs font-medium text-gray-900">Executed: {todaysPerformance.executed}</span>
            </div>
            
            <div className="flex items-center bg-white rounded-lg py-1.5 px-3 shadow-sm border border-gray-200">
              <ChevronsUp className="w-4 h-4 text-green-500 mr-1.5" />
              <span className="text-xs font-medium text-gray-900">Wins: {todaysPerformance.wins}</span>
            </div>
            
            <div className="flex items-center bg-white rounded-lg py-1.5 px-3 shadow-sm border border-gray-200">
              <ChevronsDown className="w-4 h-4 text-red-500 mr-1.5" />
              <span className="text-xs font-medium text-gray-900">Losses: {todaysPerformance.losses}</span>
            </div>
            
            <div className={`flex items-center rounded-lg py-1.5 px-3 shadow-sm border ${
              todaysPerformance.pnl >= 0 
                ? 'bg-green-50 border-green-200 text-green-700' 
                : 'bg-red-50 border-red-200 text-red-700'
            }`}>
              <BarChart className="w-4 h-4 mr-1.5" />
              <span className="text-xs font-medium">P&L: ₹{todaysPerformance.pnl}</span>
            </div>
          </div>
        </div>
        
        {/* Index Selection Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          {indices.map((index) => {
            const isActive = signals[index];
            const signalType = signals[index]?.signal;
            const isLoading = loadingIndices.includes(index);
            
            return (
              <motion.div
                key={index}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className={`relative overflow-hidden rounded-xl shadow-sm cursor-pointer transition-all border ${
                  isActive
                    ? 'border-indigo-300 shadow-lg shadow-indigo-100/50'
                    : 'border-gray-200 hover:border-indigo-200'
                }`}
              >
                <button
                  onClick={() => handleIndexClick(index)}
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
                  {isActive && (
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
                      {signalType !== 'WAIT' && (
                        <div className="mt-2 flex justify-between items-center">
                          <div className="text-xs text-gray-500">Entry:</div>
                          <div className="text-sm font-semibold">{signals[index].entry}</div>
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
          })}
        </div>

        {/* Add this component after the signal details and before any other components */}
        <OngoingTrades 
              index={selectedTab} 
              onExitTrade={handleExitTrade} 
            />
        
        {/* Selected Signal Details */}
        <AnimatePresence mode="wait">
          {selectedTab && signals[selectedTab] && (
            <motion.div
              key={selectedTab}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
              className="mb-8"
            >
              <div className="bg-white rounded-xl shadow-md border border-gray-200 overflow-hidden">
                {/* Header with Signal Type */}
                <div className={`py-4 px-6 border-b border-gray-100 bg-gradient-to-r ${
                  signals[selectedTab].signal === 'BUY CALL'
                    ? 'from-green-50 to-emerald-50'
                    : signals[selectedTab].signal === 'BUY PUT'
                      ? 'from-red-50 to-rose-50'
                      : 'from-gray-50 to-slate-50'
                }`}>
                  <div className="flex flex-col md:flex-row md:items-center md:justify-between">
                    <div className="flex items-center">
                      <div className={`h-10 w-10 rounded-lg flex items-center justify-center ${
                        signals[selectedTab].signal === 'BUY CALL'
                          ? 'bg-green-100'
                          : signals[selectedTab].signal === 'BUY PUT'
                            ? 'bg-red-100'
                            : 'bg-gray-100'
                      }`}>
                        {signals[selectedTab].signal === 'BUY CALL' ? (
                          <ArrowUpRight className={`h-6 w-6 text-green-600`} />
                        ) : signals[selectedTab].signal === 'BUY PUT' ? (
                          <ArrowDownRight className={`h-6 w-6 text-red-600`} />
                        ) : (
                          <Activity className={`h-6 w-6 text-gray-600`} />
                        )}
                      </div>
                      <div className="ml-4">
                        <div className="flex items-center">
                          <h2 className="text-xl font-bold text-gray-900">{selectedTab}</h2>
                          <div className={`ml-3 px-2.5 py-0.5 rounded text-xs font-medium ${
                            signals[selectedTab].signal === 'BUY CALL'
                              ? 'bg-green-100 text-green-800'
                              : signals[selectedTab].signal === 'BUY PUT'
                                ? 'bg-red-100 text-red-800'
                                : 'bg-gray-100 text-gray-800'
                          }`}>
                            {signals[selectedTab].signal}
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
                        onClick={() => toggleAutoExecute(selectedTab)}
                        className={`py-2 px-4 rounded-lg text-sm font-medium flex items-center transition-colors ${
                          autoExecute[selectedTab]
                            ? 'bg-green-600 text-white hover:bg-green-700'
                            : 'bg-white border border-gray-200 text-gray-700 hover:bg-gray-50'
                        }`}
                      >
                        <Zap className={`h-4 w-4 ${autoExecute[selectedTab] ? 'text-white' : 'text-gray-500'} mr-1.5`} />
                        {autoExecute[selectedTab] ? 'Auto: ON' : 'Auto: OFF'}
                      </button>
                      
                      {/* Manual Execute Button */}
                      {signals[selectedTab].signal !== 'WAIT' && (
                        <button
                          onClick={() => executeManually(selectedTab)}
                          className={`py-2 px-4 rounded-lg text-sm font-medium flex items-center ${
                            signals[selectedTab].signal === 'BUY CALL'
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
                          <div className="text-lg font-bold text-red-700">{signals[selectedTab].stop_loss}</div>
                          <div className="text-xs text-red-600 mt-1">
                            {Math.abs(((signals[selectedTab].entry - signals[selectedTab].stop_loss) / signals[selectedTab].entry) * 100).toFixed(1)}% away
                          </div>
                        </div>
                        
                        {/* Entry */}
                        <div className="bg-blue-50 rounded-lg p-3 border border-blue-100">
                          <div className="flex items-center text-xs text-blue-600 mb-1">
                            <Target className="h-3.5 w-3.5 mr-1" />
                            ENTRY
                          </div>
                          <div className="text-lg font-bold text-blue-700">{signals[selectedTab].entry}</div>
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
                          <div className="text-lg font-bold text-green-700">{signals[selectedTab].target}</div>
                          <div className="text-xs text-green-600 mt-1">
                            {Math.abs(((signals[selectedTab].target - signals[selectedTab].entry) / signals[selectedTab].entry) * 100).toFixed(1)}% potential
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    {/* Price Chart (placeholder) */}
                    <div className="mb-6">
                      <div className="flex justify-between items-center mb-3">
                        <h3 className="text-sm font-medium text-gray-500">PRICE CHART</h3>
                        <div className="flex text-xs space-x-2">
                          <button className="px-2 py-1 rounded bg-indigo-100 text-indigo-700">5m</button>
                          <button className="px-2 py-1 rounded">15m</button>
                          <button className="px-2 py-1 rounded">1h</button>
                        </div>
                      </div>
                      <div className="h-64 bg-gray-50 rounded-lg border border-gray-200 flex items-center justify-center">
                        {/* This would be replaced with an actual chart component */}
                        <div className="text-center p-4">
                          <LineChart className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                          <p className="text-gray-500 text-sm">Price chart would render here</p>
                          <p className="text-gray-400 text-xs mt-1">Using real-time OHLC data</p>
                        </div>
                      </div>
                    </div>
                    
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
                        {signals[selectedTab].patterns_detected.map((pattern, idx) => (
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
                      <AnimatePresence>
                        {showPatternInfo && (
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
                              </div>
                            </div>
                          </motion.div>
                        )}
                      </AnimatePresence>
                    </div>
                    
                    {/* Option Chain */}
                    <AnimatePresence>
                      {optionChainVisible && (
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
                                    <tr key={index} className={row.strike === signals[selectedTab].strike ? 'bg-indigo-50' : ''}>
                                      <td className="px-6 py-2 whitespace-nowrap text-sm text-gray-600">{row.calls.oi}</td>
                                      <td className={`px-6 py-2 whitespace-nowrap text-sm ${row.calls.change > 0 ? 'text-green-600' : 'text-red-600'}`}>
                                        {row.calls.change > 0 ? '+' : ''}{row.calls.change}
                                      </td>
                                      <td className="px-6 py-2 whitespace-nowrap text-sm text-gray-900">{row.calls.ltp}</td>
                                      <td className={`px-6 py-2 whitespace-nowrap text-sm font-medium text-center ${row.strike === signals[selectedTab].strike ? 'text-indigo-700 bg-indigo-100 rounded' : 'text-gray-900'}`}>
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
                    
                    {/* Execution Logs */}
                    {executionLogs[selectedTab]?.length > 0 && (
                      <div>
                        <h3 className="text-sm font-medium text-gray-500 mb-3">EXECUTION LOG</h3>
                        <div className="bg-gray-50 rounded-lg border border-gray-200 p-3">
                          <ul className="space-y-2 text-sm">
                            {executionLogs[selectedTab].map((log, i) => (
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
                          {signals[selectedTab].confidence_reason || `
                            Pattern analysis indicates strong ${signals[selectedTab].signal === 'BUY CALL' ? 'bullish' : 'bearish'} momentum, 
                            supported by increasing volume and favorable technical indicators. 
                            RSI at 58.2 shows room for continued movement without immediate reversal risk.
                          `}
                        </p>
                        
                        {/* Key Indicators */}
                        <div className="space-y-2 mt-4">
                          <div className="flex justify-between items-center">
                            <span className="text-xs text-gray-600">Trend Strength:</span>
                            <div className="w-1/2 bg-gray-200 rounded-full h-1.5">
                              <div 
                                className="bg-indigo-600 h-1.5 rounded-full" 
                                style={{ width: `${marketData.trend_strength}%` }}
                              ></div>
                            </div>
                            <span className="text-xs font-medium text-gray-900">{marketData.trend_strength}%</span>
                          </div>
                          <div className="flex justify-between items-center">
                            <span className="text-xs text-gray-600">Volume Analysis:</span>
                            <div className="w-1/2 bg-gray-200 rounded-full h-1.5">
                              <div 
                                className="bg-indigo-600 h-1.5 rounded-full" 
                                style={{ width: `75%` }}
                              ></div>
                            </div>
                            <span className="text-xs font-medium text-gray-900">75%</span>
                          </div>
                          <div className="flex justify-between items-center">
                            <span className="text-xs text-gray-600">Pattern Reliability:</span>
                            <div className="w-1/2 bg-gray-200 rounded-full h-1.5">
                              <div 
                                className="bg-indigo-600 h-1.5 rounded-full" 
                                style={{ width: `82%` }}
                              ></div>
                            </div>
                            <span className="text-xs font-medium text-gray-900">82%</span>
                          </div>
                        </div>
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
                              signals[selectedTab].signal === 'BUY CALL'
                                ? 'text-green-700'
                                : 'text-red-700'
                            }`}>{signals[selectedTab].signal}</span>
                          </div>
                          <div className="flex justify-between items-center">
                            <span className="text-sm text-gray-700">Strike Price:</span>
                            <span className="text-sm font-medium text-gray-900">{signals[selectedTab].strike}</span>
                          </div>
                          <div className="flex justify-between items-center">
                            <span className="text-sm text-gray-700">Expiry:</span>
                            <span className="text-sm font-medium text-gray-900">
                              {new Date().getDate() + 2} {new Date().toLocaleString('default', { month: 'short' })} 2025
                            </span>
                          </div>
                          <div className="flex justify-between items-center">
                            <span className="text-sm text-gray-700">Recommended Lots:</span>
                            <span className="text-sm font-medium text-gray-900">2</span>
                          </div>
                          <div className="flex justify-between items-center">
                            <span className="text-sm text-gray-700">Risk-Reward Ratio:</span>
                            <span className="text-sm font-medium text-green-700">1:2.4</span>
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    {/* Upcoming Events */}
                    <div>
                      <h3 className="text-sm font-medium text-gray-500 mb-3">UPCOMING EVENTS</h3>
                      <div className="bg-amber-50 rounded-lg p-4 border border-amber-100">
                        <div className="flex items-start">
                          <AlertCircle className="h-5 w-5 text-amber-500 flex-shrink-0" />
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
          )}
        </AnimatePresence>
        
        {/* No Signals State */}
        <AnimatePresence>
          {!Object.keys(signals).length && (
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
                    onClick={() => handleIndexClick(index)}
                    className="py-2 px-4 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 rounded-lg text-sm font-medium flex items-center transition-colors"
                  >
                    <PlusCircle className="h-4 w-4 mr-1.5" />
                    Activate {index}
                  </button>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
}