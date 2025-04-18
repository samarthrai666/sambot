'use client'
import { useRouter } from 'next/navigation'
import Header from '@/components/Header'
import { useState, useEffect } from 'react'
import { Activity, BarChart2, Brain, TrendingUp, LineChart } from 'lucide-react'

export default function Home() {
  const router = useRouter()
  const [mounted, setMounted] = useState(false)
  const [hoverSignal, setHoverSignal] = useState(false)
  const [hoverMarket, setHoverMarket] = useState(false)
  const [hoverPerformance, setHoverPerformance] = useState(false)
  
  // Animation on mount
  useEffect(() => {
    setMounted(true)
  }, [])

  return (
    <div className="min-h-screen bg-gradient-to-b from-white to-green-50 text-gray-800 overflow-hidden">
      <Header />
      
      {/* Animated background elements */}
      <div className="absolute inset-0 z-0">
        <div className="absolute top-1/4 left-1/3 w-72 h-72 bg-green-400/10 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-1/3 right-1/4 w-96 h-96 bg-emerald-400/10 rounded-full blur-3xl animate-pulse" style={{animationDelay: '1s'}}></div>
        <div className="absolute top-2/3 left-1/2 w-64 h-64 bg-teal-400/10 rounded-full blur-3xl animate-pulse" style={{animationDelay: '2s'}}></div>
        
        {/* Grid lines */}
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPjxwYXR0ZXJuIGlkPSJncmlkIiB3aWR0aD0iODAiIGhlaWdodD0iODAiIHBhdHRlcm5Vbml0cz0idXNlclNwYWNlT25Vc2UiPjxwYXRoIGQ9Ik0gODAgMCBMIDAgMCAwIDgwIiBmaWxsPSJub25lIiBzdHJva2U9IiNlNWU3ZWIiIHN0cm9rZS13aWR0aD0iMC41Ii8+PC9wYXR0ZXJuPjxyZWN0IHdpZHRoPSIxMDAlIiBoZWlnaHQ9IjEwMCUiIGZpbGw9InVybCgjZ3JpZCkiLz48L3N2Zz4=')] opacity-30"></div>
      </div>
      
      <main className="relative z-10 flex flex-col items-center justify-center h-[80vh] gap-8 p-4">
        <div className={`transition-all duration-1000 transform ${mounted ? 'translate-y-0 opacity-100' : 'translate-y-10 opacity-0'}`}>
          <h1 className="text-5xl font-bold mb-2 text-transparent bg-clip-text bg-gradient-to-r from-green-400 to-emerald-600">
            SAMBOT DASHBOARD
          </h1>
          <div className="h-0.5 w-full bg-gradient-to-r from-green-400 to-emerald-600 rounded-full mb-2"></div>
          <p className="text-gray-600 text-center max-w-md mx-auto">
            Advanced algorithmic trading signals and market analysis
          </p>
        </div>
        
        <div className="flex flex-col md:flex-row gap-6 mt-8">
          <button
            className={`relative group overflow-hidden rounded-xl transition-all duration-300 ${mounted ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}
            style={{ transitionDelay: '200ms' }}
            onClick={() => router.push('/signal')}
            onMouseEnter={() => setHoverSignal(true)}
            onMouseLeave={() => setHoverSignal(false)}
          >
            <div className={`absolute inset-0 bg-gradient-to-br from-green-500 to-emerald-600 transform transition-transform duration-500 ${hoverSignal ? 'scale-105' : 'scale-100'}`}></div>
            <div className="absolute inset-0 bg-white/20 opacity-0 group-hover:opacity-100 transition-opacity"></div>
            <div className="absolute inset-0.5 bg-white rounded-lg z-10"></div>
            <div className="relative z-20 px-8 py-4 flex items-center space-x-3">
              <Activity className="w-5 h-5 text-green-600" />
              <span className="font-medium text-gray-800">View Live Signal</span>
              <svg className="w-5 h-5 text-green-600 transform transition-transform group-hover:translate-x-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
              </svg>
            </div>
            <div className="absolute top-0 left-0 w-full h-full bg-gradient-to-r from-transparent via-green-400/20 to-transparent -translate-x-full animate-shimmer"></div>
          </button>
          
          <button
            className={`relative group overflow-hidden rounded-xl transition-all duration-300 ${mounted ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}
            style={{ transitionDelay: '400ms' }}
            onClick={() => router.push('/performance')}
            onMouseEnter={() => setHoverPerformance(true)}
            onMouseLeave={() => setHoverPerformance(false)}
          >
            <div className={`absolute inset-0 bg-gradient-to-br from-purple-500 to-indigo-600 transform transition-transform duration-500 ${hoverPerformance ? 'scale-105' : 'scale-100'}`}></div>
            <div className="absolute inset-0 bg-white/20 opacity-0 group-hover:opacity-100 transition-opacity"></div>
            <div className="absolute inset-0.5 bg-white rounded-lg z-10"></div>
            <div className="relative z-20 px-8 py-4 flex items-center space-x-3">
              <LineChart className="w-5 h-5 text-indigo-600" />
              <span className="font-medium text-gray-800">Performance</span>
              <span className="text-xs px-2 py-0.5 rounded-full bg-indigo-100 text-indigo-700 ml-1">New</span>
            </div>
            <div className="absolute top-0 left-0 w-full h-full bg-gradient-to-r from-transparent via-indigo-400/20 to-transparent -translate-x-full animate-shimmer"></div>
          </button>
          
          <button
            className={`relative group overflow-hidden rounded-xl transition-all duration-300 ${mounted ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}
            style={{ transitionDelay: '600ms' }}
            onClick={() => alert('Market Data Coming Soon')}
            onMouseEnter={() => setHoverMarket(true)}
            onMouseLeave={() => setHoverMarket(false)}
          >
            <div className={`absolute inset-0 bg-gradient-to-br from-teal-500 to-emerald-600 transform transition-transform duration-500 ${hoverMarket ? 'scale-105' : 'scale-100'}`}></div>
            <div className="absolute inset-0 bg-white/20 opacity-0 group-hover:opacity-100 transition-opacity"></div>
            <div className="absolute inset-0.5 bg-white rounded-lg z-10"></div>
            <div className="relative z-20 px-8 py-4 flex items-center space-x-3">
              <BarChart2 className="w-5 h-5 text-teal-600" />
              <span className="font-medium text-gray-800">Market Data</span>
              <span className="text-xs px-2 py-0.5 rounded-full bg-teal-100 text-teal-700 ml-1">Coming Soon</span>
            </div>
            <div className="absolute top-0 left-0 w-full h-full bg-gradient-to-r from-transparent via-teal-400/20 to-transparent -translate-x-full animate-shimmer"></div>
          </button>
        </div>
        
        <div className={`mt-12 flex gap-4 transition-all duration-1000 ${mounted ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`} style={{ transitionDelay: '800ms' }}>
          <div className="flex items-center gap-2 text-sm text-gray-600 border border-green-200 bg-white/80 shadow-sm rounded-full px-4 py-1.5">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            <span>All Systems Online</span>
          </div>
          <div className="text-sm text-gray-600 border border-green-200 bg-white/80 shadow-sm rounded-full px-4 py-1.5">
            Last update: Just now
          </div>
        </div>
      </main>
      
      {/* Add global styles for animations */}
      <style jsx global>{`
        @keyframes shimmer {
          100% {
            transform: translateX(100%);
          }
        }
        .animate-shimmer {
          animation: shimmer 2s infinite;
        }
      `}</style>
    </div>
  )
}