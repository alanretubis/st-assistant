import httpx
from bs4 import BeautifulSoup
from openai import OpenAI
from app.db import index
import hashlib
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

URLS = {
    "Alaska": "https://www.shermanstravel.com/cruise-destinations/alaska-itineraries",
    "Caribbean": "https://www.shermanstravel.com/cruise-destinations/caribbean-and-bahamas",
    "Hawaiian": "https://www.shermanstravel.com/cruise-destinations/hawaiian-islands",
    "Northern Europe": "https://www.shermanstravel.com/cruise-destinations/northern-europe"
}

def clean_text(html):
    soup = BeautifulSoup(html, "html.parser")
    for s in soup(["script", "style"]):
        s.extract()
    return soup.get_text(separator=" ", strip=True)

def chunk_text(text, chunk_size=500):
    words = text.split()
    for i in range(0, len(words), chunk_size):
        yield " ".join(words[i:i+chunk_size])

def scrape_and_upsert():
    for label, url in URLS.items():
        r = httpx.get(url, timeout=10)
        text = clean_text(r.text)
        for chunk in chunk_text(text):
            # create vector embedding (✅ fixed)
            embedding_response = client.embeddings.create(
                model="text-embedding-3-small",
                input=chunk
            )
            embedding = embedding_response.data[0].embedding

            # unique ID based on URL+chunk hash
            uid = hashlib.md5((url + chunk).encode()).hexdigest()

            # upsert into Pinecone
            index.upsert([
                (uid, embedding, {"url": url, "text": chunk})
            ])

    return {"status": "done"}
