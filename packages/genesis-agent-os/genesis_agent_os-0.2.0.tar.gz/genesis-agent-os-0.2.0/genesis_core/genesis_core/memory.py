"""
Memory management for the Genesis Core framework.

This module implements Qdrant vector storage for persistent agent memories.
"""

import asyncio
from typing import List, Dict, Any, Optional, Union
from uuid import uuid4
from datetime import datetime
from qdrant_client import QdrantClient
from qdrant_client.http import models
from pydantic import BaseModel
from .schemas import MemorySchema
from .errors import MemoryOperationError


class MemoryManager:
    """
    Manages memory operations using Qdrant vector database.
    """

    def __init__(
        self,
        location: Optional[str] = None,
        url: Optional[str] = None,
        api_key: Optional[str] = None,
        collection_name: str = "agent_memories"
    ):
        """
        Initialize the MemoryManager with Qdrant connection.

        Args:
            location: Path to local Qdrant instance (e.g., "./qdrant_data")
            url: URL to remote Qdrant instance
            api_key: API key for Qdrant authentication
            collection_name: Name of the collection to store memories
        """
        self.collection_name = collection_name
        self.client = QdrantClient(
            location=location,
            url=url,
            api_key=api_key
        )
        self._initialize_collection()

    def _initialize_collection(self) -> None:
        """
        Initialize the Qdrant collection for storing agent memories.
        """
        try:
            # Check if collection exists
            self.client.get_collection(self.collection_name)
        except:
            # Create collection if it doesn't exist
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(size=1536, distance=models.Distance.COSINE),  # Assuming OpenAI embeddings
            )

            # Create payload index for agent_id for faster filtering
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="agent_id",
                field_schema=models.PayloadSchemaType.KEYWORD
            )

    async def store_memory(
        self,
        agent_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
        embedding: Optional[List[float]] = None
    ) -> str:
        """
        Store a memory in the vector database.

        Args:
            agent_id: ID of the agent creating this memory
            content: The content to store as memory
            metadata: Additional metadata about the memory
            tags: Tags for categorizing the memory
            embedding: Pre-computed embedding vector (optional)

        Returns:
            ID of the stored memory
        """
        try:
            # Generate a unique ID for the memory
            memory_id = f"mem_{str(uuid4()).replace('-', '')[:12]}"

            # If no embedding is provided, we'd normally generate one here
            # For now, we'll create a placeholder embedding
            if embedding is None:
                # In a real implementation, you'd generate an embedding from the content
                # using an embedding model like OpenAI's text-embedding-ada-002
                embedding = [0.0] * 1536  # Placeholder for 1536-dimensional embedding

            # Create memory schema instance
            memory = MemorySchema(
                id=memory_id,
                agent_id=agent_id,
                content=content,
                metadata=metadata or {},
                created_at=datetime.now(),
                tags=tags or [],
                embedding=embedding
            )

            # Prepare the point for Qdrant
            point = models.PointStruct(
                id=memory_id,
                vector=embedding,
                payload={
                    "agent_id": agent_id,
                    "content": content,
                    "metadata": memory.metadata,
                    "created_at": memory.created_at.isoformat(),
                    "tags": memory.tags
                }
            )

            # Store the memory in Qdrant
            self.client.upsert(
                collection_name=self.collection_name,
                points=[point]
            )

            return memory_id
        except Exception as e:
            raise MemoryOperationError(f"Failed to store memory: {e}")

    async def retrieve_memory(self, memory_id: str) -> Optional[MemorySchema]:
        """
        Retrieve a specific memory by ID.

        Args:
            memory_id: ID of the memory to retrieve

        Returns:
            MemorySchema instance or None if not found
        """
        try:
            records = self.client.retrieve(
                collection_name=self.collection_name,
                ids=[memory_id]
            )

            if not records:
                return None

            record = records[0]
            payload = record.payload

            return MemorySchema(
                id=record.id,
                agent_id=payload["agent_id"],
                content=payload["content"],
                metadata=payload.get("metadata", {}),
                created_at=datetime.fromisoformat(payload["created_at"]),
                tags=payload.get("tags", []),
                embedding=record.vector if hasattr(record, 'vector') else None
            )
        except Exception as e:
            raise MemoryOperationError(f"Failed to retrieve memory: {e}")

    async def search_memories(
        self,
        query_embedding: List[float],
        agent_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 10
    ) -> List[MemorySchema]:
        """
        Search for memories using semantic similarity.

        Args:
            query_embedding: Embedding vector to search for similar memories
            agent_id: Optional filter by agent ID
            tags: Optional filter by tags
            limit: Maximum number of results to return

        Returns:
            List of matching MemorySchema instances
        """
        try:
            # Build filters
            filters = []
            if agent_id:
                filters.append(
                    models.FieldCondition(
                        key="agent_id",
                        match=models.MatchValue(value=agent_id)
                    )
                )

            if tags:
                filters.append(
                    models.FieldCondition(
                        key="tags",
                        match=models.MatchAny(any=tags)
                    )
                )

            query_filter = models.Filter(must=filters) if filters else None

            # Perform the search
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                query_filter=query_filter,
                limit=limit
            )

            memories = []
            for result in results:
                payload = result.payload
                memory = MemorySchema(
                    id=result.id,
                    agent_id=payload["agent_id"],
                    content=payload["content"],
                    metadata=payload.get("metadata", {}),
                    created_at=datetime.fromisoformat(payload["created_at"]),
                    tags=payload.get("tags", []),
                    embedding=result.vector if hasattr(result, 'vector') else None
                )
                memories.append(memory)

            return memories
        except Exception as e:
            raise MemoryOperationError(f"Failed to search memories: {e}")

    async def get_memories_by_agent(
        self,
        agent_id: str,
        limit: int = 100
    ) -> List[MemorySchema]:
        """
        Retrieve all memories associated with a specific agent.

        Args:
            agent_id: ID of the agent whose memories to retrieve
            limit: Maximum number of results to return

        Returns:
            List of MemorySchema instances
        """
        try:
            # Use scroll to get all memories for the agent
            records, _ = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="agent_id",
                            match=models.MatchValue(value=agent_id)
                        )
                    ]
                ),
                limit=limit
            )

            memories = []
            for record in records:
                payload = record.payload
                memory = MemorySchema(
                    id=record.id,
                    agent_id=payload["agent_id"],
                    content=payload["content"],
                    metadata=payload.get("metadata", {}),
                    created_at=datetime.fromisoformat(payload["created_at"]),
                    tags=payload.get("tags", []),
                    embedding=record.vector if hasattr(record, 'vector') else None
                )
                memories.append(memory)

            return memories
        except Exception as e:
            raise MemoryOperationError(f"Failed to get memories by agent: {e}")

    async def delete_memory(self, memory_id: str) -> bool:
        """
        Delete a specific memory.

        Args:
            memory_id: ID of the memory to delete

        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            operation_info = self.client.delete(
                collection_name=self.collection_name,
                points_selector=models.PointIdsList(points=[memory_id])
            )
            return True
        except Exception as e:
            raise MemoryOperationError(f"Failed to delete memory: {e}")

    async def clear_agent_memories(self, agent_id: str) -> bool:
        """
        Delete all memories associated with a specific agent.

        Args:
            agent_id: ID of the agent whose memories to delete

        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            # Get all memory IDs for this agent first
            memories = await self.get_memories_by_agent(agent_id, limit=10000)  # Large limit to get all
            memory_ids = [mem.id for mem in memories]

            if memory_ids:
                self.client.delete(
                    collection_name=self.collection_name,
                    points_selector=models.PointIdsList(points=memory_ids)
                )

            return True
        except Exception as e:
            raise MemoryOperationError(f"Failed to clear agent memories: {e}")


# Global memory manager instance (optional, for convenience)
_memory_manager: Optional[MemoryManager] = None


def get_memory_manager() -> MemoryManager:
    """
    Get the global memory manager instance, creating it if necessary.

    Returns:
        MemoryManager instance
    """
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = MemoryManager()
    return _memory_manager