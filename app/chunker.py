
def chunk_text(text, chunk_size=1000, overlap=150):
    """
    Chunk text by characters with overlap.
    """
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

def chunk_text_tokens(text, chunk_size=300, overlap=40, tokenizer=None):
    """
    Chunk text by tokens with overlap. Requires a tokenizer (e.g. tiktoken).
    """
    if tokenizer is None:
        raise ValueError("Tokenizer required for token-based chunking.")
    tokens = tokenizer.encode(text)
    chunks = []
    start = 0
    while start < len(tokens):
        end = min(start + chunk_size, len(tokens))
        chunk_tokens = tokens[start:end]
        chunk_text = tokenizer.decode(chunk_tokens)
        chunks.append(chunk_text)
        start += chunk_size - overlap
    return chunks

def chunk_pages(pages, chunk_size=1000, overlap=150, by_tokens=False, tokenizer=None):
    """
    Chunk each page by characters or tokens.
    """
    all_chunks = []
    for page_num, page_text in enumerate(pages):
        if by_tokens:
            page_chunks = chunk_text_tokens(page_text, chunk_size, overlap, tokenizer)
        else:
            page_chunks = chunk_text(page_text, chunk_size, overlap)
        for idx, chunk in enumerate(page_chunks):
            all_chunks.append({
                "page_number": page_num + 1,
                "chunk_index": idx,
                "text": chunk
            })
    return all_chunks
