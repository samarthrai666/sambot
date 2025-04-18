'use client'

import { useRouter } from 'next/navigation'
import { Bot, Brain, Activity, BarChart2 } from 'lucide-react'
import { useState, useEffect } from 'react'

export default function Header() {
  const router = useRouter()
  const [mounted, setMounted] = useState(false)
  
  useEffect(() => {
    setMounted(true)
  }, [])

  return (
    <header className="relative overflow-hidden">
      {/* Background gradient and patterns */}
      <div className="absolute inset-0 bg-gradient-to-r from-green-50 via-white to-green-50"></div>
      <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPjxwYXR0ZXJuIGlkPSJncmlkIiB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHBhdHRlcm5Vbml0cz0idXNlclNwYWNlT25Vc2UiPjxwYXRoIGQ9Ik0gNDAgMCBMIDAgMCAwIDQwIiBmaWxsPSJub25lIiBzdHJva2U9IiNlNWU3ZWIiIHN0cm9rZS13aWR0aD0iMC41Ii8+PC9wYXR0ZXJuPjxyZWN0IHdpZHRoPSIxMDAlIiBoZWlnaHQ9IjEwMCUiIGZpbGw9InVybCgjZ3JpZCkiLz48L3N2Zz4=')] opacity-30"></div>
      
      {/* Main header content */}
      <div 
        className="relative flex items-center justify-between px-6 py-3 cursor-pointer"
        onClick={() => router.push('/')}
      >
        {/* Logo and title */}
        <div className="flex items-center gap-3">
          <div className="relative">
            <div className={`absolute -inset-1 bg-gradient-to-r from-green-400 to-emerald-500 rounded-full blur-sm opacity-70 transition-opacity duration-500 ${mounted ? 'opacity-70' : 'opacity-0'}`}></div>
            <div className="relative flex items-center justify-center w-12 h-12 bg-white rounded-full border border-green-200 shadow-sm">
              <Bot className="w-6 h-6 text-emerald-600" />
            </div>
          </div>
          <div>
            <h1 className="text-transparent bg-clip-text bg-gradient-to-r from-green-600 to-emerald-700 text-2xl font-bold tracking-tight flex items-center">
              SAMBOT
              <span className="ml-2 text-emerald-500">🧠</span>
            </h1>
            <div className="text-xs text-gray-500 -mt-1 font-normal">Advanced Trading Intelligence</div>
          </div>
        </div>
        
        {/* Navigation */}
        <nav className="hidden md:flex items-center gap-6">
          <NavButton icon={<Activity className="w-4 h-4" />} label="Live Signal" onClick={() => router.push('/signal')} active={false} />
          <NavButton icon={<BarChart2 className="w-4 h-4" />} label="Market Data" onClick={() => alert('Coming Soon')} active={false} />
          <NavButton icon={<Brain className="w-4 h-4" />} label="AI Insights" onClick={() => alert('Coming Soon')} active={false} />
        </nav>
        
        {/* Status indicator */}
        <div className="hidden md:flex items-center gap-2">
          <div className="flex items-center gap-2 text-xs font-medium text-gray-600 border border-green-200 bg-white/80 shadow-sm rounded-full px-3 py-1">
            <div className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse"></div>
            <span>System Online</span>
          </div>
        </div>
      </div>
      
      {/* Highlight bar at bottom */}
      <div className="h-0.5 w-full bg-gradient-to-r from-green-400 to-emerald-500"></div>
    </header>
  )
}

// Helper component for navigation buttons
function NavButton({ icon, label, onClick, active }) {
  return (
    <button 
      onClick={onClick}
      className={`group flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium rounded-md transition-all
        ${active 
          ? 'text-emerald-700 bg-emerald-50' 
          : 'text-gray-600 hover:text-emerald-600 hover:bg-green-50'}`}
    >
      <span className={`transition-colors ${active ? 'text-emerald-500' : 'text-gray-400 group-hover:text-emerald-400'}`}>
        {icon}
      </span>
      {label}
    </button>
  )
}