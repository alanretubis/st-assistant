import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from openai import OpenAI
from app.db import index, supabase  # supabase should be created with service role key

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
router = APIRouter()

class Question(BaseModel):
    question: str

@router.post("/chat")
async def chat(q: Question):
    # 1️⃣ Create embedding
    try:
        embedding_response = client.embeddings.create(
            model="text-embedding-3-small",
            input=q.question
        )
        query_embedding = embedding_response.data[0].embedding
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI embedding error: {str(e)}")

    # 2️⃣ Query Pinecone
    try:
        results = index.query(
            vector=query_embedding,
            top_k=3,
            include_metadata=True
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pinecone query error: {str(e)}")

    # 3️⃣ Build context and URLs
    context = "\n\n".join([r["metadata"]["text"] for r in results["matches"]])
    urls = list({r["metadata"]["url"] for r in results["matches"]})  # unique URLs

    # 4️⃣ Generate answer
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Answer using only the context provided."},
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {q.question}"}
            ]
        )
        answer = resp.choices[0].message.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI chat completion error: {str(e)}")

    # 5️⃣ Store Q&A in Supabase (urls stored as JSON)
    try:
        supabase.table("chat_history").insert({
            "question": q.question,
            "answer": answer,
            "urls": urls  # make sure your column is type jsonb
        }).execute()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Supabase insert error: {str(e)}")

    # 6️⃣ Return response
    return {"answer": answer, "sources": urls}
