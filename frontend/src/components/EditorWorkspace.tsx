import React from 'react'
import ReactDiffViewer from 'react-diff-viewer-continued'

interface EditorWorkspaceProps {
  previousDraft: string;
  currentDraft: string;
}

export default function EditorWorkspace({ previousDraft, currentDraft }: EditorWorkspaceProps) {
  if (!currentDraft && !previousDraft) {
    return (
      <div className="h-full flex flex-col items-center justify-center text-gray-500">
        <div className="w-16 h-16 rounded-full bg-white/5 flex items-center justify-center mb-4">
          <div className="w-8 h-8 border-2 border-gray-600 rounded-sm"></div>
        </div>
        <p className="text-lg font-medium text-gray-300">Workspace is empty</p>
        <p className="text-sm mt-1 text-center max-w-xs">Upload a contract and request a clause generation to begin visually redlining drafts.</p>
      </div>
    )
  }

  const customStyles = {
    variables: {
      dark: {
        diffViewerBackground: 'transparent',
        diffViewerColor: '#e2e8f0',
        addedBackground: 'rgba(16, 185, 129, 0.15)',
        addedColor: '#34d399',
        removedBackground: 'rgba(239, 68, 68, 0.15)',
        removedColor: '#f87171',
        wordAddedBackground: 'rgba(16, 185, 129, 0.4)',
        wordRemovedBackground: 'rgba(239, 68, 68, 0.4)',
        addedGutterBackground: 'rgba(16, 185, 129, 0.1)',
        removedGutterBackground: 'rgba(239, 68, 68, 0.1)',
        gutterBackground: 'transparent',
        gutterBackgroundDark: 'transparent',
        highlightBackground: 'rgba(255, 255, 255, 0.05)',
        highlightGutterBackground: 'rgba(255, 255, 255, 0.05)',
        codeFoldGutterBackground: 'transparent',
        codeFoldBackground: 'transparent',
        emptyLineBackground: 'transparent',
        gutterColor: '#6b7280',
        addedGutterColor: '#34d399',
        removedGutterColor: '#f87171',
      }
    },
    line: {
      fontSize: '14px',
      lineHeight: '1.6',
      fontFamily: 'Inter, sans-serif'
    }
  }

  return (
    <div className="h-full overflow-y-auto scrollbar-hide rounded-xl bg-[#0d1117]/50">
      <ReactDiffViewer
        oldValue={previousDraft}
        newValue={currentDraft}
        splitView={false}
        useDarkTheme={true}
        styles={customStyles}
        hideLineNumbers={false}
        showDiffOnly={false}
      />
    </div>
  )
}
