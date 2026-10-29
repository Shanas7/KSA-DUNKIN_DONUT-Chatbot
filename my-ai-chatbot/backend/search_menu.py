import os

import chromadb
from dotenv import load_dotenv
from google import genai
from google.genai import types


# ==========================================
# LOAD ENVIRONMENT
# ==========================================

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


# ==========================================
# CONNECT TO CHROMADB
# ==========================================

chroma_client = chromadb.PersistentClient(
    path="chroma_db"
)


collection = chroma_client.get_collection(
    name="dunkin_menu_ksa"
)


print("KSA menu collection loaded.")

print(
    f"Total products: {collection.count()}"
)


# ==========================================
# ASK USER
# ==========================================

question = input(
    "\nAsk about the Dunkin KSA menu: "
)


# ==========================================
# CREATE QUERY EMBEDDING
# ==========================================

print(
    "\nCreating query embedding..."
)


result = client.models.embed_content(
    model="gemini-embedding-001",
    contents=question,
    config=types.EmbedContentConfig(
        task_type="RETRIEVAL_QUERY",
        output_dimensionality=768
    )
)


query_embedding = (
    result.embeddings[0].values
)


# ==========================================
# SEARCH CHROMADB
# ==========================================

print(
    "Searching KSA menu..."
)


results = collection.query(
    query_embeddings=[
        query_embedding
    ],
    n_results=5
)


# ==========================================
# DISPLAY RESULTS
# ==========================================

print(
    "\n========================================"
)

print(
    "TOP MATCHING KSA MENU ITEMS"
)

print(
    "========================================"
)


documents = results["documents"][0]

metadatas = results["metadatas"][0]

distances = results["distances"][0]


for i in range(len(documents)):

    print(
        f"\n{i + 1}. {documents[i]}"
    )

    print(
        f"   Distance: {distances[i]:.4f}"
    )

    print(
        f"   Metadata: {metadatas[i]}"
    )