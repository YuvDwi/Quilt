'use client'

import { useState, useEffect, Suspense } from 'react'
import { useSearchParams } from 'next/navigation'
import { Github, Database, Clock, CheckCircle, AlertCircle, RefreshCw, Search, Plus, Grid, List, Settings, Bell, BookOpen, HelpCircle, ChevronDown, ExternalLink, GitBranch } from 'lucide-react'
import axios from 'axios'

interface Repository {
  id: number
  name: string
  full_name: string
  html_url: string
  description: string
  updated_at: string
  private: boolean
}

interface Deployment {
  repo_name: string
  repo_url: string
  deployed_at: string
  sections_indexed: number
}

function DashboardContent() {
  const searchParams = useSearchParams()
  const [repositories, setRepositories] = useState<Repository[]>([])
  const [deployments, setDeployments] = useState<Deployment[]>([])
  const [loading, setLoading] = useState(true)
  const [deploying, setDeploying] = useState<string | null>(null)
  const [user, setUser] = useState<string>('')
  const [token, setToken] = useState<string>('')
  const [activeTab, setActiveTab] = useState<'overview' | 'deployments' | 'repositories'>('overview')

  useEffect(() => {
    const userParam = searchParams.get('user')
    const tokenParam = searchParams.get('token')
    
    if (userParam && tokenParam) {
      setUser(userParam)
      setToken(tokenParam)
      fetchRepositories(tokenParam)
      fetchDeployments(userParam)
    }
  }, [searchParams])

  const fetchRepositories = async (accessToken: string) => {
    try {
      const response = await axios.get('https://api.github.com/user/repos', {
        headers: { Authorization: `token ${accessToken}` },
        params: { sort: 'updated', per_page: 100 }
      })
      setRepositories(response.data.filter((repo: Repository) => !repo.private))
    } catch (error) {
      console.error('Failed to fetch repositories:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchDeployments = async (username: string) => {
    try {
      const response = await axios.get(`${process.env.NEXT_PUBLIC_QUILT_API_URL}/deployments/${username}`)
      setDeployments(response.data.deployments || [])
    } catch (error) {
      console.error('Failed to fetch deployments:', error)
    }
  }

  const deployRepository = async (repoUrl: string, repoName: string) => {
    setDeploying(repoName)
    try {
      const response = await axios.post(`${process.env.NEXT_PUBLIC_QUILT_API_URL}/deploy`, {
        repo_url: repoUrl,
        token: token,
        user: user
      })
      
      if (response.data.status === 'success') {
        await fetchDeployments(user)
        alert(`Successfully deployed ${repoName}! Indexed ${response.data.sections_indexed} sections.`)
      } else {
        alert(`Deployment failed: ${response.data.error}`)
      }
    } catch (error) {
      alert('Deployment failed. Please try again.')
    } finally {
      setDeploying(null)
    }
  }

  const isDeployed = (repoName: string) => {
    return deployments.some(d => d.repo_name === repoName)
  }

  const getInitials = (name: string) => {
    return name.split('-').map(word => word.charAt(0).toUpperCase()).join('').slice(0, 2)
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-black text-white flex items-center justify-center">
        <div className="flex items-center space-x-2">
          <RefreshCw className="h-6 w-6 animate-spin text-blue-500" />
          <span className="text-lg">Loading dashboard...</span>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-black text-white">
      {/* Top Header Bar */}
      <div className="border-b border-gray-800 bg-gray-900">
        <div className="flex justify-between items-center px-6 py-3">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-blue-500 rounded flex items-center justify-center">
              <Database className="h-5 w-5 text-white" />
            </div>
            <span className="text-lg font-medium">{user}'s projects</span>
            <div className="flex items-center space-x-1 text-sm text-gray-400">
              <span>Hobby</span>
              <ChevronDown className="h-4 w-4" />
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Find..."
                className="bg-gray-800 text-white pl-10 pr-4 py-2 rounded-lg border border-gray-700 focus:outline-none focus:border-blue-500"
              />
            </div>
            <button className="text-gray-400 hover:text-white">
              <HelpCircle className="h-5 w-5" />
            </button>
            <button className="text-gray-400 hover:text-white">
              <Bell className="h-5 w-5" />
            </button>
            <button className="text-gray-400 hover:text-white">
              <BookOpen className="h-5 w-5" />
            </button>
            <div className="w-8 h-8 bg-gray-600 rounded-full flex items-center justify-center">
              <span className="text-sm font-medium">{user.charAt(0).toUpperCase()}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Bar */}
      <div className="border-b border-gray-800 bg-gray-900">
        <div className="flex items-center space-x-8 px-6">
          <button
            onClick={() => setActiveTab('overview')}
            className={`py-4 px-1 border-b-2 transition-colors ${
              activeTab === 'overview' 
                ? 'border-blue-500 text-white' 
                : 'border-transparent text-gray-400 hover:text-white'
            }`}
          >
            Overview
          </button>
          <button
            onClick={() => setActiveTab('deployments')}
            className={`py-4 px-1 border-b-2 transition-colors ${
              activeTab === 'deployments' 
                ? 'border-blue-500 text-white' 
                : 'border-transparent text-gray-400 hover:text-white'
            }`}
          >
            Deployments
          </button>
          <button
            onClick={() => setActiveTab('repositories')}
            className={`py-4 px-1 border-b-2 transition-colors ${
              activeTab === 'repositories' 
                ? 'border-blue-500 text-white' 
                : 'border-transparent text-gray-400 hover:text-white'
            }`}
          >
            GitHub Repositories
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="px-6 py-8">
        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Left Column - Usage & Stats */}
            <div className="lg:col-span-1 space-y-6">
              {/* Usage Card */}
              <div className="bg-gray-900 border border-gray-800 rounded-lg p-6">
                <div className="flex justify-between items-start mb-4">
                  <h3 className="text-lg font-medium">Usage</h3>
                  <button className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded text-sm font-medium transition-colors">
                    Upgrade
                  </button>
                </div>
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-gray-400">Repositories</span>
                    <span className="text-white font-medium">{repositories.length}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-400">Deployments</span>
                    <span className="text-white font-medium">{deployments.length}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-400">Sections Indexed</span>
                    <span className="text-white font-medium">
                      {deployments.reduce((sum, d) => sum + d.sections_indexed, 0)}
                    </span>
                  </div>
                </div>
                <div className="mt-4 pt-4 border-t border-gray-800">
                  <span className="text-xs text-gray-500">Last 30 days</span>
                </div>
              </div>

              {/* Recent Deployments */}
              <div className="bg-gray-900 border border-gray-800 rounded-lg p-6">
                <h3 className="text-lg font-medium mb-4">Recent Deployments</h3>
                {deployments.length > 0 ? (
                  <div className="space-y-3">
                    {deployments.slice(0, 3).map((deployment, index) => (
                      <div key={index} className="flex items-center space-x-3">
                        <CheckCircle className="h-4 w-4 text-green-500" />
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-white truncate">{deployment.repo_name}</p>
                          <p className="text-xs text-gray-400">{deployment.sections_indexed} sections</p>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500 text-sm">No deployments yet</p>
                )}
              </div>
            </div>

            {/* Right Column - Projects Grid */}
            <div className="lg:col-span-2">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-semibold">Projects</h2>
                <div className="flex items-center space-x-2">
                  <button className="p-2 hover:bg-gray-800 rounded-lg transition-colors">
                    <Grid className="h-5 w-5 text-blue-500" />
                  </button>
                  <button className="p-2 hover:bg-gray-800 rounded-lg transition-colors">
                    <List className="h-5 w-5 text-gray-400" />
                  </button>
                  <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition-colors flex items-center space-x-2">
                    <Plus className="h-4 w-4" />
                    <span>Add New...</span>
                    <ChevronDown className="h-4 w-4" />
                  </button>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {repositories.map((repo) => (
                  <div key={repo.id} className="bg-gray-900 border border-gray-800 rounded-lg p-6 hover:border-gray-700 transition-colors">
                    <div className="flex justify-between items-start mb-4">
                      <div className="w-10 h-10 bg-gray-700 rounded flex items-center justify-center">
                        <span className="text-sm font-medium text-white">{getInitials(repo.name)}</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        {isDeployed(repo.full_name) && (
                          <CheckCircle className="h-4 w-4 text-green-500" />
                        )}
                        <button className="p-1 hover:bg-gray-800 rounded transition-colors">
                          <Settings className="h-4 w-4 text-gray-400" />
                        </button>
                      </div>
                    </div>
                    
                    <h3 className="text-lg font-medium text-white mb-2">{repo.name}</h3>
                    <p className="text-gray-400 text-sm mb-4 line-clamp-2">
                      {repo.description || 'No description available'}
                    </p>
                    
                    <div className="space-y-3 mb-4">
                      <div className="flex items-center space-x-2 text-sm text-gray-500">
                        <Github className="h-4 w-4" />
                        <span>{repo.full_name}</span>
                      </div>
                      <div className="flex items-center space-x-2 text-sm text-gray-500">
                        <Clock className="h-4 w-4" />
                        <span>{new Date(repo.updated_at).toLocaleDateString()}</span>
                      </div>
                    </div>

                    <div className="flex justify-between items-center">
                      <div className="flex items-center space-x-2 text-sm text-gray-400">
                        <GitBranch className="h-4 w-4" />
                        <span>main</span>
                      </div>
                      
                      {isDeployed(repo.full_name) ? (
                        <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-green-900 text-green-300">
                          Deployed
                        </span>
                      ) : (
                        <button
                          onClick={() => deployRepository(repo.html_url, repo.full_name)}
                          disabled={deploying === repo.full_name}
                          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors disabled:opacity-50"
                        >
                          {deploying === repo.full_name ? (
                            <div className="flex items-center space-x-2">
                              <RefreshCw className="h-4 w-4 animate-spin" />
                              <span>Deploying...</span>
                            </div>
                          ) : (
                            'Deploy'
                          )}
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'deployments' && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-semibold">Deployments</h2>
              <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition-colors">
                View All
              </button>
            </div>
            
            <div className="bg-gray-900 border border-gray-800 rounded-lg">
              <div className="p-6 border-b border-gray-800">
                <h3 className="text-lg font-medium">Recent Deployments</h3>
                <p className="text-gray-400 text-sm">Track your repository deployments and indexing progress</p>
              </div>
              
              <div className="divide-y divide-gray-800">
                {deployments.length > 0 ? (
                  deployments.map((deployment, index) => (
                    <div key={index} className="p-6 flex items-center justify-between">
                      <div>
                        <h4 className="font-medium text-white">{deployment.repo_name}</h4>
                        <p className="text-gray-400 text-sm">
                          {deployment.sections_indexed} sections indexed
                        </p>
                        <p className="text-gray-500 text-xs">
                          Deployed {new Date(deployment.deployed_at).toLocaleDateString()}
                        </p>
                      </div>
                      <div className="flex items-center space-x-2">
                        <CheckCircle className="h-5 w-5 text-green-500" />
                        <span className="text-sm font-medium text-green-400">Active</span>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="p-6 text-center">
                    <Database className="h-12 w-12 text-gray-600 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-gray-300 mb-2">No deployments yet</h3>
                    <p className="text-gray-500">Deploy your first repository to get started</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'repositories' && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-semibold">GitHub Repositories</h2>
              <div className="flex items-center space-x-2">
                <Search className="h-4 w-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search repositories..."
                  className="bg-gray-800 text-white px-3 py-2 rounded-lg border border-gray-700 focus:outline-none focus:border-blue-500"
                />
              </div>
            </div>
            
            <div className="bg-gray-900 border border-gray-800 rounded-lg">
              <div className="p-6 border-b border-gray-800">
                <h3 className="text-lg font-medium">Your Repositories</h3>
                <p className="text-gray-400 text-sm">Select repositories to deploy and index with Quilt</p>
              </div>
              
              <div className="divide-y divide-gray-800">
                {repositories.map((repo) => (
                  <div key={repo.id} className="p-6 flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <h4 className="font-medium text-white">{repo.name}</h4>
                        {isDeployed(repo.full_name) && (
                          <CheckCircle className="h-4 w-4 text-green-500" />
                        )}
                      </div>
                      <p className="text-gray-400 text-sm mb-2">
                        {repo.description || 'No description available'}
                      </p>
                      <div className="flex items-center space-x-4 text-xs text-gray-500">
                        <span>Updated {new Date(repo.updated_at).toLocaleDateString()}</span>
                        <a 
                          href={repo.html_url} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="text-blue-400 hover:text-blue-300 flex items-center space-x-1"
                        >
                          <span>View on GitHub</span>
                          <ExternalLink className="h-3 w-3" />
                        </a>
                      </div>
                    </div>
                    
                    <div className="ml-4">
                      {isDeployed(repo.full_name) ? (
                        <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-green-900 text-green-300">
                          Deployed
                        </span>
                      ) : (
                        <button
                          onClick={() => deployRepository(repo.html_url, repo.full_name)}
                          disabled={deploying === repo.full_name}
                          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors disabled:opacity-50"
                        >
                          {deploying === repo.full_name ? (
                            <div className="flex items-center space-x-2">
                              <RefreshCw className="h-4 w-4 animate-spin" />
                              <span>Deploying...</span>
                            </div>
                          ) : (
                            'Deploy'
                          )}
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default function Dashboard() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-black text-white flex items-center justify-center">
        <div className="flex items-center space-x-2">
          <RefreshCw className="h-6 w-6 animate-spin text-blue-500" />
          <span className="text-lg">Loading dashboard...</span>
        </div>
      </div>
    }>
      <DashboardContent />
    </Suspense>
  )
}
