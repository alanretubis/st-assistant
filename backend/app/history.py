from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
from supabase import create_client  # supabase-py

app = FastAPI()
router = APIRouter()

app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
  raise RuntimeError("Supabase URL/Key not set in environment")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


@router.get("/history")
async def history():
  """
  Returns last 50 chats from Supabase (most recent first).
  Expected table 'chats' with at least: id, title, messages (JSON array), created_at.
  """
  try:
    res = supabase.table("chat_history").select("*").order("created_at", desc=True).limit(50).execute()
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))

  # supabase-py returns a dict with 'data' and 'error'
  if isinstance(res, dict):
    if res.get("error"):
      raise HTTPException(status_code=500, detail=str(res["error"]))
    data = res.get("data", [])
  else:
    # fallback for other clients
    data = getattr(res, "data", []) or []

  # Normalize messages field to expected frontend format:
  normalized = []
  for row in data:
    messages = row.get("messages") or []
    # ensure each message has {role, text}
    msgs = []
    for m in messages:
      if isinstance(m, dict) and ("role" in m and "text" in m):
        msgs.append({"role": m["role"], "text": m["text"]})
      else:
        # fallback: treat as assistant text
        msgs.append({"role": "Assistant", "text": str(m)})
    normalized.append({
      "id": row.get("id"),
      "title": row.get('question'),
      "messages": msgs,
      "created_at": row.get("created_at"),
    })

  return {"chats": normalized}