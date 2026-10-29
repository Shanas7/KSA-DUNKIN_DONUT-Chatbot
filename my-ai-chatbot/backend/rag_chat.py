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


print("KSA menu database loaded.")

print(
    f"Products available: {collection.count()}"
)


# ==========================================
# GET USER QUESTION
# ==========================================

question = input(
    "\nAsk the Dunkin KSA assistant: "
)


# ==========================================
# CREATE QUERY EMBEDDING
# ==========================================

print(
    "\nSearching the KSA menu..."
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

results = collection.query(
    query_embeddings=[
        query_embedding
    ],
    n_results=5
)


# ==========================================
# BUILD CONTEXT
# ==========================================

documents = results["documents"][0]

context = "\n".join(
    documents
)


# ==========================================
# CREATE RAG PROMPT
# ==========================================

prompt = f"""
You are a helpful customer-service assistant
for Dunkin Saudi Arabia.

Answer the customer's question using ONLY
the Dunkin menu information provided below.

Important rules:

1. Do not invent products.
2. Do not invent prices.
3. Do not invent ingredients.
4. Do not invent availability.
5. Prices are in Saudi Riyals (SAR).
6. If the information is not available,
   clearly say that you don't have enough
   information.
7. Keep the answer short and friendly.
8. When giving a price, include SAR.

DUNKIN KSA MENU INFORMATION:

{context}

CUSTOMER QUESTION:

{question}
"""


# ==========================================
# GENERATE ANSWER
# ==========================================

print(
    "\nGenerating answer..."
)


response = client.models.generate_content(
    model="gemini-3.7-flash",
    contents=prompt,
    config=types.GenerateContentConfig(
        automatic_function_calling=(
            types.AutomaticFunctionCallingConfig(
                disable=True
            )
        )
    )
)


# ==========================================
# DISPLAY ANSWER
# ==========================================

print("\n========================================")

print("DUNKIN ASSISTANT")

print("========================================")

print(
    response.text
)
