import os
import re
from typing import List, Dict, Any, Tuple
import chromadb
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer
from app.core.config import settings
from app.core.ingestion import DocumentChunk

class HybridSearchEngine:
    def __init__(self):
        try:
            # 1. Initialize Dense Engine (ChromaDB)
            os.makedirs(settings.chroma_db_dir, exist_ok=True)
            self.chroma_client = chromadb.PersistentClient(path=settings.chroma_db_dir)
            self.collection_name = "legal_contracts"
            
            self.collection = self.chroma_client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            
            # Initialize specified embedding model
            self.embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
            
            # 2. Initialize Sparse Engine state (BM25)
            self.corpus_chunks: List[DocumentChunk] = []
            self.bm25_index: BM25Okapi = None
            self.tokenized_corpus: List[List[str]] = []
            
            self._sync_bm25_from_chroma()
        except Exception as e:
            print(f"Critical failure initializing Hybrid Search Engine: {str(e)}")

    def _tokenize(self, text: str) -> List[str]:
        """Simple and safe tokenizer for the sparse engine."""
        try:
            return [word for word in re.split(r'\W+', text.lower()) if word]
        except Exception:
            return []

    def _sync_bm25_from_chroma(self):
        """Reconstructs the BM25 index from persistent ChromaDB storage safely."""
        try:
            results = self.collection.get(include=["documents", "metadatas"])
            if not results or not results["documents"]:
                return
                
            docs = results["documents"]
            metas = results["metadatas"]
            
            for i, doc_text in enumerate(docs):
                meta = metas[i]
                chunk = DocumentChunk(
                    chunk_index=meta.get("chunk_index", 0),
                    text=doc_text,
                    document_id=meta.get("document_id", "unknown"),
                    document_title=meta.get("document_title", "unknown"),
                    upload_date=meta.get("upload_date", "unknown"),
                    metadata=meta
                )
                self.corpus_chunks.append(chunk)
                self.tokenized_corpus.append(self._tokenize(doc_text))
                
            if self.tokenized_corpus:
                self.bm25_index = BM25Okapi(self.tokenized_corpus)
        except Exception as e:
            print(f"Error syncing BM25 index from ChromaDB: {str(e)}")

    def add_documents(self, chunks: List[DocumentChunk]):
        """Injects documents into both Dense and Sparse engines safely."""
        if not chunks:
            return
            
        try:
            ids = [f"{c.document_id}_chunk_{c.chunk_index}" for c in chunks]
            texts = [c.text for c in chunks]
            metadatas = [c.metadata for c in chunks]
            
            embeddings = self.embedding_model.encode(texts).tolist()
            
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas
            )
            
            for chunk in chunks:
                self.corpus_chunks.append(chunk)
                self.tokenized_corpus.append(self._tokenize(chunk.text))
                
            self.bm25_index = BM25Okapi(self.tokenized_corpus)
        except Exception as e:
            print(f"Error adding documents to search indexes: {str(e)}")

    def dense_search(self, query: str, top_k: int = 5) -> List[Tuple[DocumentChunk, float]]:
        """Executes safe Dense Vector search via ChromaDB."""
        try:
            query_embedding = self.embedding_model.encode([query]).tolist()[0]
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                include=["documents", "metadatas", "distances"]
            )
            
            if not results["documents"] or not results["documents"][0]:
                return []
                
            dense_results = []
            docs = results["documents"][0]
            metas = results["metadatas"][0]
            distances = results["distances"][0]
            
            for doc_text, meta, distance in zip(docs, metas, distances):
                chunk = DocumentChunk(
                    chunk_index=meta.get("chunk_index", 0),
                    text=doc_text,
                    document_id=meta.get("document_id", "unknown"),
                    document_title=meta.get("document_title", "unknown"),
                    upload_date=meta.get("upload_date", "unknown"),
                    metadata=meta
                )
                dense_results.append((chunk, distance))
                
            return dense_results
        except Exception as e:
            print(f"Dense search failed: {str(e)}")
            return []

    def sparse_search(self, query: str, top_k: int = 5) -> List[Tuple[DocumentChunk, float]]:
        """Executes safe Sparse Keyword search via BM25."""
        try:
            if not self.bm25_index:
                return []
                
            tokenized_query = self._tokenize(query)
            scores = self.bm25_index.get_scores(tokenized_query)
            
            top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
            
            sparse_results = []
            for idx in top_indices:
                if scores[idx] > 0:
                    sparse_results.append((self.corpus_chunks[idx], scores[idx]))
                    
            return sparse_results
        except Exception as e:
            print(f"Sparse search failed: {str(e)}")
            return []

    def hybrid_search(self, query: str, top_k: int = 5) -> List[DocumentChunk]:
        """
        Unified search function integrating Reciprocal Rank Fusion (RRF) securely.
        """
        try:
            fetch_k = max(top_k * 2, 10)
            
            dense_results = self.dense_search(query, top_k=fetch_k)
            sparse_results = self.sparse_search(query, top_k=fetch_k)
            
            rrf_k = 60
            
            scores: Dict[str, float] = {}
            chunk_map: Dict[str, DocumentChunk] = {}
            
            # Process Dense Ranks
            for rank, (chunk, _) in enumerate(dense_results):
                chunk_id = f"{chunk.document_id}_{chunk.chunk_index}"
                chunk_map[chunk_id] = chunk
                scores[chunk_id] = scores.get(chunk_id, 0.0) + 1.0 / (rrf_k + rank + 1)
                
            # Process Sparse Ranks
            for rank, (chunk, _) in enumerate(sparse_results):
                chunk_id = f"{chunk.document_id}_{chunk.chunk_index}"
                chunk_map[chunk_id] = chunk
                scores[chunk_id] = scores.get(chunk_id, 0.0) + 1.0 / (rrf_k + rank + 1)
                
            # Sort mathematically
            sorted_results = sorted(scores.items(), key=lambda item: item[1], reverse=True)
            
            final_chunks = [chunk_map[chunk_id] for chunk_id, _ in sorted_results[:top_k]]
            return final_chunks
        except Exception as e:
            print(f"Hybrid search (RRF) failed: {str(e)}")
            return []
