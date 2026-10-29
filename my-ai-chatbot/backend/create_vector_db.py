import json
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
# LOAD KSA MENU
# ==========================================

with open(
    "dunkin_menu.json",
    "r",
    encoding="utf-8"
) as file:

    menu = json.load(file)


print(
    f"Loaded {len(menu)} KSA menu items."
)


# ==========================================
# PREPARE DATA
# ==========================================

documents = []
metadatas = []
ids = []


for index, item in enumerate(menu):

    name = item.get(
        "name",
        ""
    )

    price = item.get(
        "price"
    )

    currency = item.get(
        "currency",
        "SAR"
    )

    category = item.get(
        "category",
        ""
    )

    description = item.get(
        "description",
        ""
    )

    customisable = item.get(
        "customisable",
        False
    )

    source = item.get(
        "source",
        ""
    )


    # --------------------------------------
    # Text that Gemini will embed
    # --------------------------------------

    if price is not None:

        price_text = (
            f"{currency} {price:.2f}"
        )

    else:

        price_text = "Price unavailable"


    document = (
        f"Product: {name}. "
        f"Category: {category}. "
        f"Price: {price_text}. "
        f"Description: {description}. "
        f"Customisable: "
        f"{'Yes' if customisable else 'No'}."
    )


    documents.append(
        document
    )


    # --------------------------------------
    # Metadata stored in Chroma
    # --------------------------------------

    metadatas.append(
        {
            "name": name,
            "category": category,
            "price": (
                float(price)
                if price is not None
                else 0.0
            ),
            "currency": currency,
            "customisable": customisable,
            "source": source
        }
    )


    ids.append(
        f"ksa_menu_{index}"
    )


# ==========================================
# GENERATE GEMINI EMBEDDINGS
# ==========================================

print(
    "\nGenerating Gemini embeddings..."
)


result = client.models.embed_content(
    model="gemini-embedding-001",
    contents=documents,
    config=types.EmbedContentConfig(
        task_type="RETRIEVAL_DOCUMENT",
        output_dimensionality=768
    )
)


embeddings = [
    embedding.values
    for embedding in result.embeddings
]


print(
    f"Generated {len(embeddings)} embeddings."
)


# ==========================================
# CONNECT TO CHROMADB
# ==========================================

chroma_client = chromadb.PersistentClient(
    path="chroma_db"
)


# ==========================================
# CREATE A NEW KSA COLLECTION
# ==========================================

collection = chroma_client.get_or_create_collection(
    name="dunkin_menu_ksa"
)


# ==========================================
# STORE DATA
# ==========================================

collection.upsert(
    ids=ids,
    documents=documents,
    metadatas=metadatas,
    embeddings=embeddings
)


# ==========================================
# FINISHED
# ==========================================

print("\n========================================")
print("KSA VECTOR DATABASE CREATED")
print("========================================")

print(
    f"Documents stored: "
    f"{collection.count()}"
)

print(
    "Collection: dunkin_menu_ksa"
)