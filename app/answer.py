"""
Answer generation with citations using LLM
"""
from typing import List, Optional
from pydantic import BaseModel, Field
import os
import json


class Citation(BaseModel):
    """Single citation from a document chunk"""
    document_id: str = Field(default="", description="UUID of the source document")
    document_title: str = Field(default="", description="Title of the source document")
    page_number: int = Field(default=1, description="Page number in the document")
    chunk_id: int = Field(default=0, description="ID of the specific chunk")
    quote: str = Field(default="", description="1-2 sentence quote from the chunk")


class AnswerWithCitations(BaseModel):
    """Structured answer with citations"""
    answer: str = Field(..., description="The answer text based on the context")
    citations: List[Citation] = Field(default_factory=list, description="List of citations supporting the answer")
    has_sufficient_context: bool = Field(..., description="Whether sufficient context was available to answer")


SYSTEM_PROMPT = """You are an assistant that answers ONLY based on the provided context.

RULES:
1. Answer ONLY based on the provided context
2. If the context does not contain the information needed to answer, say: "No information in documents"
3. For each fact in your answer, provide a citation (chunk_id and a short 1-2 sentence quote)
4. DO NOT add information from outside the context
5. If you are not certain, state it clearly

RESPONSE FORMAT:
Return structured JSON with fields:
- answer: your answer (or "No information in documents")
- citations: list of citations [{{document_id, document_title, page_number, chunk_id, quote}}]
- has_sufficient_context: true/false

CONTEXT:
{context}

QUESTION:
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
    
    print(f"🔧 Calling OpenAI API...")
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # or gpt-4-turbo
        messages=[
            {"role": "system", "content": "Jesteś pomocnym asystentem zwracającym strukturalne odpowiedzi w JSON."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"},
        temperature=0.1,
    )
    print(f"✅ OpenAI API call successful")
    
    # Parse JSON response
    raw_content = response.choices[0].message.content
    print(f"📥 Raw content length: {len(raw_content)} chars")
    print(f"📥 Raw content preview: {raw_content[:300]}...")
    
    result = json.loads(raw_content)
    print(f"📝 OpenAI parsed JSON keys: {list(result.keys())}")
    print(f"📝 OpenAI raw response:")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # Validate and convert to Pydantic model
    citations = []
    citations_raw = result.get("citations", [])
    print(f"📋 Citations count: {len(citations_raw)}")
    
    for i, c in enumerate(citations_raw):
        print(f"   Citation {i+1}: {c}")
        try:
            # Try to create Citation with flexible field mapping
            citation = Citation(
                document_id=str(c.get("document_id", c.get("doc_id", "unknown"))),
                document_title=str(c.get("document_title", c.get("document", c.get("title", "unknown")))),
                page_number=int(c.get("page_number", c.get("page", 1))),
                chunk_id=int(c.get("chunk_id", c.get("id", 0))),
                quote=str(c.get("quote", c.get("text", "")))
            )
            citations.append(citation)
            print(f"   ✅ Citation {i+1} parsed successfully")
        except Exception as e:
            print(f"   ⚠️  Failed to parse citation {i+1}: {e}")
            print(f"   Available keys: {list(c.keys())}")
    
    return AnswerWithCitations(
        answer=result.get("answer", ""),
        citations=citations,
        has_sufficient_context=result.get("has_sufficient_context", len(chunks) > 0)
    )


def generate_answer_local(question: str, chunks: List[dict]) -> AnswerWithCitations:
    """
    Fallback: Generate simple answer without LLM
    Returns context-based answer with all chunks as citations
    """
    if not chunks:
        return AnswerWithCitations(
            answer="No information in documents.",
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
    print(f"\n{'='*60}")
    print(f"🚀 generate_answer() called")
    print(f"   Question: {question[:50]}...")
    print(f"   Chunks: {len(chunks)}")
    print(f"   use_openai: {use_openai}")
    print(f"{'='*60}\n")
    
    if not chunks:
        return AnswerWithCitations(
            answer="No information in documents.",
            citations=[],
            has_sufficient_context=False
        )
    
    if use_openai:
        api_key = os.getenv("OPENAI_API_KEY")
        print(f"   API key present: {api_key is not None}")
        if api_key:
            print(f"🤖 Using OpenAI for answer generation (key length: {len(api_key)})")
            try:
                result = generate_answer_openai(question, chunks, api_key)
                print(f"✅ OpenAI generation successful!")
                return result
            except Exception as e:
                import traceback
                print(f"❌ OpenAI generation failed: {type(e).__name__}: {e}")
                print(f"   Full traceback:")
                traceback.print_exc()
                print(f"   Falling back to local generation")
                return generate_answer_local(question, chunks)
        else:
            print("⚠️  OPENAI_API_KEY not found, using local generation")
    
    print("📝 Using local generation (use_openai=False)")
    return generate_answer_local(question, chunks)
