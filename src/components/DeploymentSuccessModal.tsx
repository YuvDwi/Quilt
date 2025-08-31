'use client'

import React from 'react'
import { X, CheckCircle, Copy, ExternalLink, Database, Zap, Brain, Code, Globe } from 'lucide-react'

interface ContentPreview {
  file_path: string
  content_type: string
  content_preview: string
  word_count: number
  section_title: string
}

interface DeploymentData {
  success: boolean
  message: string
  deployment_id?: number
  sections_indexed: number
  documents_added?: number
  content_preview?: ContentPreview[]
  total_files_processed?: number
  repo_name: string
  repo_url: string
  user_id: string
  api_url: string
}

interface DeploymentSuccessModalProps {
  isOpen: boolean
  onClose: () => void
  deploymentData: DeploymentData
}

const DeploymentSuccessModal: React.FC<DeploymentSuccessModalProps> = ({
  isOpen,
  onClose,
  deploymentData
}) => {
  const [copiedText, setCopiedText] = React.useState<string>('')

  if (!isOpen) return null

  const copyToClipboard = async (text: string, label: string) => {
    try {
      await navigator.clipboard.writeText(text)
      setCopiedText(label)
      setTimeout(() => setCopiedText(''), 2000)
    } catch (err) {
      console.error('Failed to copy text: ', err)
    }
  }

  const apiEndpoints = {
    stats: `${deploymentData.api_url}/stats`,
    deployments: `${deploymentData.api_url}/deployments/${deploymentData.user_id}`,
    health: `${deploymentData.api_url}/health`
  }

  const llmIntegrations = [
    {
      name: "Claude Desktop (MCP)",
      icon: <Brain className="h-5 w-5" />,
      description: "Direct integration with Claude Desktop via Model Context Protocol",
      setup: [
        "1. Create config file:",
        "~/Library/Application Support/Claude/claude_desktop_config.json",
        "",
        "2. Add this configuration:",
        JSON.stringify({
          "mcpServers": {
            "quilt-search": {
              "command": "/usr/local/bin/python3",
              "args": ["/path/to/your/mcp_server.py"],
              "env": {
                "CLOUD_API_URL": deploymentData.api_url
              }
            }
          }
        }, null, 2),
        "",
        "3. Restart Claude Desktop",
        "4. Ask: 'Search my database for [topic]'"
      ],
      color: "bg-purple-500"
    },
    {
      name: "ChatGPT (Custom GPT)",
      icon: <Zap className="h-5 w-5" />,
      description: "Create a Custom GPT with your API as an action",
      setup: [
        "1. Go to ChatGPT → Create a GPT",
        "2. In Actions, add this OpenAPI schema:",
        "3. Set base URL: " + deploymentData.api_url,
        "4. Add endpoints: /stats, /deployments/{user_id}",
        "5. Test with your repository data"
      ],
      color: "bg-green-500"
    },
    {
      name: "Ollama (Local LLM)",
      icon: <Database className="h-5 w-5" />,
      description: "Use with local models via API calls",
      setup: [
        "1. Install Ollama: https://ollama.ai",
        "2. Pull a model: ollama pull llama2",
        "3. Create integration script:",
        "4. Use curl or Python requests to query your API",
        "5. Feed results to Ollama for processing"
      ],
      color: "bg-blue-500"
    },
    {
      name: "Direct API Access",
      icon: <Code className="h-5 w-5" />,
      description: "Use with any LLM via HTTP requests",
      setup: [
        "1. Make HTTP requests to your API endpoints",
        "2. Parse the JSON response",
        "3. Feed content to your preferred LLM",
        "4. Available in any programming language"
      ],
      color: "bg-orange-500"
    }
  ]

  return (
    <div className="fixed inset-0 bg-black bg-opacity-80 flex items-center justify-center z-50 p-4">
      <div className="bg-black rounded-lg max-w-6xl w-full max-h-[90vh] overflow-y-auto border border-gray-600 shadow-2xl shadow-gray-500/20">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-600 bg-gradient-to-r from-gray-800/50 to-black">
          <div className="flex items-center space-x-3">
            <CheckCircle className="h-8 w-8 text-green-400" />
            <div>
              <h2 className="text-2xl font-bold text-white">Deployment Successful!</h2>
              <p className="text-gray-300">Your repository has been indexed and is ready to use</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        <div className="p-6 space-y-8">
          {/* LLM Access Notification */}
          <div className="bg-gradient-to-r from-green-900/30 to-gray-800/30 rounded-lg p-6 border-2 border-green-500/50 relative overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-r from-green-500/10 to-gray-500/10 animate-pulse"></div>
            <div className="relative z-10">
              <div className="flex items-center mb-4">
                <div className="bg-green-500 rounded-full p-2 mr-3">
                  <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <h3 className="text-2xl font-bold text-white">Your Content is Now LLM-Accessible!</h3>
              </div>
              
              <div className="bg-black/30 rounded-lg p-4 mb-4 border border-green-500/30">
                <p className="text-green-300 text-lg font-semibold mb-2">
                  Any LLM connected to Quilt's MCP server can now search and access your deployed content!
                </p>
                <p className="text-gray-200 text-sm">
                  Your <code className="bg-gray-600/30 px-2 py-1 rounded text-blue-300">data-llm</code> tagged content from <strong>{deploymentData.repo_name}</strong> is indexed and searchable by:
                </p>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-2 mt-3">
                  <div className="bg-blue-500/20 rounded px-3 py-2 text-center">
                    <p className="text-blue-300 font-semibold text-sm">Claude Desktop</p>
                  </div>
                  <div className="bg-green-500/20 rounded px-3 py-2 text-center">
                    <p className="text-green-300 font-semibold text-sm">ChatGPT</p>
                  </div>
                  <div className="bg-cyan-500/20 rounded px-3 py-2 text-center">
                    <p className="text-cyan-300 font-semibold text-sm">Ollama</p>
                  </div>
                  <div className="bg-gray-500/20 rounded px-3 py-2 text-center">
                    <p className="text-gray-300 font-semibold text-sm">Any LLM</p>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-black/20 rounded-lg p-4 border border-blue-500/20">
                  <h4 className="text-white font-semibold mb-2 flex items-center">
                    <span className="bg-blue-500 rounded-full w-6 h-6 flex items-center justify-center text-white text-sm mr-2">1</span>
                    LLMs Can Search Your Content
                  </h4>
                  <p className="text-gray-200 text-sm">
                    Any LLM with Quilt MCP access can search through your {deploymentData.sections_indexed} indexed sections using natural language queries.
                  </p>
                </div>
                <div className="bg-black/20 rounded-lg p-4 border border-green-500/20">
                  <h4 className="text-white font-semibold mb-2 flex items-center">
                    <span className="bg-green-500 rounded-full w-6 h-6 flex items-center justify-center text-white text-sm mr-2">2</span>
                    Instant Knowledge Access
                  </h4>
                  <p className="text-green-200 text-sm">
                    LLMs can instantly retrieve and reference your website's information to provide accurate, contextual responses.
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Deployed Content Preview */}
          {deploymentData.content_preview && deploymentData.content_preview.length > 0 && (
            <div className="bg-gradient-to-br from-gray-800/30 to-black rounded-lg p-6 border border-gray-600/30">
              <h3 className="text-xl font-semibold text-white mb-4 flex items-center">
                <Database className="h-5 w-5 mr-2 text-blue-400" />
                Deployed Content Preview
              </h3>
              <div className="grid grid-cols-1 gap-4 max-h-96 overflow-y-auto">
                {deploymentData.content_preview.map((content, index) => (
                  <div key={index} className="bg-black/50 rounded-lg p-4 border border-gray-600/20">
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex-1">
                        <h4 className="text-blue-300 font-medium text-sm mb-1">
                          {content.section_title}
                        </h4>
                        <p className="text-gray-400 text-xs font-mono">
                          {content.file_path}
                        </p>
                      </div>
                      <div className="flex items-center space-x-3 text-xs">
                        <span className="bg-blue-500/20 text-blue-300 px-2 py-1 rounded">
                          {content.content_type}
                        </span>
                        <span className="text-gray-400">
                          {content.word_count} words
                        </span>
                      </div>
                    </div>
                    <div className="bg-black/30 rounded p-3 mt-2">
                      <p className="text-gray-300 text-sm font-mono leading-relaxed">
                        {content.content_preview}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
              <div className="mt-4 flex items-center justify-between text-sm">
                <p className="text-gray-300">
                  Showing {deploymentData.content_preview.length} of {deploymentData.sections_indexed} indexed sections
                </p>
                <p className="text-gray-400">
                  {deploymentData.total_files_processed} files processed
                </p>
              </div>
            </div>
          )}

          {/* Deployment Summary */}
          <div className="bg-gradient-to-br from-purple-900/20 to-black rounded-lg p-6 border border-purple-500/20">
            <h3 className="text-xl font-semibold text-white mb-4 flex items-center">
              <Database className="h-5 w-5 mr-2 text-purple-500" />
              Deployment Summary
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-3">
                <div>
                  <label className="text-sm text-gray-400">Repository</label>
                  <p className="text-white font-mono">{deploymentData.repo_name}</p>
                </div>
                <div>
                  <label className="text-sm text-purple-400">Sections Indexed</label>
                  <p className="text-white text-2xl font-bold text-purple-400">{deploymentData.sections_indexed}</p>
                </div>
                <div>
                  <label className="text-sm text-gray-400">Deployment ID</label>
                  <p className="text-white font-mono">#{deploymentData.deployment_id}</p>
                </div>
              </div>
              <div className="space-y-3">
                <div>
                  <label className="text-sm text-gray-400">User</label>
                  <p className="text-white">{deploymentData.user_id}</p>
                </div>
                <div>
                  <label className="text-sm text-purple-400">Status</label>
                  <p className="text-purple-400 font-semibold">Successfully Deployed</p>
                </div>
                <div>
                  <label className="text-sm text-gray-400">Cloud API</label>
                  <div className="flex items-center space-x-2">
                    <p className="text-white font-mono text-sm">{deploymentData.api_url}</p>
                    <button
                      onClick={() => copyToClipboard(deploymentData.api_url, 'API URL')}
                      className="text-gray-400 hover:text-white"
                    >
                      <Copy className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* API Endpoints */}
          <div className="bg-gradient-to-br from-purple-900/20 to-black rounded-lg p-6 border border-purple-500/20">
            <h3 className="text-xl font-semibold text-white mb-4 flex items-center">
              <Globe className="h-5 w-5 mr-2 text-purple-400" />
              Available API Endpoints
            </h3>
            <div className="space-y-3">
              {Object.entries(apiEndpoints).map(([name, url]) => (
                <div key={name} className="flex items-center justify-between bg-black/50 rounded p-3 border border-purple-500/20">
                  <div>
                    <p className="text-white font-semibold capitalize">{name}</p>
                    <p className="text-purple-300 text-sm font-mono">{url}</p>
                  </div>
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => copyToClipboard(url, name)}
                      className="text-purple-400 hover:text-white p-1"
                      title="Copy URL"
                    >
                      <Copy className="h-4 w-4" />
                    </button>
                    <a
                      href={url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-purple-400 hover:text-white p-1"
                      title="Open in new tab"
                    >
                      <ExternalLink className="h-4 w-4" />
                    </a>
                  </div>
                </div>
              ))}
            </div>
            {copiedText && (
              <p className="text-purple-400 text-sm mt-2">{copiedText} copied to clipboard!</p>
            )}
          </div>

          {/* LLM Integration Guides */}
          <div className="bg-gradient-to-br from-purple-900/20 to-black rounded-lg p-6 border border-purple-500/20">
            <h3 className="text-xl font-semibold text-white mb-4 flex items-center">
              <Brain className="h-5 w-5 mr-2 text-purple-400" />
              LLM Integration Options
            </h3>
            <p className="text-purple-300 mb-6">
              Your data is now searchable! Here's how to integrate it with different LLMs:
            </p>
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {llmIntegrations.map((integration, index) => (
                <div key={index} className="bg-black/50 rounded-lg p-4 border border-purple-500/20">
                  <div className="flex items-center space-x-3 mb-3">
                    <div className={`p-2 rounded ${integration.color}`}>
                      {integration.icon}
                    </div>
                    <div>
                      <h4 className="text-white font-semibold">{integration.name}</h4>
                      <p className="text-purple-300 text-sm">{integration.description}</p>
                    </div>
                  </div>
                  
                  <div className="bg-black/30 rounded p-3 mt-3 border border-purple-500/10">
                    <h5 className="text-white text-sm font-semibold mb-2">Setup Instructions:</h5>
                    <div className="text-purple-200 text-xs font-mono space-y-1">
                      {integration.setup.map((step, stepIndex) => (
                        <div key={stepIndex} className={step.startsWith('{') ? 'bg-black/50 p-2 rounded overflow-x-auto border border-purple-500/20' : ''}>
                          {step}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Quick Test */}
          <div className="bg-gradient-to-br from-purple-900/20 to-black rounded-lg p-6 border border-purple-500/20">
            <h3 className="text-xl font-semibold text-white mb-4">Quick Test</h3>
            <p className="text-purple-300 mb-4">Test your deployment right now:</p>
            <div className="bg-black/50 rounded p-4 font-mono text-sm border border-purple-500/20">
              <p className="text-purple-400"># Get your deployment stats</p>
              <p className="text-purple-300">curl "{apiEndpoints.stats}"</p>
              <br />
              <p className="text-purple-400"># Get your deployments</p>
              <p className="text-purple-300">curl "{apiEndpoints.deployments}"</p>
            </div>
          </div>

          {/* Next Steps */}
          <div className="bg-gradient-to-r from-purple-900/50 to-black rounded-lg p-6 border border-purple-500/30">
            <h3 className="text-xl font-semibold text-white mb-4">Connect Your LLM</h3>
            <p className="text-purple-300 mb-4">Set up MCP connection to start using your deployed content:</p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
              <div className="bg-black/50 rounded p-4 border border-purple-500/20">
                <h4 className="text-white font-semibold mb-2">1. Choose Your LLM</h4>
                <p className="text-purple-200">Pick from Claude Desktop, ChatGPT, Ollama, or direct API access</p>
              </div>
              <div className="bg-black/50 rounded p-4 border border-purple-500/20">
                <h4 className="text-white font-semibold mb-2">2. Set Up MCP Connection</h4>
                <p className="text-purple-200">Follow the setup guide for your chosen LLM above</p>
              </div>
              <div className="bg-black/50 rounded p-4 border border-purple-500/20">
                <h4 className="text-white font-semibold mb-2">3. Start Asking Questions!</h4>
                <p className="text-purple-200">LLMs can now search and reference your {deploymentData.repo_name} content</p>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="border-t border-purple-500/30 p-6 flex justify-center items-center bg-gradient-to-r from-purple-900/10 to-black">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
            <p className="text-purple-300 text-sm">
              <strong className="text-green-400">Live:</strong> Your content is now accessible by any LLM with Quilt MCP connection
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default DeploymentSuccessModal
