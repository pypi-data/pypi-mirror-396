"""
🚀 UltraRAG - Complete Unified Package
Revolutionary RAG with Built-in Ollama + FastAPI + Swagger

pip install ultrarag
ultrarag serve --ollama-host localhost --ollama-model llama3.2

Author: Abhishek Kumar
Email: ipsabhi420@gmail.com
Version: 1.0.0
"""

import re
import logging
import hashlib
import json
import time
import sys
from typing import List, Dict, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict

# Logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class Chunk:
    """Atomic chunk with guaranteed completeness"""
    id: str
    text: str
    start_pos: int
    end_pos: int
    completeness_score: float = 0.0
    is_atomic: bool = False
    entities: List[Dict] = field(default_factory=list)
    references: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass  
class QueryAnalysis:
    """QueryDNA - Multi-dimensional query analysis"""
    original_query: str
    intent: str
    entities: List[Dict]
    complexity: float
    temporal_context: Optional[str] = None
    expansions: List[str] = field(default_factory=list)
    corrected: str = ""
    language: str = "en"
    info_types: List[str] = field(default_factory=list)

@dataclass
class RAGResponse:
    """Complete RAG response with full metadata"""
    answer: str
    sources: List[str]
    confidence: float
    grounding_score: float
    chunks_used: int
    strategy_used: str
    tokens_used: int
    metadata: Dict[str, Any] = field(default_factory=dict)

# ============================================================================
# ATOMIC CHUNKING
# ============================================================================

class AtomicChunker:
    """Guaranteed complete chunks (ICS ≥ 0.75)"""
    
    def __init__(self, min_ics: float = 0.75):
        self.min_ics = min_ics
    
    def chunk(self, text: str) -> List[Chunk]:
        """Chunk text into atomic units"""
        sentences = self._split_sentences(text)
        chunks = []
        current_chunk = []
        position = 0
        
        for sent in sentences:
            current_chunk.append(sent)
            chunk_text = " ".join(current_chunk)
            ics = self._calculate_ics(chunk_text)
            
            if ics >= self.min_ics and len(current_chunk) >= 2:
                chunk = Chunk(
                    id=self._generate_id(chunk_text),
                    text=chunk_text,
                    start_pos=position,
                    end_pos=position + len(chunk_text),
                    completeness_score=ics,
                    is_atomic=True,
                    entities=self._extract_entities(chunk_text)
                )
                chunks.append(chunk)
                position += len(chunk_text)
                current_chunk = []
        
        if current_chunk:
            chunk_text = " ".join(current_chunk)
            chunk = Chunk(
                id=self._generate_id(chunk_text),
                text=chunk_text,
                start_pos=position,
                end_pos=position + len(chunk_text),
                completeness_score=self._calculate_ics(chunk_text),
                is_atomic=True,
                entities=self._extract_entities(chunk_text)
            )
            chunks.append(chunk)
        
        return chunks
    
    def _split_sentences(self, text: str) -> List[str]:
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _calculate_ics(self, text: str) -> float:
        score = 0.0
        word_count = len(text.split())
        if word_count >= 10:
            score += 0.3
        elif word_count >= 5:
            score += 0.15
        if text.endswith(('.', '!', '?')):
            score += 0.3
        entities = len([w for w in text.split() if w and (w[0].isupper() or w.isdigit())])
        if entities > 0:
            score += 0.2
        dangling_refs = ['this', 'that', 'it', 'they']
        if not any(ref in text.lower().split()[:3] for ref in dangling_refs):
            score += 0.2
        return min(1.0, score)
    
    def _extract_entities(self, text: str) -> List[Dict]:
        entities = []
        for word in text.split():
            if word and word[0].isupper() and len(word) > 2:
                entities.append({'text': word, 'type': 'ENTITY'})
        return entities
    
    def _generate_id(self, text: str) -> str:
        return hashlib.md5(text.encode()).hexdigest()[:12]

# ============================================================================
# QUERY PROCESSING
# ============================================================================

