import React, { useState, useRef, useEffect } from 'react'
import { Send, Loader2 } from 'lucide-react'

interface ChatInterfaceProps {
  onSend: (prompt: string) => void;
  isLoading: boolean;
}

export default function ChatInterface({ onSend, isLoading }: ChatInterfaceProps) {
  const [prompt, setPrompt] = useState('')
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    if (!isLoading) {
      inputRef.current?.focus()
    }
  }, [isLoading])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!prompt.trim() || isLoading) return
    onSend(prompt)
    setPrompt('')
  }

  return (
    <form onSubmit={handleSubmit} className="flex items-center space-x-3 w-full relative">
      <div className="relative flex-1">
        <input
          ref={inputRef}
          type="text"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="E.g., Draft a non-compete clause, but limit the term to 1 year..."
          disabled={isLoading}
          className="w-full bg-black/40 border border-white/10 rounded-2xl py-4 pl-5 pr-14 text-sm focus:outline-none focus:ring-2 focus:ring-accent/50 focus:border-accent/50 transition-all text-white disabled:opacity-50 placeholder:text-gray-500 shadow-inner"
        />
        <div className="absolute right-2 top-1/2 -translate-y-1/2">
          <button
            type="submit"
            disabled={!prompt.trim() || isLoading}
            className="p-2.5 rounded-xl bg-accent hover:bg-accent/80 text-white disabled:opacity-50 disabled:hover:bg-accent transition-all shadow-lg shadow-accent/20"
          >
            {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
          </button>
        </div>
      </div>
    </form>
  )
}
