import uuid
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from typing import Dict, Any

from app.api.dependencies import get_document_parser, get_search_engine, get_generator_pipeline
from app.core.ingestion import DocumentParser
from app.core.hybrid_search import HybridSearchEngine
from app.core.generator import GeneratorPipeline
from app.schemas.payloads import ChatRequest, ChatResponse, AuditRequest, AuditResponse

router = APIRouter()

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    parser: DocumentParser = Depends(get_document_parser),
    search_engine: HybridSearchEngine = Depends(get_search_engine)
) -> Dict[str, Any]:
    """
    Accepts files, processes via ingestion.py, updates hybrid search index dynamically.
    """
    if not file.filename.lower().endswith(('.pdf', '.docx')):
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported.")
        
    try:
        content = await file.read()
        document_id = str(uuid.uuid4())
        
        chunks = parser.process_document(
            file_content=content,
            filename=file.filename,
            document_id=document_id
        )
        
        search_engine.add_documents(chunks)
        
        return {
            "status": "success",
            "document_id": document_id,
            "filename": file.filename,
            "chunks_processed": len(chunks),
            "message": "Document ingested and indexed dynamically."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat", response_model=ChatResponse)
async def chat_generate(
    request: ChatRequest,
    search_engine: HybridSearchEngine = Depends(get_search_engine),
    generator: GeneratorPipeline = Depends(get_generator_pipeline)
):
    """
    Accepts prompts, fetches documents via hybrid search, drafts clause, keeps conversation states.
    """
    try:
        context_chunks = search_engine.hybrid_search(query=request.prompt, top_k=5)
        
        response = generator.generate_draft(
            session_id=request.session_id,
            prompt=request.prompt,
            context_chunks=context_chunks
        )
        
        return ChatResponse(
            draft=response.draft,
            sources=response.sources
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/audit", response_model=AuditResponse)
async def audit_draft(
    request: AuditRequest,
    generator: GeneratorPipeline = Depends(get_generator_pipeline)
):
    """
    Passes text to the Compliance Auditor agent and outputs the JSON evaluation arrays.
    """
    try:
        risks = generator.run_compliance_audit(draft=request.draft)
        return AuditResponse(risks=risks)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
