import httpx
from bs4 import BeautifulSoup
from openai import OpenAI
from app.db import index
import hashlib
import os
from pathlib import Path
import json

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

_config_path = Path(__file__).with_name("urls.json")

# Default data
default_urls = {
    "Alaska": "https://www.shermanstravel.com/cruise-destinations/alaska-itineraries",
    "Caribbean": "https://www.shermanstravel.com/cruise-destinations/caribbean-and-bahamas",
    "Hawaiian": "https://www.shermanstravel.com/cruise-destinations/hawaiian-islands",
    "Northern Europe": "https://www.shermanstravel.com/cruise-destinations/northern-europe"
}

# Load or create file
if _config_path.exists():
    with _config_path.open("r", encoding="utf-8") as _f:
        URLS = json.load(_f)
else:
    URLS = default_urls
    # Create the file
    with _config_path.open("w", encoding="utf-8") as _f:
        json.dump(default_urls, _f, indent=4, ensure_ascii=False)
    print(f"Created {_config_path.name} with default URLs.")

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

    return {"status": "Done Scraping"}