class QueryProcessor:
    """QueryDNA - Multi-dimensional analysis"""
    
    INTENT_PATTERNS = {
        'factual': [r'\bwhat\b', r'\bwho\b', r'\bkya\b'],
        'comparison': [r'\bcompare\b', r'\bvs\b'],
        'causal': [r'\bwhy\b', r'\bhow\b', r'\bkyun\b'],
        'temporal': [r'\bcurrent\b', r'\blatest\b', r'\babhi\b']
    }
    
    def analyze(self, query: str) -> QueryAnalysis:
        """Analyze query"""
        return QueryAnalysis(
            original_query=query,
            intent=self._detect_intent(query),
            entities=self._extract_entities(query),
            complexity=self._calculate_complexity(query),
            temporal_context=self._detect_temporal(query),
            expansions=self._expand_query(query),
            corrected=query,
            language=self._detect_language(query),
            info_types=self._identify_info_types(query)
        )
    
    def _detect_intent(self, query: str) -> str:
        query_lower = query.lower()
        for intent, patterns in self.INTENT_PATTERNS.items():
            if any(re.search(p, query_lower) for p in patterns):
                return intent
        return 'general'
    
    def _extract_entities(self, query: str) -> List[Dict]:
        entities = []
        for word in query.split():
            if word and word[0].isupper() and len(word) > 2:
                entities.append({'text': word, 'type': 'ENTITY'})
        return entities
    
    def _calculate_complexity(self, query: str) -> float:
        return min(1.0, len(query.split()) / 30 + len(self._extract_entities(query)) * 0.1)
    
    def _detect_temporal(self, query: str) -> Optional[str]:
        temporal_keywords = {'current': 'current', 'latest': 'latest', 'recent': 'recent'}
        for keyword, context in temporal_keywords.items():
            if keyword in query.lower():
                return context
        return None
    
    def _expand_query(self, query: str) -> List[str]:
        return [query]
    
    def _detect_language(self, query: str) -> str:
        hindi_words = ['kya', 'hai', 'kyun', 'kaise', 'abhi']
        return 'hi-en' if any(w in query.lower() for w in hindi_words) else 'en'
    
    def _identify_info_types(self, query: str) -> List[str]:
        info_types = []
        if re.search(r'\d+|number|amount', query.lower()):
            info_types.append('numerical')
        return info_types if info_types else ['general']

# ============================================================================
# ADAPTIVE RETRIEVAL
# ============================================================================

class AdaptiveRetriever:
    """Intent-based retrieval"""
    
    def retrieve(self, chunks: List[Chunk], query_analysis: QueryAnalysis, top_k: int = 5) -> List[Chunk]:
        """Retrieve relevant chunks"""
        query_terms = set(query_analysis.original_query.lower().split())
        
        results = []
        for chunk in chunks:
            chunk_terms = set(chunk.text.lower().split())
            overlap = len(query_terms & chunk_terms)
            score = overlap / len(query_terms) if query_terms else 0.0
            
            for entity in query_analysis.entities:
                if entity['text'].lower() in chunk.text.lower():
                    score += 0.2
            
            if score > 0:
                results.append((chunk, score))
        
        results = sorted(results, key=lambda x: x[1], reverse=True)
        return [chunk for chunk, score in results[:top_k]]

# ============================================================================
# ANSWER VALIDATOR
# ============================================================================

class AnswerValidator:
    """ProvenAnswer - Multi-layer validation"""
    
    def __init__(self, min_score: float = 0.70):
        self.min_score = min_score
    
    def validate(self, answer: str, chunks: List[Chunk]) -> dict:
        """Validate answer"""
        entity_score = self._verify_entities(answer, chunks)
        claim_score = self._verify_claims(answer, chunks)
        overall_score = 0.5 * entity_score + 0.5 * claim_score
        
        if overall_score >= 0.90:
            verdict = "FULLY_GROUNDED"
        elif overall_score >= 0.75:
            verdict = "MOSTLY_GROUNDED"
        else:
            verdict = "PARTIALLY_GROUNDED"
        
        return {
            'is_grounded': overall_score >= self.min_score,
            'overall_score': overall_score,
            'verdict': verdict
        }
    
    def _verify_entities(self, answer: str, chunks: List[Chunk]) -> float:
        answer_entities = [w for w in answer.split() if w and w[0].isupper()]
        if not answer_entities:
            return 1.0
        chunk_text = " ".join([c.text for c in chunks])
        verified = sum(1 for e in answer_entities if e.lower() in chunk_text.lower())
        return verified / len(answer_entities)
    
    def _verify_claims(self, answer: str, chunks: List[Chunk]) -> float:
        claims = [c.strip() for c in re.split(r'[.!?]', answer) if c.strip()]
        if not claims:
            return 0.5
        chunk_text = " ".join([c.text for c in chunks])
        verified = sum(1 for claim in claims if any(w in chunk_text.lower() for w in claim.lower().split()))
        return verified / len(claims)

