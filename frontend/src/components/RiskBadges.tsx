import React from 'react'
import { AlertTriangle, ShieldAlert, AlertCircle } from 'lucide-react'
import { Risk } from '../lib/api'

export default function RiskBadges({ risks }: { risks: Risk[] }) {
  if (!risks || risks.length === 0) {
    return (
      <div className="flex items-center space-x-2 text-green-400 p-3 bg-green-400/10 rounded-lg border border-green-400/20">
        <ShieldAlert className="w-4 h-4" />
        <span className="text-sm font-medium">Compliance Auditor: No critical risks detected.</span>
      </div>
    )
  }

  return (
    <div className="space-y-2">
      <div className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-3">Auditor Warnings</div>
      {risks.map((risk, idx) => {
        const isHigh = risk.risk_level.toLowerCase() === 'high'
        const isMed = risk.risk_level.toLowerCase() === 'medium'
        return (
          <div key={idx} className={`p-4 rounded-xl border glass-panel relative overflow-hidden transition-all hover:scale-[1.01] ${isHigh ? 'border-red-500/30 bg-red-500/5' : isMed ? 'border-yellow-500/30 bg-yellow-500/5' : 'border-blue-500/30 bg-blue-500/5'}`}>
            <div className={`absolute top-0 left-0 w-1 h-full ${isHigh ? 'bg-red-500' : isMed ? 'bg-yellow-500' : 'bg-blue-500'}`} />
            <div className="flex items-start justify-between mb-2">
              <div className="flex items-center space-x-2">
                {isHigh ? <AlertTriangle className="text-red-400 w-4 h-4" /> : <AlertCircle className="text-yellow-400 w-4 h-4" />}
                <span className={`text-sm font-bold ${isHigh ? 'text-red-400' : 'text-yellow-400'}`}>{risk.risk_level} Risk</span>
              </div>
            </div>
            <p className="text-sm text-gray-200 mb-2"><strong className="text-gray-400">Issue:</strong> {risk.issue}</p>
            <p className="text-sm text-green-300"><strong className="text-green-500/50">Fix:</strong> {risk.fix}</p>
          </div>
        )
      })}
    </div>
  )
}
