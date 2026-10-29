\# Dunkin KSA AI Chatbot



An AI-powered customer service chatbot for Dunkin KSA, built with Google Gemini, FastAPI, ChromaDB, and a RAG-based architecture.



\## Features



\- 🤖 AI-powered conversational chatbot

\- 🇸🇦 Dunkin KSA menu information

\- 🔍 Semantic menu search using embeddings

\- 📚 Retrieval-Augmented Generation (RAG)

\- 🍩 Donut and product search

\- 💰 Price-based menu search

\- 📂 Category-based menu browsing

\- 📍 Official Dunkin KSA store locator information

\- 📝 Customer complaint workflow

\- 🔢 Billing-number collection workflow

\- 🧠 Session-based conversation state

\- 🌙 Light and dark mode

\- 🐳 Docker support

\- 🌐 English chatbot interface



\## Technology Stack



\### Frontend

\- HTML

\- CSS

\- JavaScript



\### Backend

\- Python

\- FastAPI

\- Uvicorn

\- Pydantic



\### AI

\- Google Gemini

\- `gemini-3.5-flash-lite`

\- `gemini-embedding-001`



\### Vector Database

\- ChromaDB



\### Other

\- Playwright

\- Docker

\- Docker Compose

\- JSON

\- python-dotenv



\## Architecture



```text

User

&#x20; │

&#x20; ▼

Frontend

(HTML/CSS/JavaScript)

&#x20; │

&#x20; ▼

FastAPI Backend

&#x20; │

&#x20; ├── Intent Detection

&#x20; │

&#x20; ├── Menu Services

&#x20; │

&#x20; ├── Outlet Services

&#x20; │

&#x20; └── RAG Pipeline

&#x20;         │

&#x20;         ▼

&#x20;     Gemini Embeddings

&#x20;         │

&#x20;         ▼

&#x20;      ChromaDB

&#x20;         │

&#x20;         ▼

&#x20;    Relevant Menu Data

&#x20;         │

&#x20;         ▼

&#x20;      Gemini LLM

&#x20;         │

&#x20;         ▼

&#x20;      AI Response







