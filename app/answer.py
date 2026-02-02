"""
Answer generation with citations using LLM
"""
from typing import List, Optional
from pydantic import BaseModel, Field
import os
import json


class Citation(BaseModel):
    """Single citation from a document chunk"""
    document_id: str = Field(..., description="UUID of the source document")
    document_title: str = Field(..., description="Title of the source document")
    page_number: int = Field(..., description="Page number in the document")
    chunk_id: int = Field(..., description="ID of the specific chunk")
    quote: str = Field(..., description="1-2 sentence quote from the chunk")


class AnswerWithCitations(BaseModel):
    """Structured answer with citations"""
    answer: str = Field(..., description="The answer text based on the context")
    citations: List[Citation] = Field(default_factory=list, description="List of citations supporting the answer")
    has_sufficient_context: bool = Field(..., description="Whether sufficient context was available to answer")


SYSTEM_PROMPT = """Jesteś asystentem odpowiadającym WYŁĄCZNIE na podstawie dostarczonego kontekstu.

ZASADY:
1. Odpowiadaj TYLKO na podstawie dostarczonego kontekstu
2. Jeśli kontekst nie zawiera informacji potrzebnych do odpowiedzi, powiedz: "Brak informacji w dokumentach"
3. Dla każdego faktu w odpowiedzi, podaj cytowanie (chunk_id i krótki cytat 1-2 zdania)
4. NIE dodawaj informacji spoza kontekstu
5. Jeśli nie jesteś pewien, powiedz to jasno

FORMAT ODPOWIEDZI:
Zwróć strukturalny JSON z polami:
- answer: twoja odpowiedź (lub "Brak informacji w dokumentach")
- citations: lista cytowań [{document_id, document_title, page_number, chunk_id, quote}]
- has_sufficient_context: true/false

KONTEKST:
{context}

PYTANIE:
{question}
"""


def build_context_string(chunks: List[dict]) -> str:
    """Build context string from retrieved chunks"""
    context_parts = []
    for i, chunk in enumerate(chunks):
        context_parts.append(
            f"[Chunk {chunk['chunk_id']}] (Document: {chunk['document']}, Page: {chunk['page_number']})\n"
            f"{chunk['text']}\n"
        )
    return "\n---\n".join(context_parts)


def generate_answer_openai(question: str, chunks: List[dict], api_key: str) -> AnswerWithCitations:
    """Generate answer with citations using OpenAI"""
    from openai import OpenAI
    
    client = OpenAI(api_key=api_key)
    context = build_context_string(chunks)
    
    prompt = SYSTEM_PROMPT.format(context=context, question=question)
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # or gpt-4-turbo
        messages=[
            {"role": "system", "content": "Jesteś pomocnym asystentem zwracającym strukturalne odpowiedzi w JSON."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"},
        temperature=0.1,
    )
    
    # Parse JSON response
    result = json.loads(response.choices[0].message.content)
    
    # Validate and convert to Pydantic model
    return AnswerWithCitations(
        answer=result.get("answer", ""),
        citations=[Citation(**c) for c in result.get("citations", [])],
        has_sufficient_context=result.get("has_sufficient_context", len(chunks) > 0)
    )


def generate_answer_local(question: str, chunks: List[dict]) -> AnswerWithCitations:
    """
    Fallback: Generate simple answer without LLM
    Returns context-based answer with all chunks as citations
    """
    if not chunks:
        return AnswerWithCitations(
            answer="Brak informacji w dokumentach.",
            citations=[],
            has_sufficient_context=False
        )
    
    # Simple fallback: return concatenated chunks with citations
    answer_parts = []
    citations = []
    
    for chunk in chunks[:3]:  # Top 3 chunks
        answer_parts.append(f"[Dokument: {chunk['document']}, str. {chunk['page_number']}]: {chunk['text'][:200]}...")
        
        citations.append(Citation(
            document_id=chunk.get('document_id', 'unknown'),
            document_title=chunk['document'],
            page_number=chunk['page_number'],
            chunk_id=chunk['chunk_id'],
            quote=chunk['text'][:200] + "..."
        ))
    
    answer = "\n\n".join(answer_parts)
    
    return AnswerWithCitations(
        answer=answer,
        citations=citations,
        has_sufficient_context=True
    )


def generate_answer(question: str, chunks: List[dict], use_openai: bool = True) -> AnswerWithCitations:
    """
    Main function to generate answer with citations
    
    Args:
        question: User's question
        chunks: Retrieved chunks from vector search
        use_openai: Whether to use OpenAI (requires OPENAI_API_KEY)
    
    Returns:
        AnswerWithCitations with structured answer and citations
    """
    if not chunks:
        return AnswerWithCitations(
            answer="Brak informacji w dokumentach.",
            citations=[],
            has_sufficient_context=False
        )
    
    if use_openai:
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            try:
                return generate_answer_openai(question, chunks, api_key)
            except Exception as e:
                print(f"OpenAI generation failed: {e}, falling back to local")
                return generate_answer_local(question, chunks)
    
    return generate_answer_local(question, chunks)
