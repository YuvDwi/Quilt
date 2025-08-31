'use client'

import { useState, useEffect } from 'react'
import { CheckCircle, AlertCircle, X } from 'lucide-react'

interface ToastProps {
  message: string
  type: 'success' | 'error'
  isVisible: boolean
  onClose: () => void
  duration?: number
}

export default function Toast({ message, type, isVisible, onClose, duration = 4000 }: ToastProps) {
  useEffect(() => {
    if (isVisible) {
      const timer = setTimeout(() => {
        onClose()
      }, duration)
      return () => clearTimeout(timer)
    }
  }, [isVisible, onClose, duration])

  if (!isVisible) return null

  return (
    <div className="fixed top-4 right-4 z-50 animate-slide-in-right">
      <div className={`
        flex items-center space-x-3 px-4 py-3 rounded-lg shadow-lg border
        ${type === 'success' 
          ? 'bg-green-900/90 border-green-500/50 text-green-100' 
          : 'bg-red-900/90 border-red-500/50 text-red-100'
        }
        backdrop-blur-sm max-w-md
      `}>
        {type === 'success' ? (
          <CheckCircle className="h-5 w-5 text-green-400 flex-shrink-0" />
        ) : (
          <AlertCircle className="h-5 w-5 text-red-400 flex-shrink-0" />
        )}
        <p className="text-sm font-medium flex-1">{message}</p>
        <button
          onClick={onClose}
          className={`
            p-1 rounded-full transition-colors flex-shrink-0
            ${type === 'success' 
              ? 'hover:bg-green-800/50 text-green-300 hover:text-green-100' 
              : 'hover:bg-red-800/50 text-red-300 hover:text-red-100'
            }
          `}
        >
          <X className="h-4 w-4" />
        </button>
      </div>
    </div>
  )
}

// Hook for managing toast state
export function useToast() {
  const [toast, setToast] = useState<{
    message: string
    type: 'success' | 'error'
    isVisible: boolean
  }>({
    message: '',
    type: 'success',
    isVisible: false
  })

  const showToast = (message: string, type: 'success' | 'error') => {
    setToast({ message, type, isVisible: true })
  }

  const hideToast = () => {
    setToast(prev => ({ ...prev, isVisible: false }))
  }

  return { toast, showToast, hideToast }
}
