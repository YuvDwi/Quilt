'use client'

import { useState } from 'react'
import { Github, Database, Zap, Search, ArrowRight } from 'lucide-react'
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

  return (
    <main className="min-h-screen">
      {/* Header */}
      <nav className="bg-white/80 backdrop-blur-sm border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center space-x-2">
              <Database className="h-8 w-8 text-indigo-600" />
              <span className="text-2xl font-bold text-slate-900">Quilt</span>
            </div>
            <div className="hidden md:flex items-center space-x-8">
              <Link href="#features" className="text-slate-600 hover:text-slate-900">Features</Link>
              <Link href="#how-it-works" className="text-slate-600 hover:text-slate-900">How it Works</Link>
              <Link href="https://github.com/YuvDwi/Quilt" className="text-slate-600 hover:text-slate-900">GitHub</Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-20 pb-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 className="text-5xl md:text-6xl font-bold text-slate-900 mb-8">
            Vector Database for
            <span className="block text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-purple-600">
              the Web
            </span>
          </h1>
          <p className="text-xl text-slate-600 mb-12 max-w-3xl mx-auto">
            Deploy your repositories and automatically index HTML content with pre-computed vector embeddings. 
            Revolutionize RAG systems with instant semantic search instead of real-time embedding generation.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <button
              onClick={handleGitHubLogin}
              disabled={isLoading}
              className="flex items-center space-x-2 bg-slate-900 text-white px-8 py-4 rounded-lg hover:bg-slate-800 transition-colors disabled:opacity-50"
            >
              <Github className="h-5 w-5" />
              <span>{isLoading ? 'Connecting...' : 'Deploy with GitHub'}</span>
              <ArrowRight className="h-5 w-5" />
            </button>
            <Link 
              href="#demo" 
              className="flex items-center space-x-2 text-slate-600 hover:text-slate-900"
            >
              <span>View Demo</span>
              <ArrowRight className="h-4 w-4" />
            </Link>
          </div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-slate-900 mb-4">Why Quilt?</h2>
            <p className="text-lg text-slate-600">Traditional RAG systems are inefficient. Quilt changes the game.</p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center p-8 rounded-xl bg-slate-50 card-hover">
              <div className="bg-indigo-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-6">
                <Zap className="h-8 w-8 text-indigo-600" />
              </div>
              <h3 className="text-xl font-semibold mb-4">Instant Search</h3>
              <p className="text-slate-600">
                Pre-computed vectors eliminate real-time embedding generation. 
                Search happens in milliseconds, not seconds.
              </p>
            </div>
            
            <div className="text-center p-8 rounded-xl bg-slate-50 card-hover">
              <div className="bg-purple-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-6">
                <Database className="h-8 w-8 text-purple-600" />
              </div>
              <h3 className="text-xl font-semibold mb-4">Hybrid Search</h3>
              <p className="text-slate-600">
                TF-IDF vector similarity combined with keyword matching. 
                Best of semantic understanding and exact text matching.
              </p>
            </div>
            
            <div className="text-center p-8 rounded-xl bg-slate-50 card-hover">
              <div className="bg-cyan-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-6">
                <Search className="h-8 w-8 text-cyan-600" />
              </div>
              <h3 className="text-xl font-semibold mb-4">One-Click Deploy</h3>
              <p className="text-slate-600">
                Connect GitHub, select repositories, and deploy instantly. 
                No complex webhook setup or configuration needed.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* How it Works */}
      <section id="how-it-works" className="py-20 bg-slate-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-slate-900 mb-4">How Quilt Works</h2>
            <p className="text-lg text-slate-600">Simple, powerful, and automatic</p>
          </div>
          
          <div className="grid md:grid-cols-4 gap-8">
            <div className="text-center">
              <div className="bg-indigo-600 text-white w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-4 text-xl font-bold">1</div>
              <h3 className="font-semibold mb-2">Connect GitHub</h3>
              <p className="text-sm text-slate-600">Sign in with GitHub OAuth and select repositories to index</p>
            </div>
            <div className="text-center">
              <div className="bg-indigo-600 text-white w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-4 text-xl font-bold">2</div>
              <h3 className="font-semibold mb-2">Parse HTML</h3>
              <p className="text-sm text-slate-600">Extract content from data-llm attributes in your HTML files</p>
            </div>
            <div className="text-center">
              <div className="bg-indigo-600 text-white w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-4 text-xl font-bold">3</div>
              <h3 className="font-semibold mb-2">Create Vectors</h3>
              <p className="text-sm text-slate-600">Generate TF-IDF vectors for semantic similarity search</p>
            </div>
            <div className="text-center">
              <div className="bg-indigo-600 text-white w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-4 text-xl font-bold">4</div>
              <h3 className="font-semibold mb-2">Instant Search</h3>
              <p className="text-sm text-slate-600">Your content is immediately searchable via API</p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 bg-slate-900 text-white">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold mb-6">Ready to revolutionize your search?</h2>
          <p className="text-xl text-slate-300 mb-8">
            Join the movement to make RAG systems faster and more efficient
          </p>
          <button
            onClick={handleGitHubLogin}
            disabled={isLoading}
            className="bg-indigo-600 hover:bg-indigo-700 text-white px-8 py-4 rounded-lg text-lg font-semibold transition-colors disabled:opacity-50"
          >
            Get Started with GitHub
          </button>
        </div>
      </section>
    </main>
  )
}
