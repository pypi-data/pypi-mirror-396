"""
Main entry point for the Genesis Server - RAG Backend
"""

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
import logging

import os
from dotenv import load_dotenv

# Ye line code ko batati hai ke .env file aik folder peeche (root mein) hai
print("🔍 Loading environment variables...")
load_dotenv(dotenv_path="../.env")

# Debugging ke liye check karein ke URL load hua ya nahi
print(f"🔍 DEBUG: Qdrant URL is -> {os.getenv('QDRANT_URL')}")

from config import settings
from database import get_qdrant_client
from rag import RAGService

# Initialize FastAPI app
app = FastAPI(
    title="Genesis Server",
    description="RAG Backend for the Genesis Framework Documentation",
    version="0.1.0"
)

# Initialize RAG service
rag_service = RAGService()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChatRequest(BaseModel):
    query: str
    top_k: Optional[int] = settings.TOP_K
    model: Optional[str] = settings.LLM_MODEL

class ChatResponse(BaseModel):
    query: str
    answer: str
    sources: List[str]
    model_used: str

@app.get("/")
async def root():
    return {"message": "Welcome to the Genesis Server - RAG Backend"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "genesis-server"}

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    RAG endpoint that accepts a user query and returns an answer based on documentation.

    The process:
    1. Embed the user query
    2. Search Qdrant for relevant documentation
    3. Generate an answer using the LLM based on retrieved context
    """
    try:
        logger.info(f"Processing chat request: {request.query[:50]}...")

        # Process the query through the RAG pipeline
        result = await rag_service.process_query(
            query=request.query,
            top_k=request.top_k,
            model=request.model
        )

        logger.info("Chat request processed successfully")

        return ChatResponse(
            query=request.query,
            answer=result["answer"],
            sources=result["sources"],
            model_used=result["model_used"]
        )
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "genesis_server.main:app",
        host="0.0.0.0",
        port=settings.SERVER_PORT,
        reload=settings.RELOAD_ON_DEV
    )