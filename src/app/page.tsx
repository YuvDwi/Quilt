'use client'

import { useState } from 'react'
import { Github, Database, Zap, Search, ArrowRight, ExternalLink, Play, ChevronRight } from 'lucide-react'
import Link from 'next/link'

export default function Home() {
  const [isLoading, setIsLoading] = useState(false)

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
      <nav className="border-b border-gray-800 bg-black/80 backdrop-blur-sm fixed w-full z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-white rounded-md flex items-center justify-center">
                <Database className="h-5 w-5 text-black" />
              </div>
              <span className="text-xl font-semibold text-white">Quilt</span>
            </div>
            <div className="hidden md:flex items-center space-x-8">
              <button 
                onClick={handleGetStarted}
                className="text-gray-400 hover:text-white transition-colors"
              >
                Features
              </button>
              <button 
                onClick={() => document.getElementById('how-it-works')?.scrollIntoView({ behavior: 'smooth' })}
                className="text-gray-400 hover:text-white transition-colors"
              >
                How it Works
              </button>
              <Link 
                href="https://github.com/YuvDwi/Quilt" 
                target="_blank"
                className="text-gray-400 hover:text-white transition-colors flex items-center space-x-1"
              >
                <span>GitHub</span>
                <ExternalLink className="h-3 w-3" />
              </Link>
              <button
                onClick={handleGitHubLogin}
                disabled={isLoading}
                className="bg-white text-black px-4 py-2 rounded-md text-sm font-medium hover:bg-gray-200 transition-colors disabled:opacity-50"
              >
                {isLoading ? 'Connecting...' : 'Deploy Now'}
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-20">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="mb-8">
            <div className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-gray-900 border border-gray-800 text-gray-300 mb-8">
              <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
              100K free embeddings with Cohere
            </div>
          </div>
          
          <h1 className="text-5xl md:text-7xl font-bold text-white mb-6 tracking-tight">
            Vector Database for{' '}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-white to-gray-400">
              the Web
            </span>
          </h1>
          
          <p className="text-xl text-gray-400 mb-12 max-w-2xl mx-auto leading-relaxed">
            Turn your GitHub repositories into a searchable database. 
            Deploy once, search instantly.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-12">
            <button
              onClick={handleGitHubLogin}
              disabled={isLoading}
              className="flex items-center space-x-2 bg-white text-black px-6 py-3 rounded-md font-medium hover:bg-gray-200 transition-colors disabled:opacity-50 group"
            >
              <Github className="h-4 w-4" />
              <span>{isLoading ? 'Connecting...' : 'Deploy with GitHub'}</span>
              <ArrowRight className="h-4 w-4 group-hover:translate-x-1 transition-transform" />
            </button>
            
            <button 
              onClick={handleViewDemo}
              className="flex items-center space-x-2 text-gray-400 hover:text-white transition-colors"
            >
              <Play className="h-4 w-4" />
              <span>View Live Demo</span>
            </button>
          </div>
          
          {/* Live Demo Preview */}
          <div className="bg-gray-900 border border-gray-800 rounded-lg p-6 max-w-2xl mx-auto">
            <div className="flex items-center justify-between mb-4">
              <div className="flex space-x-2">
                <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                <div className="w-3 h-3 bg-green-500 rounded-full"></div>
              </div>
              <div className="text-gray-500 text-sm">quilt-api.railway.app</div>
            </div>
            <div className="text-left">
              <div className="text-green-400 text-sm mb-2">$ curl -X GET "https://your-backend.railway.app/search?query=authentication"</div>
              <div className="text-gray-400 text-sm">
                <div>{"{"}</div>
                <div className="pl-4">"search_type": "hybrid_cohere",</div>
                <div className="pl-4">"total_results": 5,</div>
                <div className="pl-4">"results": [...]</div>
                <div>{"}"}</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="py-20 bg-gray-950">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              Why choose Quilt?
            </h2>
            <p className="text-lg text-gray-400 max-w-2xl mx-auto">
              Stop building complex search systems. Just connect GitHub and start searching.
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8">
            <div className="bg-gray-900 border border-gray-800 rounded-lg p-8 hover:border-gray-700 transition-colors">
              <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg flex items-center justify-center mb-6">
                <Zap className="h-6 w-6 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-4">Lightning Fast</h3>
              <p className="text-gray-400 leading-relaxed">
                Search results appear instantly. No complex setup or waiting required.
              </p>
            </div>
            
            <div className="bg-gray-900 border border-gray-800 rounded-lg p-8 hover:border-gray-700 transition-colors">
              <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-purple-600 rounded-lg flex items-center justify-center mb-6">
                <Database className="h-6 w-6 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-4">Hybrid Intelligence</h3>
              <p className="text-gray-400 leading-relaxed">
                Smart search that understands meaning, not just keywords. 
                Find what you're looking for, even with different words.
              </p>
            </div>
            
            <div className="bg-gray-900 border border-gray-800 rounded-lg p-8 hover:border-gray-700 transition-colors">
              <div className="w-12 h-12 bg-gradient-to-br from-green-500 to-green-600 rounded-lg flex items-center justify-center mb-6">
                <Search className="h-6 w-6 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-4">Zero Config</h3>
              <p className="text-gray-400 leading-relaxed">
                Connect GitHub and deploy in minutes. 
                No servers to manage or code to write.
              </p>
            </div>
          </div>
          
          {/* Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mt-16 pt-16 border-t border-gray-800">
            <div className="text-center">
              <div className="text-3xl font-bold text-white mb-2">100K</div>
              <div className="text-gray-400 text-sm">Free embeddings/month</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-white mb-2">&lt;100ms</div>
              <div className="text-gray-400 text-sm">Search response time</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-white mb-2">1024</div>
              <div className="text-gray-400 text-sm">Vector dimensions</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-white mb-2">0</div>
              <div className="text-gray-400 text-sm">Infrastructure setup</div>
            </div>
          </div>
        </div>
      </section>

      {/* How it Works */}
      <section id="how-it-works" className="py-20 bg-black">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              How it works
            </h2>
            <p className="text-lg text-gray-400">
              Deploy in minutes, search in milliseconds
            </p>
          </div>
          
          <div className="grid md:grid-cols-4 gap-8">
            <div className="text-center group">
              <div className="relative">
                <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-transform">
                  <Github className="h-8 w-8 text-white" />
                </div>
                {/* Connection line */}
                <div className="hidden md:block absolute top-8 left-16 w-full h-0.5 bg-gray-800"></div>
              </div>
              <h3 className="text-lg font-semibold text-white mb-3">Connect GitHub</h3>
              <p className="text-sm text-gray-400 leading-relaxed">
                Authenticate with GitHub and select the repositories you want to index for search
              </p>
            </div>
            
            <div className="text-center group">
              <div className="relative">
                <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-transform">
                  <Search className="h-8 w-8 text-white" />
                </div>
                <div className="hidden md:block absolute top-8 left-16 w-full h-0.5 bg-gray-800"></div>
              </div>
              <h3 className="text-lg font-semibold text-white mb-3">Parse Content</h3>
              <p className="text-sm text-gray-400 leading-relaxed">
                Automatically extract and process HTML content from your repository files
              </p>
            </div>
            
            <div className="text-center group">
              <div className="relative">
                <div className="w-16 h-16 bg-gradient-to-br from-green-500 to-green-600 rounded-xl flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-transform">
                  <Zap className="h-8 w-8 text-white" />
                </div>
                <div className="hidden md:block absolute top-8 left-16 w-full h-0.5 bg-gray-800"></div>
              </div>
              <h3 className="text-lg font-semibold text-white mb-3">Generate Embeddings</h3>
              <p className="text-sm text-gray-400 leading-relaxed">
                Create high-quality vector embeddings using Cohere's advanced models
              </p>
            </div>
            
            <div className="text-center group">
              <div className="w-16 h-16 bg-gradient-to-br from-orange-500 to-orange-600 rounded-xl flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-transform">
                <Database className="h-8 w-8 text-white" />
              </div>
              <h3 className="text-lg font-semibold text-white mb-3">Search Ready</h3>
              <p className="text-sm text-gray-400 leading-relaxed">
                Your content is instantly searchable via our high-performance API
              </p>
            </div>
          </div>
          
          {/* Code Example */}
          <div className="mt-16 bg-gray-900 border border-gray-800 rounded-lg overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-800 flex items-center justify-between">
              <div className="text-gray-400 text-sm">API Example</div>
              <div className="flex space-x-2">
                <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                <div className="w-3 h-3 bg-green-500 rounded-full"></div>
              </div>
            </div>
            <div className="p-6">
              <div className="text-green-400 text-sm mb-4">
                # Deploy your repository and search instantly
              </div>
              <div className="text-gray-300 text-sm font-mono">
                <div className="text-blue-400">POST</div>
                <div className="text-gray-500 mb-4">https://your-quilt-api.railway.app/deploy</div>
                
                <div className="text-blue-400">GET</div>
                <div className="text-gray-500">https://your-quilt-api.railway.app/search?query=authentication</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 bg-gray-950 border-t border-gray-800">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">
            Ready to deploy your vector database?
          </h2>
          <p className="text-xl text-gray-400 mb-12 max-w-2xl mx-auto">
            Get started with 100,000 free embeddings per month. No credit card required.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-12">
            <button
              onClick={handleGitHubLogin}
              disabled={isLoading}
              className="flex items-center space-x-3 bg-white text-black px-8 py-4 rounded-lg font-semibold hover:bg-gray-100 transition-colors disabled:opacity-50 group"
            >
              <Github className="h-5 w-5" />
              <span>{isLoading ? 'Connecting...' : 'Deploy with GitHub'}</span>
              <ArrowRight className="h-5 w-5 group-hover:translate-x-1 transition-transform" />
            </button>
            
            <Link 
              href="https://github.com/YuvDwi/Quilt" 
              target="_blank"
              className="flex items-center space-x-2 text-gray-400 hover:text-white transition-colors border border-gray-800 px-6 py-4 rounded-lg hover:border-gray-700"
            >
              <span>View on GitHub</span>
              <ExternalLink className="h-4 w-4" />
            </Link>
          </div>
          
          {/* Footer */}
          <div className="pt-12 border-t border-gray-800">
            <div className="flex items-center justify-center space-x-6 text-gray-500 text-sm">
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span>Railway Backend</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                <span>Vercel Frontend</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                <span>Cohere Embeddings</span>
              </div>
            </div>
          </div>
        </div>
      </section>
    </main>
  )
}
