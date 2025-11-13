import os
from supabase import create_client
from pinecone import Pinecone, ServerlessSpec

# Initialize Supabase
# SUPABASE_URL = os.getenv("SUPABASE_URL")
# SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_ROLE_KEY")  # must be service role key
)

# Initialize Pinecone (v3 syntax)
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENV")  # e.g. "us-west-2"

pc = Pinecone(api_key=PINECONE_API_KEY)

INDEX_NAME = "shermanstravel"

# Check if index exists
if INDEX_NAME not in pc.list_indexes().names():
    pc.create_index(
        name=INDEX_NAME,
        dimension=1536,  # depends on your embedding model
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",
            region=PINECONE_ENV
        )
    )

# Connect to the index
index = pc.Index(INDEX_NAME)