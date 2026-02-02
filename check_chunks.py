from sqlalchemy import create_engine, text

engine = create_engine('postgresql+psycopg2://rag_user:rag_pass@localhost:5432/rag_db')
with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT text, chunk_index FROM chunks 
        WHERE document_id = (
            SELECT id FROM documents 
            WHERE title='Invoice_FV_2025_0847.txt' 
            LIMIT 1
        )
        ORDER BY chunk_index
    """))
    for row in result:
        print(f'\n=== CHUNK {row.chunk_index} ===')
        content = row.text
        # Search for amounts
        if 'PLN' in content or 'brutto' in content.lower() or '74' in content:
            print("📌 CONTAINS AMOUNT INFO!")
            print(content[:800])
        else:
            print(f"Length: {len(content)} chars, preview: {content[:150]}")
