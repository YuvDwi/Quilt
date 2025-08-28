'use client'

import { useEffect, useState } from 'react'
import { useSearchParams, useRouter } from 'next/navigation'
import { RefreshCw } from 'lucide-react'
import axios from 'axios'

export default function AuthCallback() {
  const searchParams = useSearchParams()
  const router = useRouter()
  const [status, setStatus] = useState('Connecting with GitHub...')

  useEffect(() => {
    const handleCallback = async () => {
      const code = searchParams.get('code')
      const state = searchParams.get('state')

      if (!code) {
        setStatus('Error: No authorization code received')
        return
      }

      try {
        setStatus('Exchanging authorization code...')
        
        // Exchange code for access token via backend (more secure)
        const tokenResponse = await axios.post(`${process.env.NEXT_PUBLIC_QUILT_API_URL}/auth/github/callback`, {
          code: code,
          state: state
        }, {
          headers: {
            'Accept': 'application/json'
          }
        })

        const accessToken = tokenResponse.data.access_token
        const user = tokenResponse.data.user

        if (!accessToken || !user) {
          throw new Error('Failed to get access token or user info')
        }

        setStatus('Redirecting to dashboard...')

        // Redirect to dashboard with user info
        router.push(`/dashboard?token=${accessToken}&user=${user.login}`)

      } catch (error) {
        console.error('OAuth callback error:', error)
        setStatus('Authentication failed. Please try again.')
        setTimeout(() => {
          router.push('/')
        }, 3000)
      }
    }

    handleCallback()
  }, [searchParams, router])

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50">
      <div className="text-center">
        <RefreshCw className="h-12 w-12 animate-spin text-indigo-600 mx-auto mb-4" />
        <h2 className="text-xl font-semibold text-slate-900 mb-2">Connecting to GitHub</h2>
        <p className="text-slate-600">{status}</p>
      </div>
    </div>
  )
}
