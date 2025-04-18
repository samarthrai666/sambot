'use client';

import { useRouter } from 'next/navigation';
import { useState, useEffect } from 'react';
import { Bot, Lock, User, ArrowRight } from 'lucide-react';

const LoginPage = () => {
  const router = useRouter();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();

    if (username === 'admin' && password === 'Shiva') {
      localStorage.setItem('sambot-auth', 'true');
      router.push('/signal');
    } else {
      setError('Invalid credentials 🤖');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-green-50 via-white to-emerald-50 relative overflow-hidden">
      {/* Background elements */}
      <div className="absolute inset-0">
        <div className="absolute top-1/4 left-1/3 w-72 h-72 bg-green-300/10 rounded-full blur-3xl"></div>
        <div className="absolute bottom-1/3 right-1/4 w-96 h-96 bg-emerald-300/10 rounded-full blur-3xl"></div>
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPjxwYXR0ZXJuIGlkPSJncmlkIiB3aWR0aD0iODAiIGhlaWdodD0iODAiIHBhdHRlcm5Vbml0cz0idXNlclNwYWNlT25Vc2UiPjxwYXRoIGQ9Ik0gODAgMCBMIDAgMCAwIDgwIiBmaWxsPSJub25lIiBzdHJva2U9IiNlNWU3ZWIiIHN0cm9rZS13aWR0aD0iMC41Ii8+PC9wYXR0ZXJuPjxyZWN0IHdpZHRoPSIxMDAlIiBoZWlnaHQ9IjEwMCUiIGZpbGw9InVybCgjZ3JpZCkiLz48L3N2Zz4=')] opacity-30"></div>
      </div>
      
      {/* Login card */}
      <div className={`relative z-10 bg-white rounded-xl shadow-lg p-8 w-full max-w-md border border-green-100 transform transition-all duration-700 ${mounted ? 'translate-y-0 opacity-100' : 'translate-y-8 opacity-0'}`}>
        {/* Logo */}
        <div className="flex justify-center mb-6">
          <div className="relative">
            <div className="absolute -inset-2 bg-gradient-to-r from-green-400 to-emerald-500 rounded-full blur-sm opacity-70"></div>
            <div className="relative flex items-center justify-center w-16 h-16 bg-white rounded-full border border-green-200 shadow-sm">
              <Bot className="w-8 h-8 text-emerald-600" />
            </div>
          </div>
        </div>
        
        {/* Title */}
        <h2 className="text-2xl font-bold text-center text-transparent bg-clip-text bg-gradient-to-r from-green-600 to-emerald-700 mb-2">SAMBOT ACCESS</h2>
        <p className="text-gray-500 text-center text-sm mb-6">Enter your credentials to continue</p>
        
        {/* Error message */}
        {error && (
          <div className="bg-red-50 border border-red-100 rounded-lg p-3 mb-4 flex items-center justify-center">
            <p className="text-red-600 text-sm">{error}</p>
          </div>
        )}
        
        {/* Login form */}
        <form onSubmit={handleLogin} className="space-y-4">
          <div className="relative">
            <label className="block text-sm font-medium text-gray-700 mb-1 ml-1">Username</label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <User className="h-4 w-4 text-gray-400" />
              </div>
              <input
                type="text"
                className="w-full pl-10 pr-3 py-2.5 border border-gray-200 rounded-lg focus:ring-2 focus:ring-green-400 focus:border-green-400 transition-colors"
                placeholder="Enter username"
                value={username}
                onChange={e => setUsername(e.target.value)}
                required
              />
            </div>
          </div>
          
          <div className="relative">
            <label className="block text-sm font-medium text-gray-700 mb-1 ml-1">Password</label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Lock className="h-4 w-4 text-gray-400" />
              </div>
              <input
                type="password"
                className="w-full pl-10 pr-3 py-2.5 border border-gray-200 rounded-lg focus:ring-2 focus:ring-green-400 focus:border-green-400 transition-colors"
                placeholder="Enter password"
                value={password}
                onChange={e => setPassword(e.target.value)}
                required
              />
            </div>
          </div>
          
          <button
            type="submit"
            className="w-full mt-6 px-4 py-2.5 rounded-lg relative overflow-hidden group"
          >
            <div className="absolute inset-0 bg-gradient-to-r from-green-500 to-emerald-600 transition-transform duration-300 group-hover:scale-105"></div>
            <div className="absolute inset-0 bg-white/20 opacity-0 group-hover:opacity-100 transition-opacity"></div>
            <span className="relative flex items-center justify-center text-white font-medium">
              Access Dashboard
              <ArrowRight className="w-4 h-4 ml-2 transform transition-transform group-hover:translate-x-1" />
            </span>
          </button>
        </form>
        
        {/* System status */}
        <div className="mt-8 flex justify-center">
          <div className="flex items-center gap-2 text-xs text-gray-500 border border-gray-200 rounded-full px-3 py-1">
            <div className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse"></div>
            <span>System Ready</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;