import React from 'react'
import { FileText, BookOpen } from 'lucide-react'

interface Source {
  document_title: string;
  chunk_index: number;
  text: string;
}

export default function CitationPanel({ sources }: { sources: Source[] }) {
  if (!sources || sources.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-gray-500 space-y-3">
        <BookOpen className="w-8 h-8 opacity-50" />
        <span className="text-sm text-center px-4">Upload a document and prompt the AI to see exact source citations here.</span>
      </div>
    )
  }

  return (
    <div className="space-y-4 h-full overflow-y-auto scrollbar-hide pb-20">
      <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider sticky top-0 bg-[#0a0a0a]/80 backdrop-blur-md py-2 z-10">Retrieved Context</h3>
      {sources.map((src, idx) => (
        <div key={idx} className="p-4 rounded-xl glass-panel hover:bg-white/5 transition-colors group cursor-default">
          <div className="flex items-center space-x-2 mb-3">
            <div className="p-1.5 bg-accent/20 rounded-md text-accent">
              <FileText className="w-4 h-4" />
            </div>
            <div className="flex-1 overflow-hidden">
              <p className="text-xs font-semibold text-gray-200 truncate">{src.document_title}</p>
              <p className="text-[10px] text-gray-500">Chunk {src.chunk_index}</p>
            </div>
          </div>
          <div className="text-xs text-gray-400 leading-relaxed border-l-2 border-accent/30 pl-3 group-hover:border-accent transition-colors">
            "{src.text}"
          </div>
        </div>
      ))}
    </div>
  )
}
