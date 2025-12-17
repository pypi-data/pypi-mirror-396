"""
RAG (Retrieval Augmented Generation) service for Genesis Server
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI
from qdrant_client import QdrantClient
from qdrant_client.http import models
import os

from config import settings
from database import get_qdrant_client, ensure_docs_collection_exists

logger = logging.getLogger(__name__)

class RAGService:
    """
    Service class to handle RAG operations: embedding, search, and generation.
    """

    def __init__(self):
        self.qdrant_client = get_qdrant_client()
        self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        ensure_docs_collection_exists(self.qdrant_client)

    async def process_query(self, query: str, top_k: int = 5, model: str = "gpt-4o") -> Dict[str, Any]:
        """
        Process a user query using the RAG pipeline.

        Args:
            query: The user's question/query
            top_k: Number of top results to retrieve from vector store
            model: The LLM model to use for generation

        Returns:
            Dictionary containing the answer, sources, and model used
        """
        # Step 1: Embed the query
        query_embedding = await self._embed_text(query)

        # Step 2: Search Qdrant for relevant documentation
        search_results = self._search_docs(query_embedding, top_k)

        if not search_results:
            return {
                "answer": "I couldn't find any relevant documentation to answer your question.",
                "sources": [],
                "model_used": model
            }

        # Step 3: Format context from search results
        context = self._format_context(search_results)

        # Step 4: Generate answer using LLM
        answer = await self._generate_answer(query, context, model)

        # Extract sources
        sources = [result.payload.get("source", "") for result in search_results if result.payload.get("source")]

        return {
            "answer": answer,
            "sources": sources,
            "model_used": model
        }

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

    def _search_docs(self, query_embedding: List[float], top_k: int) -> List:
        """
        Search the Qdrant documentation collection for relevant documents.

        Args:
            query_embedding: Embedding of the query
            top_k: Number of results to return

        Returns:
            List of search results
        """
        try:
            results = self.qdrant_client.search(
                collection_name=settings.QDRANT_DOCS_COLLECTION,
                query_vector=query_embedding,
                limit=top_k,
                with_payload=True,
                with_vectors=False
            )
            return results
        except Exception as e:
            logger.error(f"Error searching documentation: {e}")
            raise

    def _format_context(self, search_results: List) -> str:
        """
        Format search results into a context string for the LLM.

        Args:
            search_results: List of search results from Qdrant

        Returns:
            Formatted context string
        """
        context_parts = []
        for result in search_results:
            payload = result.payload
            content = payload.get("content", "")
            source = payload.get("source", "Unknown source")
            score = result.score

            context_parts.append(
                f"Source: {source}\n"
                f"Relevance Score: {score}\n"
                f"Content: {content}\n"
                f"---"
            )

        return "\n".join(context_parts)

    async def _generate_answer(self, query: str, context: str, model: str) -> str:
        """
        Generate an answer using the LLM based on the query and context.

        Args:
            query: The original user query
            context: Retrieved context from documentation
            model: The LLM model to use

        Returns:
            Generated answer
        """
        try:
            system_prompt = (
                "You are a helpful assistant for the Genesis Framework documentation. "
                "Use the provided context to answer the user's question. "
                "If the context doesn't contain enough information, say so. "
                "Be concise and accurate in your response, and cite sources when possible."
            )

            user_message = (
                f"Context:\n{context}\n\n"
                f"Question: {query}\n\n"
                f"Answer:"
            )

            response = await self.openai_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.3,
                max_tokens=1000
            )

            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            raise