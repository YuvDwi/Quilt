'use client'

import { useState, useEffect, Suspense } from 'react'
import { useSearchParams } from 'next/navigation'
import { Github, Database, Clock, CheckCircle, AlertCircle, RefreshCw, Search, Plus, Grid, List, Settings, Bell, BookOpen, HelpCircle, ChevronDown, ExternalLink, GitBranch, Trash2 } from 'lucide-react'
import axios from 'axios'
import DeploymentSuccessModal from '../../components/DeploymentSuccessModal'
import Toast, { useToast } from '../../components/Toast'

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
  id: number
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
  const [showSuccessModal, setShowSuccessModal] = useState(false)
  const [deploymentResult, setDeploymentResult] = useState<any>(null)
  const [deleting, setDeleting] = useState<number | null>(null)
  const [token, setToken] = useState<string>('')
  const [activeTab, setActiveTab] = useState<'overview' | 'deployments' | 'repositories'>('overview')
  const { toast, showToast, hideToast } = useToast()

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

  const deleteDeployment = async (deploymentId: number, repoName: string) => {
    setDeleting(deploymentId)
    try {
      const response = await axios.delete(`${process.env.NEXT_PUBLIC_QUILT_API_URL}/deployments/${deploymentId}`)
      
      if (response.data.success) {
        await fetchDeployments(user)
        showToast(`Successfully deleted deployment for ${repoName}`, 'success')
      } else {
        showToast(`Failed to delete deployment: ${response.data.message}`, 'error')
      }
    } catch (error) {
      showToast('Failed to delete deployment. Please try again.', 'error')
    } finally {
      setDeleting(null)
    }
  }

  const deployRepository = async (repoUrl: string, repoName: string) => {
    setDeploying(repoName)
    try {
      const response = await axios.post(`${process.env.NEXT_PUBLIC_QUILT_API_URL}/deploy`, {
        user_id: user,
        repo_url: repoUrl,
        github_token: token
      })
      
      if (response.data.success) {
        await fetchDeployments(user)
        

        const deploymentData = {
          success: response.data.success,
          message: response.data.message,
          deployment_id: response.data.deployment_id,
          sections_indexed: response.data.sections_indexed,
          documents_added: response.data.documents_added,
          content_preview: Array.isArray(response.data.content_preview) ? response.data.content_preview : [],
          total_files_processed: response.data.total_files_processed,
          repo_name: repoName,
          repo_url: repoUrl,
          user_id: user,
          api_url: process.env.NEXT_PUBLIC_QUILT_API_URL || 'https://quilt-vkfk.onrender.com'
        }
        
        setDeploymentResult(deploymentData)
        setShowSuccessModal(true)
      } else {
        showToast(`Deployment failed: ${response.data.message}`, 'error')
      }
    } catch (error) {
      showToast('Deployment failed. Please try again.', 'error')
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
          <RefreshCw className="h-6 w-6 animate-spin text-purple-500" />
          <span className="text-lg font-light">Loading dashboard...</span>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-black text-white">

      <div className="border-b border-gray-700 bg-black">
        <div className="relative flex items-center justify-between px-6 py-3">
          <div className="flex items-center space-x-3">
            <span className="text-lg font-light">{user}'s projects</span>
            <div className="flex items-center space-x-1 text-sm text-gray-400">
              <span className="font-light">Hobby</span>
              <ChevronDown className="h-4 w-4" />
            </div>
          </div>
          
          <div className="absolute left-1/2 transform -translate-x-1/2">
            <span className="text-3xl font-sacramento text-white">quilt</span>
          </div>
          
          <div className="flex items-center space-x-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Find..."
                className="bg-gray-900 text-white pl-10 pr-4 py-2 rounded-lg border border-gray-600 focus:outline-none focus:border-purple-500 font-light"
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
              <span className="text-sm font-light">{user.charAt(0).toUpperCase()}</span>
            </div>
          </div>
        </div>
      </div>


      <div className="border-b border-gray-700 bg-black">
        <div className="flex items-center space-x-8 px-6">
          <button
            onClick={() => setActiveTab('overview')}
            className={`py-4 px-1 border-b-2 transition-colors font-light ${
              activeTab === 'overview' 
                ? 'border-purple-500 text-white' 
                : 'border-transparent text-gray-400 hover:text-white'
            }`}
          >
            Overview
          </button>
          <button
            onClick={() => setActiveTab('deployments')}
            className={`py-4 px-1 border-b-2 transition-colors font-light ${
              activeTab === 'deployments' 
                ? 'border-purple-500 text-white' 
                : 'border-transparent text-gray-400 hover:text-white'
            }`}
          >
            Deployments
          </button>
          <button
            onClick={() => setActiveTab('repositories')}
            className={`py-4 px-1 border-b-2 transition-colors font-light ${
              activeTab === 'repositories' 
                ? 'border-purple-500 text-white' 
                : 'border-transparent text-gray-400 hover:text-white'
            }`}
          >
            GitHub Repositories
          </button>
        </div>
      </div>


      <div className="px-6 py-8">
        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

            <div className="lg:col-span-1 space-y-6">

              <div className="bg-black border border-gray-700 rounded-lg p-6">
                <div className="mb-4">
                  <h3 className="text-lg font-light">Usage</h3>
                </div>
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-gray-400 font-light">Repositories</span>
                    <span className="text-white font-light">{repositories.length}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-400 font-light">Deployments</span>
                    <span className="text-white font-light">{deployments.length}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-400 font-light">Sections Indexed</span>
                    <span className="text-white font-light">
                      {deployments.reduce((sum, d) => sum + d.sections_indexed, 0)}
                    </span>
                  </div>
                </div>
                <div className="mt-4 pt-4 border-t border-gray-700">
                  <span className="text-xs text-gray-500 font-light">Last 30 days</span>
                </div>
              </div>


              <div className="bg-black border border-gray-700 rounded-lg p-6">
                <h3 className="text-lg font-light mb-4">Recent Deployments</h3>
                {deployments.length > 0 ? (
                  <div className="space-y-3">
                    {deployments.slice(0, 3).map((deployment, index) => (
                      <div key={index} className="flex items-center space-x-3">
                        <CheckCircle className="h-4 w-4 text-green-500" />
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-light text-white truncate">{deployment.repo_name}</p>
                          <p className="text-xs text-gray-400 font-light">{deployment.sections_indexed} sections</p>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500 text-sm font-light">No deployments yet</p>
                )}
              </div>
            </div>


            <div className="lg:col-span-2">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-light">Projects</h2>
                <div className="flex items-center space-x-2">
                  <button className="p-2 hover:bg-gray-800 rounded-lg transition-colors">
                    <div className="purple-gradient-icon rounded p-1">
                      <Grid className="h-5 w-5 text-white" />
                    </div>
                  </button>
                  <button className="p-2 hover:bg-gray-800 rounded-lg transition-colors">
                    <List className="h-5 w-5 text-gray-400" />
                  </button>
                  <button className="purple-gradient-btn text-white px-4 py-2 rounded-lg font-light flex items-center space-x-2 shadow-lg">
                    <Plus className="h-4 w-4" />
                    <span>Add New...</span>
                    <ChevronDown className="h-4 w-4" />
                  </button>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {repositories.map((repo) => (
                  <div key={repo.id} className="bg-black border border-gray-700 rounded-lg p-6 hover:border-gray-600 transition-colors">
                    <div className="flex justify-between items-start mb-4">
                      <div className="w-10 h-10 bg-gray-700 rounded flex items-center justify-center">
                        <span className="text-sm font-light text-white">{getInitials(repo.name)}</span>
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
                    
                    <h3 className="text-lg font-light text-white mb-2">{repo.name}</h3>
                    <p className="text-gray-400 text-sm mb-4 line-clamp-2 font-light">
                      {repo.description || 'No description available'}
                    </p>
                    
                    <div className="space-y-3 mb-4">
                      <div className="flex items-center space-x-2 text-sm text-gray-500">
                        <Github className="h-4 w-4" />
                        <span className="font-light">{repo.full_name}</span>
                      </div>
                      <div className="flex items-center space-x-2 text-sm text-gray-500">
                        <Clock className="h-4 w-4" />
                        <span className="font-light">{new Date(repo.updated_at).toLocaleDateString()}</span>
                      </div>
                    </div>

                    <div className="flex justify-between items-center">
                      <div className="flex items-center space-x-2 text-sm text-gray-400">
                        <GitBranch className="h-4 w-4" />
                        <span className="font-light">main</span>
                      </div>
                      
                      {isDeployed(repo.full_name) ? (
                        <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-light bg-green-900 text-green-300">
                          Deployed
                        </span>
                      ) : (
                        <button
                          onClick={() => deployRepository(repo.html_url, repo.full_name)}
                          disabled={deploying === repo.full_name}
                          className="purple-gradient-btn text-white px-4 py-2 rounded-lg text-sm font-light"
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
              <h2 className="text-2xl font-light">Deployments</h2>
              <button className="purple-gradient-btn text-white px-4 py-2 rounded-lg font-light shadow-lg">
                View All
              </button>
            </div>
            
            <div className="bg-black border border-gray-700 rounded-lg">
              <div className="p-6 border-b border-gray-700">
                <h3 className="text-lg font-light">Recent Deployments</h3>
                <p className="text-gray-400 text-sm font-light">Track your repository deployments and indexing progress</p>
              </div>
              
              <div className="divide-y divide-gray-700">
                {deployments.length > 0 ? (
                  deployments.map((deployment, index) => (
                    <div key={index} className="p-6 flex items-center justify-between">
                      <div>
                        <h4 className="font-light text-white">{deployment.repo_name}</h4>
                        <p className="text-gray-400 text-sm font-light">
                          {deployment.sections_indexed} sections indexed
                        </p>
                        <p className="text-gray-500 text-xs font-light">
                          Deployed {new Date(deployment.deployed_at).toLocaleDateString()}
                        </p>
                      </div>
                      <div className="flex items-center space-x-3">
                        <div className="flex items-center space-x-2">
                          <CheckCircle className="h-5 w-5 text-green-500" />
                          <span className="text-sm font-light text-green-400">Active</span>
                        </div>
                        <button
                          onClick={() => deleteDeployment(deployment.id, deployment.repo_name)}
                          disabled={deleting === deployment.id}
                          className="p-2 text-red-400 hover:text-red-300 hover:bg-red-500/10 rounded-lg transition-colors disabled:opacity-50"
                          title="Delete deployment"
                        >
                          {deleting === deployment.id ? (
                            <RefreshCw className="h-4 w-4 animate-spin" />
                          ) : (
                            <Trash2 className="h-4 w-4" />
                          )}
                        </button>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="p-6 text-center">
                    <Database className="h-12 w-12 text-gray-600 mx-auto mb-4" />
                    <h3 className="text-lg font-light text-gray-300 mb-2">No deployments yet</h3>
                    <p className="text-gray-500 font-light">Deploy your first repository to get started</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'repositories' && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-light">GitHub Repositories</h2>
              <div className="flex items-center space-x-2">
                <Search className="h-4 w-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search repositories..."
                  className="bg-gray-800 text-white px-3 py-2 rounded-lg border border-gray-600 focus:outline-none focus:border-purple-500 font-light"
                />
              </div>
            </div>
            
            <div className="bg-black border border-gray-700 rounded-lg">
              <div className="p-6 border-b border-gray-700">
                <h3 className="text-lg font-light">Your Repositories</h3>
                <p className="text-gray-400 text-sm font-light">Select repositories to deploy and index with Quilt</p>
              </div>
              
              <div className="divide-y divide-gray-700">
                {repositories.map((repo) => (
                  <div key={repo.id} className="p-6 flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <h4 className="font-light text-white">{repo.name}</h4>
                        {isDeployed(repo.full_name) && (
                          <CheckCircle className="h-4 w-4 text-green-500" />
                        )}
                      </div>
                      <p className="text-gray-400 text-sm mb-2 font-light">
                        {repo.description || 'No description available'}
                      </p>
                      <div className="flex items-center space-x-4 text-xs text-gray-500">
                        <span className="font-light">Updated {new Date(repo.updated_at).toLocaleDateString()}</span>
                        <a 
                          href={repo.html_url} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="text-purple-400 hover:text-purple-300 flex items-center space-x-1 font-light"
                        >
                          <span>View on GitHub</span>
                          <ExternalLink className="h-3 w-3" />
                        </a>
                      </div>
                    </div>
                    
                    <div className="ml-4">
                      {isDeployed(repo.full_name) ? (
                        <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-light bg-green-900 text-green-300">
                          Deployed
                        </span>
                      ) : (
                        <button
                          onClick={() => deployRepository(repo.html_url, repo.full_name)}
                          disabled={deploying === repo.full_name}
                          className="purple-gradient-btn text-white px-4 py-2 rounded-lg text-sm font-light"
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

      {/* Deployment Success Modal */}
      {showSuccessModal && deploymentResult && (
        <DeploymentSuccessModal
          isOpen={showSuccessModal}
          onClose={() => setShowSuccessModal(false)}
          deploymentData={deploymentResult}
        />
      )}

      {/* Toast Notification */}
      <Toast
        message={toast.message}
        type={toast.type}
        isVisible={toast.isVisible}
        onClose={hideToast}
      />
    </div>
  )
}

export default function Dashboard() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-black text-white flex items-center justify-center">
        <div className="flex items-center space-x-2">
          <RefreshCw className="h-6 w-6 animate-spin text-purple-500" />
          <span className="text-lg font-light">Loading dashboard...</span>
        </div>
      </div>
    }>
      <DashboardContent />
    </Suspense>
  )
}
