'use client'

import React, { useState, useEffect } from 'react'
import { UploadCloud, Shield, CheckCircle2, FileUp } from 'lucide-react'
import ChatInterface from '../components/ChatInterface'
import EditorWorkspace from '../components/EditorWorkspace'
import CitationPanel from '../components/CitationPanel'
import RiskBadges from '../components/RiskBadges'
import { generateDraft, auditDraft, uploadDocument, ChatResponse, Risk } from '../lib/api'

export default function Dashboard() {
  const [sessionId] = useState(() => Math.random().toString(36).substring(7))
  const [previousDraft, setPreviousDraft] = useState('')
  const [currentDraft, setCurrentDraft] = useState('')
  const [sources, setSources] = useState<ChatResponse['sources']>([])
  const [risks, setRisks] = useState<Risk[]>([])
  
  const [isGenerating, setIsGenerating] = useState(false)
  const [isAuditing, setIsAuditing] = useState(false)
  const [isUploading, setIsUploading] = useState(false)
  const [uploadStatus, setUploadStatus] = useState<string | null>(null)

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    
    setIsUploading(true)
    setUploadStatus(null)
    try {
      await uploadDocument(file)
      setUploadStatus('Document ingested successfully.')
      setTimeout(() => setUploadStatus(null), 3000)
    } catch (err) {
      setUploadStatus('Upload failed.')
    } finally {
      setIsUploading(false)
    }
  }

  const handleSendPrompt = async (prompt: string) => {
    setIsGenerating(true)
    setIsAuditing(false)
    setRisks([])
    
    try {
      const response = await generateDraft(sessionId, prompt)
      
      setPreviousDraft(currentDraft)
      setCurrentDraft(response.draft)
      setSources(response.sources)
      
      // Feature 5: Automated Risk Auditor trigger
      if (response.draft && !response.draft.includes("Insufficient reference context")) {
        setIsAuditing(true)
        try {
          const auditRes = await auditDraft(response.draft)
          setRisks(auditRes.risks)
        } catch (err) {
          console.error("Audit failed", err)
        } finally {
          setIsAuditing(false)
        }
      }
    } catch (err) {
      console.error("Generation failed", err)
    } finally {
      setIsGenerating(false)
    }
  }

  return (
    <div className="h-screen flex overflow-hidden bg-gradient-to-br from-background to-black">
      {/* Sidebar: Dynamic Ingestion & Exact Citations */}
      <div className="w-80 border-r border-white/10 glass-panel flex flex-col z-10 relative shadow-2xl">
        <div className="p-6 border-b border-white/10">
          <div className="flex items-center space-x-3 mb-6">
            <div className="p-2 bg-gradient-to-tr from-accent to-primary rounded-xl shadow-lg">
              <Shield className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-sm font-bold tracking-tight text-white">Aegis Legal Tech</h1>
              <p className="text-[10px] text-gray-400 font-medium tracking-widest uppercase">AI-Powered Assistant</p>
            </div>
          </div>
          
          <div className="space-y-4">
            <label className={`flex items-center justify-center space-x-2 w-full p-3 rounded-xl border border-dashed transition-all cursor-pointer ${isUploading ? 'border-primary/50 bg-primary/10 text-primary' : 'border-gray-600 hover:border-gray-400 hover:bg-white/5 text-gray-400'}`}>
              {isUploading ? <UploadCloud className="w-4 h-4 animate-bounce" /> : <FileUp className="w-4 h-4" />}
              <span className="text-xs font-semibold">{isUploading ? 'Ingesting...' : 'Upload Contract (PDF/DOCX)'}</span>
              <input type="file" className="hidden" accept=".pdf,.docx" onChange={handleFileUpload} disabled={isUploading} />
            </label>
            {uploadStatus && (
              <div className="flex items-center space-x-2 text-xs text-green-400 bg-green-400/10 p-2 rounded-lg border border-green-400/20">
                <CheckCircle2 className="w-3 h-3" />
                <span>{uploadStatus}</span>
              </div>
            )}
          </div>
        </div>
        
        <div className="flex-1 overflow-hidden p-6">
          <CitationPanel sources={sources} />
        </div>
      </div>

      {/* Main Panel: Interactive Workspace & AI Orchaestration */}
      <div className="flex-1 flex flex-col relative z-0">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-primary/10 via-background to-background -z-10" />
        
        <div className="flex-1 p-6 overflow-hidden flex flex-col min-h-0 space-y-6">
          {/* Header */}
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-medium text-gray-200">Interactive Redlining Workspace</h2>
            <div className="flex items-center space-x-2">
              <span className="flex h-2 w-2 relative">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
              </span>
              <span className="text-xs font-medium text-green-500 uppercase tracking-widest">RAG Engine Online</span>
            </div>
          </div>

          {/* Visual Redlining (Diff Viewer) */}
          <div className="flex-1 relative glass-panel rounded-2xl shadow-xl overflow-hidden p-1 border border-white/5">
            <EditorWorkspace previousDraft={previousDraft} currentDraft={currentDraft} />
          </div>
          
          {/* Risk Badges */}
          {currentDraft && !currentDraft.includes("Insufficient reference context") && (
            <div className="max-h-48 overflow-y-auto scrollbar-hide">
              {isAuditing ? (
                <div className="flex items-center space-x-2 text-sm text-gray-400 p-4 border border-white/10 rounded-xl glass-panel animate-pulse">
                  <Shield className="w-4 h-4 text-accent" />
                  <span>Compliance Auditor scanning for vulnerabilities...</span>
                </div>
              ) : (
                <RiskBadges risks={risks} />
              )}
            </div>
          )}
        </div>

        {/* Input Bar (Multi-Turn Refinement) */}
        <div className="p-6 pt-0">
          <ChatInterface onSend={handleSendPrompt} isLoading={isGenerating} />
        </div>
      </div>
    </div>
  )
}
