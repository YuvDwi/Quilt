'use client'

import { useState, useEffect } from 'react'
import { Github, Database, Zap, Search, ArrowRight, ExternalLink, Play, ChevronRight, Globe, Cpu, Network } from 'lucide-react'
import Link from 'next/link'

interface Block {
  x: number
  y: number
  vx: number
  vy: number
  id: string
  color: string
}

export default function Home() {
  const [isLoading, setIsLoading] = useState(false)
  const [isVisible, setIsVisible] = useState(false)
  const [blocks, setBlocks] = useState<Block[]>([
    { x: 2, y: 3, vx: 1, vy: 0, id: 'block1', color: 'bg-purple-500' },
    { x: 15, y: 1, vx: 0, vy: 1, id: 'block2', color: 'bg-purple-400' },
    { x: 8, y: 6, vx: -1, vy: 0, id: 'block3', color: 'bg-purple-600' }
  ])

  const GRID_COLS = 20
  const GRID_ROWS = 12

  useEffect(() => {
    setIsVisible(true)
    
    const moveBlocks = () => {
      setBlocks(prevBlocks => {
        return prevBlocks.map(block => {
          let newX = block.x + block.vx
          let newY = block.y + block.vy
          let newVx = block.vx
          let newVy = block.vy

          // Wall collision - repel from edges
          if (newX <= 0 || newX >= GRID_COLS - 1) {
            newVx = -newVx
            newX = Math.max(1, Math.min(GRID_COLS - 2, newX))
          }
          if (newY <= 0 || newY >= GRID_ROWS - 1) {
            newVy = -newVy
            newY = Math.max(1, Math.min(GRID_ROWS - 2, newY))
          }

          // Check collision with other blocks
          const otherBlocks = prevBlocks.filter(b => b.id !== block.id)
          for (const other of otherBlocks) {
            const dx = newX - other.x
            const dy = newY - other.y
            const distance = Math.sqrt(dx * dx + dy * dy)
            
            if (distance < 2) { // Collision detected
              // Repel in opposite directions
              if (Math.abs(dx) > Math.abs(dy)) {
                newVx = dx > 0 ? 1 : -1
                newVy = 0
              } else {
                newVx = 0
                newVy = dy > 0 ? 1 : -1
              }
              // Push apart
              newX = block.x + newVx
              newY = block.y + newVy
            }
          }

          return {
            ...block,
            x: newX,
            y: newY,
            vx: newVx,
            vy: newVy
          }
        })
      })
    }

    const interval = setInterval(moveBlocks, 300) // Move every 300ms
    return () => clearInterval(interval)
  }, [GRID_COLS, GRID_ROWS])

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

      {/* Hero Section - Full Screen */}
      <section className="relative h-screen overflow-hidden">
        {/* Square Grid Background with Glow */}
        <div className="absolute inset-0">
          <div className="grid grid-cols-20 grid-rows-12 h-full w-full gap-1 p-2">
            {Array.from({ length: GRID_COLS * GRID_ROWS }).map((_, i) => (
              <div 
                key={i} 
                className="border border-purple-500/20 bg-purple-900/5 rounded-sm glow-square"
                style={{ aspectRatio: '1' }}
              ></div>
            ))}
          </div>
        </div>
        
        {/* Physics-based Blocks */}
        <div className="absolute inset-0 p-2">
          <div className="grid grid-cols-20 grid-rows-12 h-full w-full gap-1">
            {blocks.map(block => (
              <div
                key={block.id}
                className={`${block.color} rounded-sm shadow-lg transition-all duration-300 ease-linear glow-block`}
                style={{
                  gridColumn: block.x + 1,
                  gridRow: block.y + 1,
                  aspectRatio: '1'
                }}
              ></div>
            ))}
          </div>
        </div>
        
        {/* Content Overlay */}
        <div className="relative z-10 h-full flex items-center justify-center">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 w-full">
            <div className="grid lg:grid-cols-2 gap-12 items-center h-full">
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
                  But LLMs need context, structure, and meaning — not buttons and pictures.
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
              
              {/* Right side - Empty for grid visibility */}
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