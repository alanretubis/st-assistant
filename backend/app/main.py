from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.scrape import scrape_and_upsert
from app.chat import router as chat_router
from app.history import router as history_router

app = FastAPI()
app.include_router(chat_router)
app.include_router(history_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/scrape")
async def scrape():
    return scrape_and_upsert()
