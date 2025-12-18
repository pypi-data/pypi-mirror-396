"""
Knowledge ingestion module for Genesis Server
Handles reading documentation files and storing them in the vector database.
"""

import asyncio
import os
import logging
from pathlib import Path
from typing import List, Dict, Any
from openai import AsyncOpenAI
from qdrant_client import QdrantClient
from qdrant_client.http import models
import hashlib

from .config import settings
from .database import get_qdrant_client, ensure_docs_collection_exists

logger = logging.getLogger(__name__)

class DocumentIngestor:
    """
    Service class to handle document ingestion from various sources into the vector database.
    """

    def __init__(self):
        self.qdrant_client = get_qdrant_client()
        self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        ensure_docs_collection_exists(self.qdrant_client)

    async def ingest_docs_directory(self, docs_path: str = "docs"):
        """
        Ingest all documentation files from the specified directory.

        Args:
            docs_path: Path to the documentation directory
        """
        docs_dir = Path(docs_path)
        if not docs_dir.exists():
            raise ValueError(f"Documentation directory does not exist: {docs_path}")

        # Get all markdown files
        md_files = list(docs_dir.rglob("*.md"))
        logger.info(f"Found {len(md_files)} markdown files to process")

        total_processed = 0
        for md_file in md_files:
            try:
                await self.ingest_file(md_file)
                total_processed += 1
                logger.info(f"Processed: {md_file}")
            except Exception as e:
                logger.error(f"Error processing file {md_file}: {e}")

        logger.info(f"Ingestion complete. Processed {total_processed} files.")

    async def ingest_file(self, file_path: Path):
        """
        Ingest a single documentation file into the vector database.

        Args:
            file_path: Path to the documentation file to ingest
        """
        # Read the file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Split the content into chunks
        chunks = self._chunk_document(content, file_path)

        # Process each chunk
        for i, chunk in enumerate(chunks):
            try:
                # Generate embedding for the chunk
                embedding = await self._embed_text(chunk['text'])

                # Create a unique ID for this chunk
                chunk_id = self._generate_chunk_id(str(file_path), i, chunk['text'])

                # Prepare the payload
                payload = {
                    "content": chunk['text'],
                    "source": str(file_path),
                    "title": chunk.get('title', ''),
                    "section": chunk.get('section', ''),
                    "chunk_index": i,
                    "total_chunks": len(chunks)
                }

                # Upsert the point to Qdrant
                self.qdrant_client.upsert(
                    collection_name=settings.QDRANT_DOCS_COLLECTION,
                    points=[
                        models.PointStruct(
                            id=chunk_id,
                            vector=embedding,
                            payload=payload
                        )
                    ]
                )

                logger.debug(f"Upserted chunk {i+1}/{len(chunks)} from {file_path}")
            except Exception as e:
                logger.error(f"Error processing chunk {i} from {file_path}: {e}")
                raise

    def _chunk_document(self, content: str, file_path: Path) -> List[Dict[str, Any]]:
        """
        Split document content into overlapping chunks.

        Args:
            content: The raw document content
            file_path: Path to the source file

        Returns:
            List of document chunks with metadata
        """
        # Simple approach: split by paragraphs, then by sentences if paragraphs are too long
        paragraphs = content.split('\n\n')

        chunks = []
        current_chunk = ""
        current_title = ""

        # Extract title from the first heading if available
        lines = content.split('\n')
        for line in lines:
            if line.strip().startswith('# '):
                current_title = line.strip()[2:]  # Remove '# ' prefix
                break

        for paragraph in paragraphs:
            if len(current_chunk) + len(paragraph) <= settings.CHUNK_SIZE:
                current_chunk += paragraph + "\n\n"
            else:
                # Save the current chunk
                if current_chunk.strip():
                    chunks.append({
                        "text": current_chunk.strip(),
                        "title": current_title,
                        "section": str(file_path)
                    })

                # Start a new chunk with overlap
                # For simplicity, we'll just start fresh with the current paragraph
                # In a more sophisticated implementation, we would have actual overlap
                current_chunk = paragraph + "\n\n"

        # Add the last chunk
        if current_chunk.strip():
            chunks.append({
                "text": current_chunk.strip(),
                "title": current_title,
                "section": str(file_path)
            })

        # Further split large chunks if needed
        final_chunks = []
        for chunk in chunks:
            if len(chunk["text"]) > settings.CHUNK_SIZE:
                # Split by sentences if the chunk is still too large
                sentences = chunk["text"].split('. ')
                temp_chunk = ""

                for sentence in sentences:
                    if len(temp_chunk) + len(sentence) <= settings.CHUNK_SIZE:
                        temp_chunk += sentence + ". "
                    else:
                        if temp_chunk.strip():
                            final_chunks.append({
                                "text": temp_chunk.strip(),
                                "title": chunk["title"],
                                "section": chunk["section"]
                            })
                        temp_chunk = sentence + ". "

                # Add the remaining text as a chunk
                if temp_chunk.strip():
                    final_chunks.append({
                        "text": temp_chunk.strip(),
                        "title": chunk["title"],
                        "section": chunk["section"]
                    })
            else:
                final_chunks.append(chunk)

        return final_chunks

    async def _embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a given text using OpenAI's embedding model.

        Args:
            text: Text to embed

        Returns:
            List of floats representing the embedding
        """
        try:
            response = await self.openai_client.embeddings.create(
                input=text,
                model=settings.EMBEDDING_MODEL
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise

    def _generate_chunk_id(self, file_path: str, chunk_index: int, content: str) -> str:
        """
        Generate a unique ID for a document chunk.

        Args:
            file_path: Path to the source file
            chunk_index: Index of this chunk in the document
            content: Content of the chunk

        Returns:
            Unique ID for the chunk
        """
        # Create a hash of the file path, chunk index, and content to ensure uniqueness
        hash_input = f"{file_path}:{chunk_index}:{content[:100]}".encode('utf-8')
        return hashlib.md5(hash_input).hexdigest()

    async def clear_docs_collection(self):
        """
        Clear all documents from the Qdrant docs collection.
        """
        try:
            self.qdrant_client.delete_collection(settings.QDRANT_DOCS_COLLECTION)
            logger.info(f"Cleared collection: {settings.QDRANT_DOCS_COLLECTION}")
            ensure_docs_collection_exists(self.qdrant_client)  # Recreate the collection
        except Exception as e:
            logger.error(f"Error clearing docs collection: {e}")
            raise