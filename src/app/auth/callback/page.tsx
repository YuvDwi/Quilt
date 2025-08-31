'use client'

import { useEffect, useState, Suspense } from 'react'
import { useSearchParams, useRouter } from 'next/navigation'
import { RefreshCw } from 'lucide-react'
import axios from 'axios'

function AuthCallbackContent() {
  const searchParams = useSearchParams()
  const router = useRouter()
  const [status, setStatus] = useState('Connecting with GitHub...')

  useEffect(() => {
    const handleCallback = async () => {
      const code = searchParams?.get('code')
      const state = searchParams?.get('state')

      if (!code) {
        setStatus('Error: No authorization code received')
        return
      }

      try {
        setStatus('Exchanging authorization code...')
        
        const apiUrl = process.env.NEXT_PUBLIC_QUILT_API_URL
        if (!apiUrl) {
          throw new Error('API URL not configured')
        }
        

        const tokenResponse = await axios.post(`${apiUrl}/auth/github/callback`, {
          code: code,
          state: state
        }, {
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          }
        })

        const accessToken = tokenResponse.data.access_token
        const user = tokenResponse.data.user

        if (!accessToken || !user) {
          throw new Error('Failed to get access token or user info')
        }

        setStatus('Redirecting to dashboard...')


        window.location.href = `/dashboard?token=${accessToken}&user=${user.login}`

      } catch (error) {
        console.error('OAuth callback error:', error)
        setStatus('Authentication failed. Please try again.')
        setTimeout(() => {
          window.location.href = '/'
        }, 3000)
      }
    }


    const timer = setTimeout(handleCallback, 100)
    return () => clearTimeout(timer)
  }, [searchParams, router])

  return (
    <div className="min-h-screen flex items-center justify-center bg-black">
      <div className="text-center">
        <RefreshCw className="h-12 w-12 animate-spin text-purple-500 mx-auto mb-4" />
        <h2 className="text-xl font-semibold text-white mb-2">Connecting to GitHub</h2>
        <p className="text-gray-400">{status}</p>
      </div>
    </div>
  )
}

export default function AuthCallback() {
  return (
    <Suspense fallback={
      <div className="min-h-screen flex items-center justify-center bg-black">
        <div className="text-center">
          <RefreshCw className="h-12 w-12 animate-spin text-purple-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-white mb-2">Loading...</h2>
        </div>
      </div>
    }>
      <AuthCallbackContent />
    </Suspense>
  )
}