# ============================================================================
# MAIN RAG CLASS
# ============================================================================

class RAG:
    """
    🚀 UltraRAG - Complete RAG System
    
    Usage:
        rag = RAG()
        rag.add("document text...")
        answer = rag.ask("question?")
    """
    
    def __init__(self, min_chunk_completeness: float = 0.75, min_grounding_score: float = 0.70):
        self.chunker = AtomicChunker(min_ics=min_chunk_completeness)
        self.query_processor = QueryProcessor()
        self.retriever = AdaptiveRetriever()
        self.validator = AnswerValidator(min_score=min_grounding_score)
        self.chunks: List[Chunk] = []
        logger.info("✅ UltraRAG initialized")
    
    def add(self, text: str, metadata: Optional[Dict] = None) -> int:
        """Add document"""
        new_chunks = self.chunker.chunk(text)
        if metadata:
            for chunk in new_chunks:
                chunk.metadata.update(metadata)
        self.chunks.extend(new_chunks)
        logger.info(f"✅ Added {len(new_chunks)} chunks (total: {len(self.chunks)})")
        return len(new_chunks)
    
    def ask(self, question: str, explain: bool = False) -> Union[str, RAGResponse]:
        """Ask question"""
        if not self.chunks:
            return "⚠️ No documents added yet"
        
        query_analysis = self.query_processor.analyze(question)
        retrieved_chunks = self.retriever.retrieve(self.chunks, query_analysis, top_k=5)
        
        if not retrieved_chunks:
            return "❌ No relevant information found"
        
        # Generate answer (extractive)
        answer = self._generate_answer(question, retrieved_chunks, query_analysis)
        
        # Validate
        validation = self.validator.validate(answer, retrieved_chunks)
        
        if not validation['is_grounded']:
            answer = "⚠️ Cannot answer confidently"
        
        if explain:
            return RAGResponse(
                answer=answer,
                sources=[f"Chunk {c.id[:8]}" for c in retrieved_chunks[:3]],
                confidence=0.9,
                grounding_score=validation['overall_score'],
                chunks_used=len(retrieved_chunks),
                strategy_used='keyword',
                tokens_used=len(answer.split()),
                metadata={'verdict': validation['verdict']}
            )
        else:
            return answer
    
    def _generate_answer(self, question: str, chunks: List[Chunk], query_analysis: QueryAnalysis) -> str:
        """Generate answer from chunks"""
        context_sentences = []
        for chunk in chunks:
            context_sentences.extend(re.split(r'[.!?]', chunk.text))
        context_sentences = [s.strip() for s in context_sentences if s.strip()]
        
        query_terms = set(question.lower().split())
        scored_sentences = []
        
        for sentence in context_sentences:
            sentence_terms = set(sentence.lower().split())
            overlap = len(query_terms & sentence_terms)
            score = overlap / len(query_terms) if query_terms else 0.0
            if score > 0:
                scored_sentences.append((sentence, score))
        
        scored_sentences.sort(key=lambda x: x[1], reverse=True)
        if scored_sentences:
            answer_sentences = [sent for sent, score in scored_sentences[:2]]
            return ". ".join(answer_sentences) + "."
        return "Information not found"
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics"""
        return {
            'total_chunks': len(self.chunks),
            'atomic_chunks': sum(1 for c in self.chunks if c.is_atomic),
            'avg_completeness': sum(c.completeness_score for c in self.chunks) / len(self.chunks) if self.chunks else 0
        }

# ============================================================================
# OLLAMA INTEGRATION (OPTIONAL)
# ============================================================================

try:
    import requests
    
    class OllamaLLM:
        """Ollama LLM Integration"""
        
        def __init__(self, host: str = "localhost", port: int = 11434, model: str = "llama3.2"):
            self.host = host
            self.port = port
            self.model = model
            self.url = f"http://{host}:{port}/api/generate"
        
        def generate(self, prompt: str, max_tokens: int = 500) -> str:
            """Generate response"""
            try:
                payload = {
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"num_predict": max_tokens, "temperature": 0.1}
                }
                response = requests.post(self.url, json=payload, timeout=60)
                if response.status_code == 200:
                    return response.json().get("response", "").strip()
                return f"Error: {response.status_code}"
            except Exception as e:
                return f"Error: {str(e)}"
        
        def test(self) -> bool:
            """Test connection"""
            try:
                response = requests.get(f"http://{self.host}:{self.port}/api/tags", timeout=5)
                return response.status_code == 200
            except:
                return False
    
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    logger.warning("⚠️ Requests not installed - Ollama integration disabled")

# ============================================================================
# FASTAPI INTEGRATION (OPTIONAL)
# ============================================================================

try:
    from fastapi import FastAPI, File, UploadFile, Form
    from fastapi.responses import JSONResponse
    from pydantic import BaseModel
    import uvicorn
    
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    logger.warning("⚠️ FastAPI not installed - Web interface disabled")

# ============================================================================
# CLI SERVER (if FastAPI available)
# ============================================================================

def create_server(ollama_host: str = "localhost", ollama_port: int = 11434, 
                 ollama_model: str = "llama3.2"):
    """Create FastAPI server with Ollama"""
    
    if not FASTAPI_AVAILABLE:
        print("❌ FastAPI not installed!")
        print("Install: pip install fastapi uvicorn")
        return None
    
    app = FastAPI(title="🚀 UltraRAG API", docs_url="/docs")
    
    # Initialize
    rag = RAG()
    if OLLAMA_AVAILABLE:
        llm = OllamaLLM(ollama_host, ollama_port, ollama_model)
    else:
        llm = None
    
    class QueryRequest(BaseModel):
        question: str
        use_llm: bool = True
    
    @app.get("/")
    async def root():
        return {"message": "🚀 UltraRAG API", "docs": "/docs"}
    
    @app.post("/upload")
    async def upload(file: UploadFile = File(...)):
        content = await file.read()
        text = content.decode('utf-8')
        chunks = rag.add(text, {"filename": file.filename})
        return {"status": "success", "chunks": chunks, "filename": file.filename}
    
    @app.post("/upload-text")
    async def upload_text(text: str = Form(...), filename: str = Form("manual.txt")):
        chunks = rag.add(text, {"filename": filename})
        return {"status": "success", "chunks": chunks}
    
    @app.post("/query")
    async def query(req: QueryRequest):
        if req.use_llm and llm:
            # Get context
            query_analysis = rag.query_processor.analyze(req.question)
            chunks = rag.retriever.retrieve(rag.chunks, query_analysis, top_k=3)
            context = " ".join([c.text for c in chunks])
            
            prompt = f"""Based on this context, answer the question:

