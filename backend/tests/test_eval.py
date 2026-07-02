import os
import json
import asyncio
from typing import List, Dict, Any
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage

# Import the core logic to evaluate end-to-end
from app.core.ingestion import DocumentChunk
from app.core.config import settings

class RAGEvaluator:
    """
    Automated RAG Evaluation Suite utilizing the LLM-as-a-judge pattern.
    Measures the core RAG Triad: Faithfulness, Answer Relevance, and Context Recall.
    """
    def __init__(self):
        # We instantiate a dedicated judge instance with absolute determinism (temp=0.0)
        self.eval_llm = ChatGoogleGenerativeAI(
            model="gemini-pro",
            google_api_key=settings.gemini_api_key,
            temperature=0.0
        )

    def _parse_eval_response(self, response_text: str) -> Dict[str, Any]:
        """Safely parses JSON scoring payload from the LLM judge."""
        try:
            content = response_text.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            return json.loads(content.strip())
        except Exception as e:
            return {"score": 0.0, "reasoning": f"Failed to parse evaluation JSON: {str(e)}"}

    async def evaluate_faithfulness(self, query: str, context_chunks: List[DocumentChunk], generated_draft: str) -> Dict[str, Any]:
        """
        Metric 1: Faithfulness (Groundedness)
        Verifies that the generator strictly utilized the retrieved context and didn't hallucinate.
        """
        context_text = "\n\n".join([c.text for c in context_chunks])
        
        prompt = (
            "You are an impartial RAG Evaluation Judge.\n"
            "Evaluate whether the provided 'Generated Draft' contains ANY external facts, legal clauses, or terms not present in the 'Source Context'.\n"
            "Score from 0.0 to 1.0, where 1.0 means perfectly grounded (no hallucinations) and 0.0 means completely hallucinated.\n\n"
            f"--- Source Context ---\n{context_text}\n\n"
            f"--- Generated Draft ---\n{generated_draft}\n\n"
            "Output strictly valid JSON with exactly two keys: 'score' (float) and 'reasoning' (string)."
        )
        
        response = await self.eval_llm.ainvoke([SystemMessage(content=prompt)])
        return self._parse_eval_response(response.content)

    async def evaluate_answer_relevance(self, query: str, generated_draft: str) -> Dict[str, Any]:
        """
        Metric 2: Answer Relevance
        Verifies that the generated clause accurately executes the user's legal intent.
        """
        prompt = (
            "You are an impartial RAG Evaluation Judge.\n"
            "Evaluate whether the 'Generated Draft' completely and accurately answers the 'User Intent'.\n"
            "Score from 0.0 to 1.0, where 1.0 means perfectly answers the intent, and 0.0 means completely irrelevant or off-topic.\n\n"
            f"--- User Intent ---\n{query}\n\n"
            f"--- Generated Draft ---\n{generated_draft}\n\n"
            "Output strictly valid JSON with exactly two keys: 'score' (float) and 'reasoning' (string)."
        )
        
        response = await self.eval_llm.ainvoke([SystemMessage(content=prompt)])
        return self._parse_eval_response(response.content)

    async def evaluate_context_recall(self, query: str, context_chunks: List[DocumentChunk], ground_truth_keywords: List[str]) -> Dict[str, Any]:
        """
        Metric 3: Context Recall / Precision
        Verifies that the RRF hybrid search successfully captured the required legal precedents.
        """
        context_text = "\n\n".join([c.text for c in context_chunks])
        
        prompt = (
            "You are an impartial RAG Evaluation Judge.\n"
            "Evaluate if the provided 'Retrieved Context' contains sufficient information covering the 'Required Legal Concepts'.\n"
            "Score from 0.0 to 1.0, where 1.0 means all necessary legal precedents are present, and 0.0 means none are present.\n\n"
            f"--- User Query ---\n{query}\n\n"
            f"--- Required Legal Concepts ---\n{', '.join(ground_truth_keywords)}\n\n"
            f"--- Retrieved Context ---\n{context_text}\n\n"
            "Output strictly valid JSON with exactly two keys: 'score' (float) and 'reasoning' (string)."
        )
        
        response = await self.eval_llm.ainvoke([SystemMessage(content=prompt)])
        return self._parse_eval_response(response.content)

async def run_evaluation_suite():
    print("Initializing RAG Evaluation Suite...")
    evaluator = RAGEvaluator()
    
    # Static Data Injection for Integration Testing
    mock_query = "Draft a mutual non-compete clause limited to 2 years."
    mock_chunks = [
        DocumentChunk(
            chunk_index=0, 
            text="The parties agree not to engage in competitive business practices against each other for a period of two (2) years following termination.", 
            document_id="doc1", document_title="contract.pdf", upload_date="now", metadata={}
        )
    ]
    mock_draft = "During the term of this Agreement and for a period of two (2) years thereafter, neither party shall directly or indirectly engage in any business that competes with the other."
    mock_concepts = ["mutual non-compete", "2 years timeframe"]
    
    print("\n--- Running Automated RAG Triad Evaluator ---")
    
    # 1. Evaluate Faithfulness
    f_res = await evaluator.evaluate_faithfulness(mock_query, mock_chunks, mock_draft)
    print(f"\n[Metric 1] Faithfulness (Groundedness)\nScore: {f_res.get('score')}\nReasoning: {f_res.get('reasoning')}")
    
    # 2. Evaluate Answer Relevance
    r_res = await evaluator.evaluate_answer_relevance(mock_query, mock_draft)
    print(f"\n[Metric 2] Answer Relevance\nScore: {r_res.get('score')}\nReasoning: {r_res.get('reasoning')}")
    
    # 3. Evaluate Context Recall
    c_res = await evaluator.evaluate_context_recall(mock_query, mock_chunks, mock_concepts)
    print(f"\n[Metric 3] Context Recall (RRF Precision)\nScore: {c_res.get('score')}\nReasoning: {c_res.get('reasoning')}")

if __name__ == "__main__":
    asyncio.run(run_evaluation_suite())
