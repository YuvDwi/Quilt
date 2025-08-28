'use client'

import { useState, useEffect } from 'react'
import { useSearchParams } from 'next/navigation'
import { Github, Database, Clock, CheckCircle, AlertCircle, RefreshCw } from 'lucide-react'
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

export default function Dashboard() {
  const searchParams = useSearchParams()
  const [repositories, setRepositories] = useState<Repository[]>([])
  const [deployments, setDeployments] = useState<Deployment[]>([])
  const [loading, setLoading] = useState(true)
  const [deploying, setDeploying] = useState<string | null>(null)
  const [user, setUser] = useState<string>('')
  const [token, setToken] = useState<string>('')

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
        // Refresh deployments
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

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="flex items-center space-x-2">
          <RefreshCw className="h-6 w-6 animate-spin text-indigo-600" />
          <span className="text-lg">Loading repositories...</span>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <nav className="bg-white border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center space-x-2">
              <Database className="h-8 w-8 text-indigo-600" />
              <span className="text-2xl font-bold text-slate-900">Quilt</span>
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <Github className="h-5 w-5 text-slate-600" />
                <span className="text-slate-700 font-medium">{user}</span>
              </div>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats */}
        <div className="grid md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow-sm border border-slate-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-600">Total Repositories</p>
                <p className="text-2xl font-bold text-slate-900">{repositories.length}</p>
              </div>
              <Github className="h-8 w-8 text-slate-400" />
            </div>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow-sm border border-slate-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-600">Deployed</p>
                <p className="text-2xl font-bold text-slate-900">{deployments.length}</p>
              </div>
              <CheckCircle className="h-8 w-8 text-green-500" />
            </div>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow-sm border border-slate-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-600">Total Sections Indexed</p>
                <p className="text-2xl font-bold text-slate-900">
                  {deployments.reduce((sum, d) => sum + d.sections_indexed, 0)}
                </p>
              </div>
              <Database className="h-8 w-8 text-indigo-500" />
            </div>
          </div>
        </div>

        {/* Repositories */}
        <div className="bg-white rounded-lg shadow-sm border border-slate-200">
          <div className="px-6 py-4 border-b border-slate-200">
            <h2 className="text-lg font-semibold text-slate-900">Your Repositories</h2>
            <p className="text-sm text-slate-600">Select repositories to deploy and index with Quilt</p>
          </div>
          
          <div className="divide-y divide-slate-200">
            {repositories.map((repo) => (
              <div key={repo.id} className="px-6 py-4 flex items-center justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-2">
                    <h3 className="font-medium text-slate-900">{repo.name}</h3>
                    {isDeployed(repo.full_name) && (
                      <CheckCircle className="h-4 w-4 text-green-500" />
                    )}
                  </div>
                  <p className="text-sm text-slate-600 mt-1">
                    {repo.description || 'No description available'}
                  </p>
                  <div className="flex items-center space-x-4 mt-2 text-xs text-slate-500">
                    <span>Updated {new Date(repo.updated_at).toLocaleDateString()}</span>
                    <a 
                      href={repo.html_url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-indigo-600 hover:text-indigo-800"
                    >
                      View on GitHub
                    </a>
                  </div>
                </div>
                
                <div className="ml-4">
                  {isDeployed(repo.full_name) ? (
                    <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                      Deployed
                    </span>
                  ) : (
                    <button
                      onClick={() => deployRepository(repo.html_url, repo.full_name)}
                      disabled={deploying === repo.full_name}
                      className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors disabled:opacity-50"
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

        {/* Deployments */}
        {deployments.length > 0 && (
          <div className="mt-8 bg-white rounded-lg shadow-sm border border-slate-200">
            <div className="px-6 py-4 border-b border-slate-200">
              <h2 className="text-lg font-semibold text-slate-900">Recent Deployments</h2>
            </div>
            
            <div className="divide-y divide-slate-200">
              {deployments.map((deployment, index) => (
                <div key={index} className="px-6 py-4 flex items-center justify-between">
                  <div>
                    <h3 className="font-medium text-slate-900">{deployment.repo_name}</h3>
                    <p className="text-sm text-slate-600">
                      {deployment.sections_indexed} sections indexed
                    </p>
                    <p className="text-xs text-slate-500">
                      Deployed {new Date(deployment.deployed_at).toLocaleDateString()}
                    </p>
                  </div>
                  <div className="flex items-center space-x-2">
                    <CheckCircle className="h-5 w-5 text-green-500" />
                    <span className="text-sm font-medium text-green-600">Active</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
