'use client'

import { useState, useEffect } from 'react'
import { Github, Database, Zap, Search, ArrowRight, ExternalLink, Play, ChevronRight, Globe, Cpu, Network } from 'lucide-react'
import Link from 'next/link'

export default function Home() {
  const [isLoading, setIsLoading] = useState(false)
  const [isVisible, setIsVisible] = useState(false)

  useEffect(() => {
    setIsVisible(true)
  }, [])

  const handleGitHubLogin = () => {
    setIsLoading(true)
    // Redirect to GitHub OAuth
    const clientId = process.env.NEXT_PUBLIC_GITHUB_CLIENT_ID || 'your_client_id'
    const redirectUri = encodeURIComponent(window.location.origin + '/auth/callback')
    const scope = 'repo'
    const state = Math.random().toString(36).substring(7)
    
    window.location.href = `https://github.com/login/oauth/authorize?client_id=${clientId}&redirect_uri=${redirectUri}&scope=${scope}&state=${state}`
  }

  const handleGetStarted = () => {
    const element = document.getElementById('features')
    element?.scrollIntoView({ behavior: 'smooth' })
  }

  const handleViewDemo = () => {
    window.open('https://your-railway-backend.railway.app/api', '_blank')
  }

  return (
    <main className="min-h-screen bg-black text-white">
      {/* Header */}
      <nav className="border-b border-gray-800 bg-black fixed w-full z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-purple-500 rounded flex items-center justify-center">
                <Database className="h-5 w-5 text-white" />
              </div>
              <span className="text-xl font-semibold text-white">Quilt</span>
            </div>
            <div className="hidden md:flex items-center space-x-8">
              <button 
                onClick={handleGetStarted}
                className="text-gray-400 hover:text-white transition-colors"
              >
                Product
              </button>
              <button 
                onClick={() => document.getElementById('how-it-works')?.scrollIntoView({ behavior: 'smooth' })}
                className="text-gray-400 hover:text-white transition-colors"
              >
                Docs
              </button>
              <Link 
                href="https://github.com/YuvDwi/Quilt" 
                target="_blank"
                className="text-gray-400 hover:text-white transition-colors"
              >
                GitHub
              </Link>
              <button
                onClick={handleGitHubLogin}
                disabled={isLoading}
                className="bg-white text-black px-4 py-2 rounded font-medium hover:bg-gray-100 transition-colors disabled:opacity-50"
              >
                {isLoading ? 'Connecting...' : 'Get Started'}
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative h-screen overflow-hidden">
        {/* Grid Background with Moving Blocks */}
        <div className="absolute inset-0">
          {/* SVG Grid */}
          <svg className="w-full h-full opacity-40" viewBox="0 0 400 240">
            <defs>
              <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
                <path d="M 20 0 L 0 0 0 20" fill="none" stroke="rgb(168 85 247)" strokeWidth="0.7" opacity="0.4"/>
              </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#grid)" />
          </svg>
          
          {/* Moving Purple Blocks */}
          <div className="absolute inset-0 p-2">
            <div className="relative w-full h-full">
              <div className="absolute bg-purple-500 block-1"></div>
              <div className="absolute bg-purple-600 block-2"></div>
              <div className="absolute bg-purple-400 block-3"></div>
              <div className="absolute bg-purple-300 block-4"></div>
            </div>
          </div>
        </div>

        {/* Content Overlay */}
        <div className="relative z-10 h-full flex items-center">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="grid lg:grid-cols-2 gap-12 items-center">
              {/* Left Content */}
              <div className="text-left bg-black/20 backdrop-blur-sm rounded-2xl p-8 border border-purple-500/20">
                <h1 className="text-5xl md:text-6xl lg:text-7xl font-medium text-white mb-8 tracking-tight leading-tight">
                  Internet Infrastructure,{' '}
                  <span className="text-purple-400">
                    Now For LLMs
                  </span>
                </h1>
                
                <p className="text-xl md:text-2xl text-gray-400 mb-12 leading-relaxed max-w-2xl">
                  Today's web is human-first. Search engines, browsers, and content all assume people are on the other end. 
                  But LLMs need context, structure, and meaning — not unpredictable pages, buttons and hidden information.
                </p>
            
                <div className="flex flex-col sm:flex-row gap-4">
                  <button
                    onClick={handleGitHubLogin}
                    disabled={isLoading}
                    className="bg-white text-black px-8 py-4 rounded-lg font-semibold hover:bg-gray-100 transition-colors disabled:opacity-50 flex items-center space-x-2"
                  >
                    <Github className="h-5 w-5" />
                    <span>{isLoading ? 'Connecting...' : 'Get Started for Free'}</span>
                    <ArrowRight className="h-4 w-4" />
                  </button>
                  
                  <button 
                    onClick={handleViewDemo}
                    className="border border-gray-600 text-white px-8 py-4 rounded-lg font-semibold hover:border-gray-500 transition-colors flex items-center space-x-2"
                  >
                    <span>Contact Sales</span>
                    <ArrowRight className="h-4 w-4" />
                  </button>
                </div>
              </div>
              
              {/* Right side placeholder for balance */}
              <div className="hidden lg:block"></div>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="py-20 bg-gray-900">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-medium text-white mb-4">
              Build, deploy, and scale your apps with unparalleled ease
            </h2>
            <p className="text-xl text-gray-400 max-w-3xl mx-auto">
              From your first user to your billionth
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="w-12 h-12 bg-purple-500 rounded-lg flex items-center justify-center mx-auto mb-6">
                <Globe className="h-6 w-6 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-4">Universal Compatibility</h3>
              <p className="text-gray-400 leading-relaxed">
                Works with any GitHub repository. HTML, Markdown, code files — we parse it all into structured, searchable content.
              </p>
            </div>
            
            <div className="text-center">
              <div className="w-12 h-12 bg-purple-500 rounded-lg flex items-center justify-center mx-auto mb-6">
                <Cpu className="h-6 w-6 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-4">Vector Intelligence</h3>
              <p className="text-gray-400 leading-relaxed">
                Powered by Cohere's state-of-the-art embeddings. Semantic search that understands context, not just keywords.
              </p>
            </div>
            
            <div className="text-center">
              <div className="w-12 h-12 bg-purple-500 rounded-lg flex items-center justify-center mx-auto mb-6">
                <Network className="h-6 w-6 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-4">Production Ready</h3>
              <p className="text-gray-400 leading-relaxed">
                Deploy on Railway + Vercel in minutes. Built for scale with enterprise-grade reliability and performance.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* How it Works */}
      <section id="how-it-works" className="py-20 bg-black">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-medium text-white mb-4">
              Your fastest path to production
            </h2>
            <p className="text-xl text-gray-400">
              Deploy in minutes, search in milliseconds
            </p>
          </div>
          
          <div className="grid md:grid-cols-4 gap-8">
            <div className="text-center">
              <div className="w-12 h-12 bg-purple-500 rounded-lg flex items-center justify-center mx-auto mb-6">
                <Github className="h-6 w-6 text-white" />
              </div>
              <h3 className="text-lg font-semibold text-white mb-3">Connect GitHub</h3>
              <p className="text-sm text-gray-400 leading-relaxed">
                Authenticate with GitHub and select the repositories you want to index for search
              </p>
            </div>
            
            <div className="text-center">
              <div className="w-12 h-12 bg-purple-500 rounded-lg flex items-center justify-center mx-auto mb-6">
                <Search className="h-6 w-6 text-white" />
              </div>
              <h3 className="text-lg font-semibold text-white mb-3">Parse Content</h3>
              <p className="text-sm text-gray-400 leading-relaxed">
                Automatically extract and process HTML content from your repository files
              </p>
            </div>
            
            <div className="text-center">
              <div className="w-12 h-12 bg-purple-500 rounded-lg flex items-center justify-center mx-auto mb-6">
                <Zap className="h-6 w-6 text-white" />
              </div>
              <h3 className="text-lg font-semibold text-white mb-3">Generate Embeddings</h3>
              <p className="text-sm text-gray-400 leading-relaxed">
                Create high-quality vector embeddings using Cohere's advanced models
              </p>
            </div>
            
            <div className="text-center">
              <div className="w-12 h-12 bg-purple-500 rounded-lg flex items-center justify-center mx-auto mb-6">
                <Database className="h-6 w-6 text-white" />
              </div>
              <h3 className="text-lg font-semibold text-white mb-3">Search Ready</h3>
              <p className="text-sm text-gray-400 leading-relaxed">
                Your content is instantly searchable via our high-performance API
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 bg-gray-900 border-t border-gray-800">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <h2 className="text-4xl font-medium text-white mb-6">
            Ready to deploy your vector database?
          </h2>
          <p className="text-xl text-gray-400 mb-12 max-w-2xl mx-auto">
            Get started with 100,000 free embeddings per month. No credit card required.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <button
              onClick={handleGitHubLogin}
              disabled={isLoading}
              className="bg-white text-black px-8 py-4 rounded-lg font-semibold hover:bg-gray-100 transition-colors disabled:opacity-50 flex items-center space-x-2"
            >
              <Github className="h-5 w-5" />
              <span>{isLoading ? 'Connecting...' : 'Get Started for Free'}</span>
              <ArrowRight className="h-4 w-4" />
            </button>
            
            <Link 
              href="https://github.com/YuvDwi/Quilt" 
              target="_blank"
              className="border border-gray-600 text-white px-8 py-4 rounded-lg font-semibold hover:border-gray-500 transition-colors flex items-center space-x-2"
            >
              <span>View on GitHub</span>
              <ExternalLink className="h-4 w-4" />
            </Link>
          </div>
        </div>
      </section>
    </main>
  )
}