"""Gemini embeddings; failed calls never become index vectors."""
import math
import time
from google.genai import errors
from google import genai
from google.genai import types
from .config import Config


class GeminiEmbeddings:
    def __init__(self, api_key=None, model=None, client=None, dimensions=None):
        self.model = model or Config.EMBEDDING_MODEL
        self.dimensions = dimensions or Config.EMBEDDING_DIMENSIONS
        if client is None:
            Config.validate()
        self.client = client or genai.Client(api_key=api_key or Config.GOOGLE_API_KEY,
                                            http_options=types.HttpOptions(timeout=30000, retry_options=types.HttpRetryOptions(attempts=1)))

    def embed_text(self, text, task_type="retrieval_document"):
        result = self.client.models.embed_content(model=self.model, contents=text,
            config=types.EmbedContentConfig(task_type=task_type.upper(), output_dimensionality=self.dimensions))
        vector = list(result.embeddings[0].values)
        if len(vector) != self.dimensions or not all(math.isfinite(v) for v in vector) or not any(vector):
            raise ValueError("Invalid embedding dimensions, values or zero norm")
        return vector

    def embed_batch(self, texts, task_type="retrieval_document", batch_size=32, delay=21):
        if not 1 <= batch_size <= 100:
            raise ValueError("Embedding batch size must be from 1 to 100")
        batch_size = min(batch_size, 32)
        vectors = []
        for start in range(0, len(texts), batch_size):
            batch = texts[start:start + batch_size]
            if start and delay:
                time.sleep(delay)
            for attempt in range(4):
                try:
                    response = self.client.models.embed_content(model=self.model, contents=batch,
                        config=types.EmbedContentConfig(task_type=task_type.upper(), output_dimensionality=self.dimensions))
                    break
                except errors.APIError as exc:
                    if exc.code not in {429, 500, 502, 503, 504} or attempt == 3:
                        raise
                    time.sleep(2 ** attempt * 2)
            values = [list(embedding.values) for embedding in response.embeddings]
            if len(values) != len(batch) or any(len(vector) != self.dimensions or
                    not all(math.isfinite(v) for v in vector) or not any(vector) for vector in values):
                raise ValueError("Invalid embedding batch")
            vectors.extend(values)
        return vectors

    def embed_documents(self, documents):
        return self.embed_batch([document["content"] for document in documents])

    def embed_query(self, query):
        return self.embed_text(query, "retrieval_query")
