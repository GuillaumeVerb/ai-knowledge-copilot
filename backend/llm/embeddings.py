from __future__ import annotations

from collections import Counter
from math import sqrt

from openai import OpenAI

from backend.retrieval.vector_store import EmbeddingProvider


class OpenAIEmbeddingProvider(EmbeddingProvider):
    def __init__(self, *, api_key: str, model: str):
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        response = self.client.embeddings.create(model=self.model, input=texts)
        return [item.embedding for item in response.data]

    def embed_query(self, text: str) -> list[float]:
        return self.embed_documents([text])[0]


class SimpleHashEmbeddingProvider(EmbeddingProvider):
    def __init__(self, dimensions: int = 64):
        self.dimensions = dimensions

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._embed(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._embed(text)

    def _embed(self, text: str) -> list[float]:
        counts = Counter(token.lower() for token in text.split() if token.strip())
        vector = [0.0] * self.dimensions
        for token, count in counts.items():
            vector[hash(token) % self.dimensions] += float(count)
        norm = sqrt(sum(value * value for value in vector)) or 1.0
        return [value / norm for value in vector]
