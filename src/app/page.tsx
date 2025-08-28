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
    <main className="min-h-screen bg-[#0a0a0f] text-white overflow-hidden">
      {/* Header */}
      <nav className="border-b border-purple-900/20 bg-[#0a0a0f]/90 backdrop-blur-md fixed w-full z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-3">
              <div className="relative">
                <div className="w-8 h-8 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg flex items-center justify-center">
                  <Database className="h-5 w-5 text-white" />
                </div>
                <div className="absolute -inset-1 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg blur opacity-20 animate-pulse"></div>
              </div>
              <span className="text-xl font-bold text-white tracking-tight">Quilt</span>
            </div>
            <div className="hidden md:flex items-center space-x-8">
              <button 
                onClick={handleGetStarted}
                className="text-gray-400 hover:text-white transition-all duration-300 font-medium"
              >
                Features
              </button>
              <button 
                onClick={() => document.getElementById('how-it-works')?.scrollIntoView({ behavior: 'smooth' })}
                className="text-gray-400 hover:text-white transition-all duration-300 font-medium"
              >
                How it Works
              </button>
              <Link 
                href="https://github.com/YuvDwi/Quilt" 
                target="_blank"
                className="text-gray-400 hover:text-white transition-all duration-300 flex items-center space-x-1 font-medium"
              >
                <span>GitHub</span>
                <ExternalLink className="h-3 w-3" />
              </Link>
              <button
                onClick={handleGitHubLogin}
                disabled={isLoading}
                className="bg-gradient-to-r from-purple-600 to-pink-600 text-white px-6 py-2.5 rounded-lg text-sm font-semibold hover:from-purple-700 hover:to-pink-700 transition-all duration-300 disabled:opacity-50 shadow-lg shadow-purple-500/25"
              >
                {isLoading ? 'Connecting...' : 'Deploy Now'}
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative pt-32 pb-20 overflow-hidden">
        {/* Background effects */}
        <div className="absolute inset-0 bg-gradient-to-br from-purple-900/10 via-transparent to-pink-900/10"></div>
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-gradient-to-r from-purple-500/10 to-pink-500/10 rounded-full blur-3xl animate-pulse"></div>
        
        <div className="relative max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className={`mb-12 transition-all duration-1000 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}`}>
            <div className="inline-flex items-center px-4 py-2 rounded-full text-sm bg-purple-900/20 border border-purple-500/30 text-purple-200 mb-8 backdrop-blur-sm">
              <div className="w-2 h-2 bg-purple-400 rounded-full mr-2 animate-pulse"></div>
              100K free embeddings monthly • No credit card required
            </div>
          </div>
          
          <div className={`transition-all duration-1000 delay-200 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}`}>
            <h1 className="text-5xl md:text-7xl lg:text-8xl font-black text-white mb-8 tracking-tight leading-none">
              Internet Infrastructure,{' '}
              <br className="hidden md:block" />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 via-pink-400 to-purple-600 animate-gradient">
                Now For LLMs
              </span>
            </h1>
          </div>
          
          <div className={`transition-all duration-1000 delay-400 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}`}>
            <p className="text-xl md:text-2xl text-gray-300 mb-16 max-w-4xl mx-auto leading-relaxed font-light">
              Today's web is human-first. Search engines, browsers, and content all assume people are on the other end. 
              But LLMs need context, structure, and meaning — not buttons and pictures.
            </p>
          </div>
          
          <div className={`flex flex-col sm:flex-row gap-6 justify-center items-center mb-16 transition-all duration-1000 delay-600 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}`}>
            <button
              onClick={handleGitHubLogin}
              disabled={isLoading}
              className="group relative overflow-hidden bg-gradient-to-r from-purple-600 to-pink-600 text-white px-8 py-4 rounded-xl font-semibold hover:from-purple-700 hover:to-pink-700 transition-all duration-300 disabled:opacity-50 shadow-2xl shadow-purple-500/25 hover:shadow-purple-500/40 hover:scale-105"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-purple-600 to-pink-600 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
              <div className="relative flex items-center space-x-3">
                <Github className="h-5 w-5" />
                <span className="text-lg">{isLoading ? 'Connecting...' : 'Deploy with GitHub'}</span>
                <ArrowRight className="h-5 w-5 group-hover:translate-x-1 transition-transform duration-300" />
              </div>
            </button>
            
            <button 
              onClick={handleViewDemo}
              className="group flex items-center space-x-3 text-gray-300 hover:text-white transition-all duration-300 px-6 py-4 rounded-xl border border-gray-700 hover:border-purple-500/50 backdrop-blur-sm hover:shadow-lg hover:shadow-purple-500/10"
            >
              <Play className="h-5 w-5 group-hover:scale-110 transition-transform duration-300" />
              <span className="text-lg font-medium">View Live Demo</span>
            </button>
          </div>
          
          {/* Live Demo Preview */}
          <div className={`transition-all duration-1000 delay-800 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}`}>
            <div className="bg-[#0d1117] border border-purple-500/20 rounded-2xl p-8 max-w-4xl mx-auto backdrop-blur-sm shadow-2xl shadow-purple-500/10">
              <div className="flex items-center justify-between mb-6">
                <div className="flex space-x-3">
                  <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                  <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                  <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                </div>
                <div className="text-purple-300 text-sm font-mono bg-purple-900/20 px-3 py-1 rounded-lg">quilt-api.railway.app</div>
              </div>
              <div className="text-left space-y-4">
                <div className="text-green-400 text-sm font-mono bg-gray-900/50 p-4 rounded-lg border border-gray-700">
                  $ curl -X GET "https://your-backend.railway.app/search?query=authentication"
                </div>
                <div className="text-gray-300 text-sm font-mono bg-[#161b22] p-4 rounded-lg border border-gray-700">
                  <div className="text-blue-400">{"{"}</div>
                  <div className="pl-4 text-purple-300">"search_type": <span className="text-green-400">"hybrid_cohere"</span>,</div>
                  <div className="pl-4 text-purple-300">"total_results": <span className="text-yellow-400">5</span>,</div>
                  <div className="pl-4 text-purple-300">"results": <span className="text-gray-400">[...]</span></div>
                  <div className="text-blue-400">{"}"}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="py-32 bg-gradient-to-b from-[#0a0a0f] to-[#0f0f1a] relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-purple-900/5 via-transparent to-pink-900/5"></div>
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-20">
            <h2 className="text-4xl md:text-5xl lg:text-6xl font-black text-white mb-6 tracking-tight">
              Built for the{' '}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-400">
                AI Era
              </span>
            </h2>
            <p className="text-xl md:text-2xl text-gray-300 max-w-3xl mx-auto font-light leading-relaxed">
              Turn any codebase into an LLM-ready knowledge base. No prompt engineering required.
            </p>
          </div>
          
          <div className="grid lg:grid-cols-3 gap-8">
            <div className="group relative bg-gradient-to-br from-[#1a1a2e]/80 to-[#16213e]/80 border border-purple-500/20 rounded-3xl p-8 hover:border-purple-500/40 transition-all duration-500 hover:scale-105 backdrop-blur-sm">
              <div className="absolute inset-0 bg-gradient-to-br from-purple-500/5 to-pink-500/5 rounded-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
              <div className="relative">
                <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-purple-600 rounded-2xl flex items-center justify-center mb-8 shadow-lg shadow-purple-500/25">
                  <Globe className="h-8 w-8 text-white" />
                </div>
                <h3 className="text-2xl font-bold text-white mb-4">Universal Compatibility</h3>
                <p className="text-gray-300 leading-relaxed text-lg">
                  Works with any GitHub repository. HTML, Markdown, code files — we parse it all into structured, searchable content.
                </p>
              </div>
            </div>
            
            <div className="group relative bg-gradient-to-br from-[#1a1a2e]/80 to-[#16213e]/80 border border-purple-500/20 rounded-3xl p-8 hover:border-purple-500/40 transition-all duration-500 hover:scale-105 backdrop-blur-sm">
              <div className="absolute inset-0 bg-gradient-to-br from-purple-500/5 to-pink-500/5 rounded-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
              <div className="relative">
                <div className="w-16 h-16 bg-gradient-to-br from-pink-500 to-pink-600 rounded-2xl flex items-center justify-center mb-8 shadow-lg shadow-pink-500/25">
                  <Cpu className="h-8 w-8 text-white" />
                </div>
                <h3 className="text-2xl font-bold text-white mb-4">Vector Intelligence</h3>
                <p className="text-gray-300 leading-relaxed text-lg">
                  Powered by Cohere's state-of-the-art embeddings. Semantic search that understands context, not just keywords.
                </p>
              </div>
            </div>
            
            <div className="group relative bg-gradient-to-br from-[#1a1a2e]/80 to-[#16213e]/80 border border-purple-500/20 rounded-3xl p-8 hover:border-purple-500/40 transition-all duration-500 hover:scale-105 backdrop-blur-sm">
              <div className="absolute inset-0 bg-gradient-to-br from-purple-500/5 to-pink-500/5 rounded-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
              <div className="relative">
                <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl flex items-center justify-center mb-8 shadow-lg shadow-blue-500/25">
                  <Network className="h-8 w-8 text-white" />
                </div>
                <h3 className="text-2xl font-bold text-white mb-4">Production Ready</h3>
                <p className="text-gray-300 leading-relaxed text-lg">
                  Deploy on Railway + Vercel in minutes. Built for scale with enterprise-grade reliability and performance.
                </p>
              </div>
            </div>
          </div>
          
          {/* Stats */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-8 mt-20 pt-12 border-t border-purple-500/20">
            <div className="text-center group">
              <div className="text-4xl md:text-5xl font-black text-transparent bg-clip-text bg-gradient-to-br from-purple-400 to-pink-400 mb-3 group-hover:scale-110 transition-transform duration-300">100K</div>
              <div className="text-gray-300 text-lg font-medium">Free embeddings/month</div>
            </div>
            <div className="text-center group">
              <div className="text-4xl md:text-5xl font-black text-transparent bg-clip-text bg-gradient-to-br from-blue-400 to-purple-400 mb-3 group-hover:scale-110 transition-transform duration-300">&lt;100ms</div>
              <div className="text-gray-300 text-lg font-medium">Search response time</div>
            </div>
            <div className="text-center group">
              <div className="text-4xl md:text-5xl font-black text-transparent bg-clip-text bg-gradient-to-br from-pink-400 to-purple-400 mb-3 group-hover:scale-110 transition-transform duration-300">1024</div>
              <div className="text-gray-300 text-lg font-medium">Vector dimensions</div>
            </div>
            <div className="text-center group">
              <div className="text-4xl md:text-5xl font-black text-transparent bg-clip-text bg-gradient-to-br from-green-400 to-blue-400 mb-3 group-hover:scale-110 transition-transform duration-300">0</div>
              <div className="text-gray-300 text-lg font-medium">Infrastructure setup</div>
            </div>
          </div>
        </div>
      </section>

      {/* How it Works */}
      <section id="how-it-works" className="py-32 bg-gradient-to-b from-[#0f0f1a] to-[#0a0a0f] relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-pink-900/5 via-transparent to-purple-900/5"></div>
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-20">
            <h2 className="text-4xl md:text-5xl lg:text-6xl font-black text-white mb-6 tracking-tight">
              How it{' '}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-pink-400 to-purple-400">
                Works
              </span>
            </h2>
            <p className="text-xl md:text-2xl text-gray-300 font-light">
              Four steps to LLM-ready infrastructure
            </p>
          </div>
          
          <div className="grid lg:grid-cols-4 gap-8 relative">
            {/* Connection lines */}
            <div className="hidden lg:block absolute top-20 left-0 w-full h-0.5 bg-gradient-to-r from-transparent via-purple-500/30 to-transparent"></div>
            
            <div className="text-center group relative">
              <div className="relative mb-8">
                <div className="w-20 h-20 bg-gradient-to-br from-purple-500 to-purple-600 rounded-3xl flex items-center justify-center mx-auto group-hover:scale-110 transition-all duration-300 shadow-lg shadow-purple-500/25">
                  <Github className="h-10 w-10 text-white" />
                </div>
                <div className="absolute -top-2 -left-2 w-6 h-6 bg-purple-400 rounded-full flex items-center justify-center text-sm font-bold text-white">1</div>
              </div>
              <h3 className="text-xl font-bold text-white mb-4">Connect Repository</h3>
              <p className="text-gray-300 leading-relaxed text-lg">
                Authenticate with GitHub and select repositories to transform into searchable knowledge bases
              </p>
            </div>
            
            <div className="text-center group relative">
              <div className="relative mb-8">
                <div className="w-20 h-20 bg-gradient-to-br from-pink-500 to-pink-600 rounded-3xl flex items-center justify-center mx-auto group-hover:scale-110 transition-all duration-300 shadow-lg shadow-pink-500/25">
                  <Search className="h-10 w-10 text-white" />
                </div>
                <div className="absolute -top-2 -left-2 w-6 h-6 bg-pink-400 rounded-full flex items-center justify-center text-sm font-bold text-white">2</div>
              </div>
              <h3 className="text-xl font-bold text-white mb-4">Parse & Structure</h3>
              <p className="text-gray-300 leading-relaxed text-lg">
                Intelligent extraction of content from HTML, Markdown, and code files into structured format
              </p>
            </div>
            
            <div className="text-center group relative">
              <div className="relative mb-8">
                <div className="w-20 h-20 bg-gradient-to-br from-blue-500 to-blue-600 rounded-3xl flex items-center justify-center mx-auto group-hover:scale-110 transition-all duration-300 shadow-lg shadow-blue-500/25">
                  <Cpu className="h-10 w-10 text-white" />
                </div>
                <div className="absolute -top-2 -left-2 w-6 h-6 bg-blue-400 rounded-full flex items-center justify-center text-sm font-bold text-white">3</div>
              </div>
              <h3 className="text-xl font-bold text-white mb-4">Generate Vectors</h3>
              <p className="text-gray-300 leading-relaxed text-lg">
                Create high-dimensional embeddings using Cohere's enterprise-grade AI models
              </p>
            </div>
            
            <div className="text-center group relative">
              <div className="relative mb-8">
                <div className="w-20 h-20 bg-gradient-to-br from-green-500 to-green-600 rounded-3xl flex items-center justify-center mx-auto group-hover:scale-110 transition-all duration-300 shadow-lg shadow-green-500/25">
                  <Database className="h-10 w-10 text-white" />
                </div>
                <div className="absolute -top-2 -left-2 w-6 h-6 bg-green-400 rounded-full flex items-center justify-center text-sm font-bold text-white">4</div>
              </div>
              <h3 className="text-xl font-bold text-white mb-4">Deploy & Scale</h3>
              <p className="text-gray-300 leading-relaxed text-lg">
                Production-ready API deployed to Railway with global CDN and automatic scaling
              </p>
            </div>
          </div>
          
          {/* Code Example */}
          <div className="mt-20 bg-gradient-to-br from-[#0d1117] to-[#161b22] border border-purple-500/20 rounded-3xl overflow-hidden backdrop-blur-sm shadow-2xl shadow-purple-500/10">
            <div className="px-8 py-6 border-b border-purple-500/20 flex items-center justify-between">
              <div className="text-purple-300 text-lg font-semibold">API Example</div>
              <div className="flex space-x-3">
                <div className="w-4 h-4 bg-red-500 rounded-full"></div>
                <div className="w-4 h-4 bg-yellow-500 rounded-full"></div>
                <div className="w-4 h-4 bg-green-500 rounded-full"></div>
              </div>
            </div>
            <div className="p-8">
              <div className="text-green-400 text-lg mb-6 font-mono">
                # Deploy your repository and search instantly
              </div>
              <div className="space-y-6">
                <div className="bg-[#161b22] p-6 rounded-xl border border-gray-700">
                  <div className="text-blue-400 text-lg font-mono font-bold mb-2">POST</div>
                  <div className="text-purple-300 text-lg font-mono">https://your-quilt-api.railway.app/deploy</div>
                </div>
                
                <div className="bg-[#161b22] p-6 rounded-xl border border-gray-700">
                  <div className="text-blue-400 text-lg font-mono font-bold mb-2">GET</div>
                  <div className="text-purple-300 text-lg font-mono">https://your-quilt-api.railway.app/search?query=authentication</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-32 bg-gradient-to-b from-[#0a0a0f] to-[#0f0f1a] border-t border-purple-500/20 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-purple-900/10 via-transparent to-pink-900/10"></div>
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-gradient-to-r from-purple-500/5 to-pink-500/5 rounded-full blur-3xl"></div>
        
        <div className="relative max-w-5xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <h2 className="text-4xl md:text-5xl lg:text-6xl font-black text-white mb-8 tracking-tight">
            Ready to power your{' '}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-400">
              AI applications?
            </span>
          </h2>
          <p className="text-xl md:text-2xl text-gray-300 mb-16 max-w-3xl mx-auto font-light leading-relaxed">
            Join the infrastructure revolution. Deploy your LLM-ready knowledge base in minutes, not months.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-6 justify-center items-center mb-16">
            <button
              onClick={handleGitHubLogin}
              disabled={isLoading}
              className="group relative overflow-hidden bg-gradient-to-r from-purple-600 to-pink-600 text-white px-10 py-5 rounded-xl font-bold text-lg hover:from-purple-700 hover:to-pink-700 transition-all duration-300 disabled:opacity-50 shadow-2xl shadow-purple-500/25 hover:shadow-purple-500/40 hover:scale-105"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-purple-600 to-pink-600 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
              <div className="relative flex items-center space-x-3">
                <Github className="h-6 w-6" />
                <span>{isLoading ? 'Connecting...' : 'Deploy with GitHub'}</span>
                <ArrowRight className="h-6 w-6 group-hover:translate-x-1 transition-transform duration-300" />
              </div>
            </button>
            
            <Link 
              href="https://github.com/YuvDwi/Quilt" 
              target="_blank"
              className="group flex items-center space-x-3 text-gray-300 hover:text-white transition-all duration-300 px-8 py-5 rounded-xl border border-purple-500/30 hover:border-purple-500/60 backdrop-blur-sm hover:shadow-lg hover:shadow-purple-500/10 text-lg font-semibold"
            >
              <span>View on GitHub</span>
              <ExternalLink className="h-5 w-5 group-hover:scale-110 transition-transform duration-300" />
            </Link>
          </div>
          
          {/* Footer */}
          <div className="pt-16 border-t border-purple-500/20">
            <div className="flex flex-wrap items-center justify-center gap-8 text-gray-400">
              <div className="flex items-center space-x-3 group hover:text-white transition-colors duration-300">
                <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-lg font-medium">Railway Backend</span>
              </div>
              <div className="flex items-center space-x-3 group hover:text-white transition-colors duration-300">
                <div className="w-3 h-3 bg-blue-500 rounded-full animate-pulse"></div>
                <span className="text-lg font-medium">Vercel Frontend</span>
              </div>
              <div className="flex items-center space-x-3 group hover:text-white transition-colors duration-300">
                <div className="w-3 h-3 bg-purple-500 rounded-full animate-pulse"></div>
                <span className="text-lg font-medium">Cohere Embeddings</span>
              </div>
            </div>
          </div>
        </div>
      </section>
    </main>
  )
}
