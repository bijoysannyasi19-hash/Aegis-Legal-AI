import json
from typing import List, Dict, Any
from pydantic import BaseModel
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

from app.core.config import settings
from app.core.ingestion import DocumentChunk

# Configure the official Google GenAI SDK
genai.configure(api_key=settings.gemini_api_key)

class GenerationResponse(BaseModel):
    draft: str
    sources: List[Dict[str, Any]]

class GeneratorPipeline:
    def __init__(self):
        # Dictionary to track active ChatSession objects for multi-turn conversations
        self.sessions: Dict[str, genai.ChatSession] = {}
        
        safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        }

        # Primary Drafting Agent setup
        self.primary_model = genai.GenerativeModel(
            model_name="gemini-pro",
            safety_settings=safety_settings,
            generation_config=genai.types.GenerationConfig(
                temperature=0.1, # Low temp for legally precise, structured output
            )
        )
        
        # Secondary Auditor Agent setup
        self.auditor_model = genai.GenerativeModel(
            model_name="gemini-pro",
            safety_settings=safety_settings,
            generation_config=genai.types.GenerationConfig(
                temperature=0.0, # Absolute determinism for the auditor
            )
        )

    def _get_or_create_chat(self, session_id: str) -> genai.ChatSession:
        if session_id not in self.sessions:
            self.sessions[session_id] = self.primary_model.start_chat(history=[])
        return self.sessions[session_id]

    def generate_draft(self, session_id: str, prompt: str, context_chunks: List[DocumentChunk]) -> GenerationResponse:
        chat = self._get_or_create_chat(session_id)
        
        if not context_chunks:
            return GenerationResponse(
                draft="Insufficient reference context found to draft this clause.",
                sources=[]
            )
            
        context_text = ""
        sources = []
        for c in context_chunks:
            context_text += f"\n--- Document: {c.document_title} (Chunk {c.chunk_index}) ---\n{c.text}\n"
            sources.append({
                "document_id": c.document_id,
                "document_title": c.document_title,
                "chunk_index": c.chunk_index,
                "text": c.text,
                "upload_date": c.upload_date
            })
            
        system_instruction = (
            "You are an elite corporate attorney. Your task is to draft or modify legal clauses strictly based on the provided reference context.\n\n"
            "CRITICAL ZERO-HALLUCINATION GUARDRAIL:\n"
            "You must draft clauses based EXCLUSIVELY on the provided retrieved context. "
            "If the context is insufficient or missing to fulfill the user's request, you must explicitly output ONLY this exact phrase: "
            "'Insufficient reference context found to draft this clause.'\n\n"
            "Do not introduce external facts, concepts, or durations not found in the context. "
            f"REFERENCE CONTEXT:\n{context_text}"
        )
        
        full_prompt = f"{system_instruction}\n\nUSER REQUEST:\n{prompt}"
        
        try:
            response = chat.send_message(full_prompt)
            draft = response.text.strip()
            
            # Prune memory if it gets too large to prevent overflow during long sessions
            if len(chat.history) > 10:
                chat.history = chat.history[-10:]
                
            return GenerationResponse(
                draft=draft,
                sources=sources
            )
        except Exception as e:
            print(f"Error during generation: {str(e)}")
            return GenerationResponse(draft="Error generating draft.", sources=sources)

    def run_compliance_audit(self, draft: str) -> List[Dict[str, str]]:
        if not draft or "Insufficient reference context" in draft:
            return []
            
        system_instruction = (
            "You are a strict Legal Compliance Auditor.\n"
            "Scan the provided legal draft against critical vulnerabilities (e.g., uncapped liability, missing governing law, vague termination triggers, anti-competitive restrictions).\n"
            "You must output ONLY a valid JSON array of objects. Each object must have exactly three string keys: 'risk_level' (High, Medium, Low), 'issue', and 'fix'.\n"
            "If no risks are found, output an empty array: []\n\n"
            "DO NOT include any conversational text, formatting, or markdown backticks in your output. Just the raw JSON array starting with '[' and ending with ']'.\n\n"
            f"DRAFT TO AUDIT:\n{draft}"
        )
        
        try:
            response = self.auditor_model.generate_content(system_instruction)
            content = response.text.strip()
            
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
                
            risks = json.loads(content.strip())
            
            validated_risks = []
            if isinstance(risks, list):
                for r in risks:
                    if "risk_level" in r and "issue" in r and "fix" in r:
                        validated_risks.append({
                            "risk_level": str(r["risk_level"]),
                            "issue": str(r["issue"]),
                            "fix": str(r["fix"])
                        })
            return validated_risks
            
        except Exception as e:
            print(f"Compliance audit parsing engine failed: {str(e)}")
            return []
