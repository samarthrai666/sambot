'use client'
import { useEffect, useState } from 'react';
import { Power, AlertTriangle, ArrowUpRight, ArrowDownRight, Activity, Target, Shield, Zap } from 'lucide-react';
import Link from 'next/link';
import { motion, AnimatePresence } from 'framer-motion';
import { useRouter } from 'next/navigation';

const indices = ['NIFTY', 'BANKNIFTY', 'SENSEX', 'MIDCAPNIFTY'];

export default function SignalClient() {
  const [signals, setSignals] = useState({});
  const [loadingIndices, setLoadingIndices] = useState([]);
  const [autoExecute, setAutoExecute] = useState({});
  const [executionLogs, setExecutionLogs] = useState({});
  const [selectedTab, setSelectedTab] = useState(null);
  const router = useRouter();

  useEffect(() => {
    const isLoggedIn = localStorage.getItem('sambot-auth');
    if (!isLoggedIn) {
      router.push('/login');
    }
  }, [router]);

  
  useEffect(() => {
    const savedSignals = localStorage.getItem('sambot-signals');
    const savedExec = localStorage.getItem('sambot-auto-execute');
    const savedLogs = localStorage.getItem('sambot-logs');
    if (savedSignals) setSignals(JSON.parse(savedSignals));
    if (savedExec) setAutoExecute(JSON.parse(savedExec));
    if (savedLogs) setExecutionLogs(JSON.parse(savedLogs));
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

  useEffect(() => {
    const interval = setInterval(() => {
      const activeIndices = Object.keys(signals);
      activeIndices.forEach(index => {
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
            }
          })
          .catch(err => console.error(`Error fetching signal for ${index}:`, err));
      });
    }, 30000);
    return () => clearInterval(interval);
  }, [autoExecute]);

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

    fetch(`http://localhost:5050/signals?index=${index}`)
      .then(res => res.json())
      .then(json => {
        setSignals(prev => ({ ...prev, [index]: json }));
        setLoadingIndices(prev => prev.filter(i => i !== index));
        setSelectedTab(index);
      })
      .catch(err => {
        console.error('Fetch error:', err);
        setLoadingIndices(prev => prev.filter(i => i !== index));
      });
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

  return (
    <div className="bg-gradient-to-br from-indigo-50 via-blue-50 to-purple-50 text-gray-800 min-h-screen overflow-hidden">
      {/* Decorative background elements */}
      <div className="fixed inset-0 overflow-hidden z-0">
        <div className="absolute top-0 right-0 w-96 h-96 bg-purple-300 rounded-full filter blur-3xl opacity-20"></div>
        <div className="absolute bottom-0 left-0 w-96 h-96 bg-blue-300 rounded-full filter blur-3xl opacity-20"></div>
        <div className="absolute top-1/2 left-1/2 w-96 h-96 bg-indigo-300 rounded-full filter blur-3xl opacity-10 animate-pulse"></div>
        <div className="grid grid-cols-12 gap-10 absolute inset-0 opacity-10">
          {Array(24).fill(0).map((_, i) => (
            <div key={i} className="h-screen border-r border-indigo-300/30"></div>
          ))}
        </div>
        <div className="grid grid-rows-12 gap-10 absolute inset-0 opacity-10">
          {Array(24).fill(0).map((_, i) => (
            <div key={i} className="w-screen border-b border-indigo-300/30"></div>
          ))}
        </div>
      </div>

      <header className="bg-white/70 backdrop-blur-lg border-b border-indigo-200 py-4 sticky top-0 z-50 shadow-sm">
        <div className="max-w-7xl mx-auto px-6 flex justify-between items-center">
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5 }}
          >
            <Link href="/" className="text-3xl font-bold tracking-widest hover:scale-105 transition-transform flex items-center group">
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600">SAM</span>
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-purple-600">BOT</span>
              <motion.div 
                className="ml-2 w-5 h-5 rounded-full bg-gradient-to-r from-blue-500 to-purple-600"
                animate={{ 
                  boxShadow: ['0 0 0px rgba(79, 70, 229, 0.5)', '0 0 10px rgba(79, 70, 229, 0.8)', '0 0 0px rgba(79, 70, 229, 0.5)'] 
                }}
                transition={{ duration: 2, repeat: Infinity }}
              />
            </Link>
          </motion.div>

          <nav className="space-x-8 text-sm font-medium">
            {['Home', 'Signals', 'Settings'].map((item, index) => (
              <Link 
                key={item} 
                href={item === 'Home' ? '/' : `/${item.toLowerCase()}`}
                className={`relative px-2 py-1 transition-all duration-300 ${
                  item === 'Signals' ? 'text-indigo-700' : 'text-gray-700 hover:text-indigo-700'
                }`}
              >
                <span className="relative z-10">
                  {item === 'Home' && '🏠 '}
                  {item === 'Signals' && '📡 '}
                  {item === 'Settings' && '⚙️ '}
                  {item}
                </span>
                {item === 'Signals' && (
                  <motion.span 
                    className="absolute inset-0 bg-indigo-100 border border-indigo-200 rounded-md -z-0"
                    layoutId="navIndicator"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                  />
                )}
              </Link>
            ))}
          </nav>
        </div>
      </header>

      <main className="max-w-7xl mx-auto p-6 mt-6 space-y-10 relative z-10">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="text-center"
        >
          <h2 className="text-4xl font-bold tracking-wide">
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600">
              SIGNAL TRACKER
            </span>
          </h2>
          <p className="text-indigo-600/70 mt-2">Real-time market signals with AI-powered insights</p>
        </motion.div>

        <motion.div 
          className="grid grid-cols-2 md:grid-cols-4 gap-4"
          variants={{
            hidden: { opacity: 0 },
            show: {
              opacity: 1,
              transition: {
                staggerChildren: 0.1
              }
            }
          }}
          initial="hidden"
          animate="show"
        >
          {indices.map((index) => {
            const isActive = signals[index];
            const signalType = signals[index]?.signal;
            
            return (
              <motion.button
                key={index}
                variants={{
                  hidden: { opacity: 0, y: 20 },
                  show: { opacity: 1, y: 0 }
                }}
                whileHover={{ scale: 1.02, boxShadow: '0 0 15px rgba(79, 70, 229, 0.3)' }}
                onClick={() => handleIndexClick(index)}
                className={`relative overflow-hidden backdrop-blur-sm border rounded-xl shadow text-center font-bold transition flex flex-col items-center justify-center gap-2 p-5 ${
                  isActive
                    ? 'bg-gradient-to-br from-white/80 to-white/60 border-indigo-300 shadow-lg shadow-indigo-100'
                    : 'bg-white/50 border-indigo-100 hover:border-indigo-300'
                }`}
              >
                {isActive ? (
                  <div className="absolute inset-0 bg-gradient-to-br opacity-10"></div>
                ) : null}
                
                <span className="text-lg tracking-wide text-gray-800">
                  {index}
                </span>
                
                {isActive ? (
                  <div className={`flex items-center justify-center px-3 py-1 rounded-full text-xs bg-gradient-to-r ${getSignalColor(signalType)} text-white shadow-md`}>
                    {getSignalIcon(signalType)}
                    <span className="ml-1">{signalType}</span>
                  </div>
                ) : (
                  <span className="text-xs text-indigo-500/70">Click to activate</span>
                )}
                
                {isActive && (
                  <motion.div 
                    className="absolute -inset-1 opacity-20 blur-sm"
                    initial={{ background: `radial-gradient(circle at center, ${signalType === 'BUY CALL' ? '#10b981' : '#ef4444'} 0%, transparent 70%)` }}
                    animate={{ 
                      background: [
                        `radial-gradient(circle at center, ${signalType === 'BUY CALL' ? '#10b981' : '#ef4444'} 0%, transparent 70%)`,
                        `radial-gradient(circle at center, ${signalType === 'BUY CALL' ? '#10b981' : '#ef4444'} 20%, transparent 70%)`,
                        `radial-gradient(circle at center, ${signalType === 'BUY CALL' ? '#10b981' : '#ef4444'} 0%, transparent 70%)`
                      ]
                    }}
                    transition={{ duration: 2, repeat: Infinity }}
                  />
                )}
                
                <Power className={`w-5 h-5 absolute top-2 right-2 ${isActive ? 'text-indigo-500' : 'text-indigo-300'}`} />
              </motion.button>
            );
          })}
        </motion.div>

        <div className="mt-10">
          <AnimatePresence mode="wait">
            {Object.keys(signals).length > 0 ? (
              <motion.div
                key="signals"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="space-y-8"
              >
                <div className="flex space-x-2 overflow-x-auto pb-2 hide-scrollbar">
                  {Object.keys(signals).map(index => (
                    <motion.button
                      key={index}
                      onClick={() => setSelectedTab(index)}
                      className={`px-4 py-2 rounded-lg font-medium relative flex items-center ${
                        selectedTab === index 
                          ? 'text-indigo-900' 
                          : 'text-indigo-500 hover:text-indigo-700'
                      }`}
                      whileHover={{ scale: 1.05 }}
                    >
                      {selectedTab === index && (
                        <motion.div
                          layoutId="activeTab"
                          className="absolute inset-0 bg-gradient-to-r from-indigo-100 to-blue-100 border border-indigo-200 rounded-lg"
                        />
                      )}
                      <span className="relative z-10 flex items-center">
                        {getSignalIcon(signals[index]?.signal)}
                        <span className="ml-2">{index}</span>
                      </span>
                    </motion.button>
                  ))}
                </div>

                <AnimatePresence mode="wait">
                  {selectedTab && signals[selectedTab] && (
                    <motion.div
                      key={selectedTab}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                      transition={{ duration: 0.3 }}
                      className="rounded-2xl overflow-hidden relative backdrop-blur-sm border border-indigo-200 shadow-xl"
                    >
                      <div className="absolute inset-0 bg-gradient-to-br from-white/80 to-indigo-50/90 z-0"></div>
                      
                      <div className="grid grid-cols-1 md:grid-cols-7 gap-0 relative z-10">
                        {/* Main Signal Info */}
                        <div className="md:col-span-5 p-6">
                          <div className="flex justify-between items-center mb-6">
                            <div className="flex items-center">
                              <h3 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-700">
                                {selectedTab}
                              </h3>
                              <div className={`ml-4 px-4 py-1 rounded-full text-sm font-medium bg-gradient-to-r ${getSignalColor(signals[selectedTab].signal)} flex items-center`}>
                                {getSignalIcon(signals[selectedTab].signal)}
                                <span className="ml-2">{signals[selectedTab].signal}</span>
                              </div>
                            </div>
                            
                            <motion.button
                              onClick={() => toggleAutoExecute(selectedTab)}
                              className={`text-sm font-semibold px-4 py-2 rounded-full flex items-center gap-2 transition-all ${
                                autoExecute[selectedTab] 
                                  ? 'bg-gradient-to-r from-green-500 to-emerald-600 text-white shadow-md shadow-green-900/10' 
                                  : 'bg-gray-200 text-gray-700'
                              }`}
                              whileHover={{ scale: 1.05 }}
                              whileTap={{ scale: 0.95 }}
                            >
                              <Zap className="w-4 h-4" />
                              {autoExecute[selectedTab] ? 'Auto Execute ON' : 'Auto Execute OFF'}
                            </motion.button>
                          </div>

                          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div className="space-y-4">
                              <div className="backdrop-blur-sm bg-white/60 rounded-xl p-4 border border-indigo-100 shadow-sm">
                                <h4 className="text-indigo-700 text-sm font-medium mb-3 flex items-center">
                                  <Activity className="w-4 h-4 mr-2" />
                                  TREND ANALYSIS
                                </h4>
                                <p className="text-gray-800 font-medium">{signals[selectedTab].trend}</p>
                              </div>
                              
                              <div className="backdrop-blur-sm bg-white/60 rounded-xl p-4 border border-indigo-100 shadow-sm">
                                <h4 className="text-indigo-700 text-sm font-medium mb-3 flex items-center">
                                  <AlertTriangle className="w-4 h-4 mr-2" />
                                  CONFIDENCE & REASONING
                                </h4>
                                <p className="text-gray-700 text-sm">{signals[selectedTab].confidence_reason}</p>
                              </div>
                            </div>
                            
                            <div className="backdrop-blur-sm bg-white/60 rounded-xl p-4 border border-indigo-100 shadow-sm">
                              <h4 className="text-indigo-700 text-sm font-medium mb-3">PATTERN DETECTION</h4>
                              <ul className="space-y-2">
                                {signals[selectedTab].patterns_detected.map((p, i) => (
                                  <motion.li 
                                    key={i}
                                    initial={{ opacity: 0, x: -10 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    transition={{ delay: i * 0.1 }}
                                    className="bg-indigo-50 px-3 py-2 rounded-lg text-sm flex items-center border border-indigo-100"
                                  >
                                    <span className="w-2 h-2 bg-indigo-500 rounded-full mr-2"></span>
                                    {p}
                                  </motion.li>
                                ))}
                              </ul>
                            </div>
                          </div>
                        </div>
                        
                        {/* Stats Panel */}
                        <div className="md:col-span-2 bg-gradient-to-br from-indigo-100/80 to-blue-100/80 p-6 border-l border-indigo-200">
                          <h4 className="text-indigo-800 text-sm font-medium mb-4 uppercase tracking-wider">Signal Metrics</h4>
                          
                          <div className="space-y-4">
                            <div className="bg-white/70 rounded-xl p-4 border border-indigo-200 shadow-sm">
                              <div className="flex items-center text-xs text-blue-700 mb-1">
                                <Target className="w-3 h-3 mr-1" />
                                ENTRY POINT
                              </div>
                              <p className="text-2xl font-mono font-bold text-blue-700">{signals[selectedTab].entry}</p>
                            </div>
                            
                            <div className="bg-white/70 rounded-xl p-4 border border-indigo-200 shadow-sm">
                              <div className="flex items-center text-xs text-red-700 mb-1">
                                <Shield className="w-3 h-3 mr-1" />
                                STOP LOSS
                              </div>
                              <p className="text-2xl font-mono font-bold text-red-700">{signals[selectedTab].stop_loss}</p>
                            </div>
                            
                            <div className="bg-white/70 rounded-xl p-4 border border-indigo-200 shadow-sm">
                              <div className="flex items-center text-xs text-green-700 mb-1">
                                <Target className="w-3 h-3 mr-1" />
                                TARGET
                              </div>
                              <p className="text-2xl font-mono font-bold text-green-700">{signals[selectedTab].target}</p>
                            </div>
                            
                            <div className="bg-white/70 rounded-xl p-4 border border-indigo-200 shadow-sm">
                              <div className="flex items-center text-xs text-purple-700 mb-1">
                                <Zap className="w-3 h-3 mr-1" />
                                STRIKE
                              </div>
                              <p className="text-2xl font-mono font-bold text-purple-700">{signals[selectedTab].strike}</p>
                            </div>
                          </div>
                        </div>
                      </div>

                      {/* Execution Logs */}
                      {executionLogs[selectedTab]?.length > 0 && (
                        <div className="border-t border-indigo-200 p-6 bg-indigo-50/70">
                          <h4 className="text-indigo-800 text-sm font-medium mb-3 flex items-center">
                            <Activity className="w-4 h-4 mr-2" />
                            EXECUTION LOG
                          </h4>
                          <div className="bg-white/80 rounded-lg border border-indigo-200 p-3 shadow-sm">
                            <ul className="space-y-2 font-mono text-sm">
                              {executionLogs[selectedTab].map((log, i) => (
                                <motion.li 
                                  key={i}
                                  initial={{ opacity: 0 }}
                                  animate={{ opacity: 1 }}
                                  transition={{ delay: i * 0.05 }}
                                  className="text-gray-700 flex items-center"
                                >
                                  <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                                  {log}
                                </motion.li>
                              ))}
                            </ul>
                          </div>
                        </div>
                      )}
                    </motion.div>
                  )}
                </AnimatePresence>
              </motion.div>
            ) : (
              <motion.div 
                key="no-signals"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="text-center py-16"
              >
                <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-indigo-100 mb-4">
                  <Activity className="w-10 h-10 text-indigo-500 opacity-70" />
                </div>
                <h3 className="text-xl font-medium text-indigo-700">No Active Signals</h3>
                <p className="text-indigo-500/70 mt-2">Select an index above to begin tracking signals</p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </main>
      
      {/* Add custom styling for scrollbar hiding */}
      <style jsx global>{`
        .hide-scrollbar::-webkit-scrollbar {
          display: none;
        }
        .hide-scrollbar {
          -ms-overflow-style: none;
          scrollbar-width: none;
        }
      `}</style>
    </div>
  );