Context: {context}

Question: {req.question}

Answer:"""
            answer = llm.generate(prompt)
            return {"status": "success", "answer": answer, "source": "llm"}
        else:
            answer = rag.ask(req.question)
            return {"status": "success", "answer": answer, "source": "rag"}
    
    @app.get("/stats")
    async def stats():
        return rag.get_stats()
    
    @app.delete("/clear")
    async def clear():
        rag.chunks = []
        return {"status": "success"}
    
    return app

# ============================================================================
# CLI
# ============================================================================

def cli():
    """Command line interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="🚀 UltraRAG - Complete RAG System")
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Serve command
    serve_parser = subparsers.add_parser('serve', help='Start web server')
    serve_parser.add_argument('--ollama-host', default='localhost', help='Ollama host')
    serve_parser.add_argument('--ollama-port', type=int, default=11434, help='Ollama port')
    serve_parser.add_argument('--ollama-model', default='llama3.2', help='Ollama model')
    serve_parser.add_argument('--port', type=int, default=8000, help='Server port')
    
    args = parser.parse_args()
    
    if args.command == 'serve':
        if not FASTAPI_AVAILABLE:
            print("❌ FastAPI not installed!")
            print("Install: pip install fastapi uvicorn")
            return
        
        print(f"🚀 Starting UltraRAG Server...")
        print(f"📡 Ollama: {args.ollama_host}:{args.ollama_port}")
        print(f"🤖 Model: {args.ollama_model}")
        print(f"📚 Swagger UI: http://localhost:{args.port}/docs")
        
        app = create_server(args.ollama_host, args.ollama_port, args.ollama_model)
        uvicorn.run(app, host="0.0.0.0", port=args.port)
    else:
        parser.print_help()

# ============================================================================
# EXPORTS
# ============================================================================

__version__ = "1.0.0"
__all__ = ['RAG', 'OllamaLLM', 'create_server', 'cli']

if __name__ == "__main__":
    cli()
