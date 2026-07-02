const API_BASE_URL = 'http://localhost:8000/api'

export interface ChatResponse {
  draft: string;
  sources: Array<{
    document_title: string;
    chunk_index: number;
    text: string;
  }>;
}

export interface Risk {
  risk_level: string;
  issue: string;
  fix: string;
}

export const uploadDocument = async (file: File) => {
  const formData = new FormData()
  formData.append('file', file)
  
  const res = await fetch(`${API_BASE_URL}/upload`, {
    method: 'POST',
    body: formData,
  })
  if (!res.ok) throw new Error('Upload failed')
  return res.json()
}

export const generateDraft = async (sessionId: string, prompt: string): Promise<ChatResponse> => {
  const res = await fetch(`${API_BASE_URL}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, prompt }),
  })
  if (!res.ok) throw new Error('Generation failed')
  return res.json()
}

export const auditDraft = async (draft: string): Promise<{ risks: Risk[] }> => {
  const res = await fetch(`${API_BASE_URL}/audit`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ draft }),
  })
  if (!res.ok) throw new Error('Audit failed')
  return res.json()
}
