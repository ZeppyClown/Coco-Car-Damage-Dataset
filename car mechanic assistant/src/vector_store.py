"""Chroma retrieval with canonical applicability and versioned index builds."""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import tempfile
import chromadb
from chromadb.config import Settings
from .config import Config
from .embeddings import GeminiEmbeddings
from .document_processor import DocumentProcessor, canonical_vehicle_value


class VectorStore:
    def __init__(self, persist_directory=None, collection_name=None, embeddings=None):
        self.persist_directory = Path(persist_directory or Config.CHROMA_PERSIST_DIR)
        self.collection_name = collection_name or Config.COLLECTION_NAME
        self.embeddings = embeddings or GeminiEmbeddings()
        self.identity = {"schema": 2, "embedding_model": self.embeddings.model,
                         "dimensions": self.embeddings.dimensions, "distance": "cosine"}
        release = self.persist_directory / "release.json"
        if release.exists():
            saved = json.loads(release.read_text())
            if any(saved.get(key) != value for key, value in self.identity.items()):
                raise ValueError("Index/model schema mismatch; build a fresh index directory")
        elif (self.persist_directory / "chroma.sqlite3").exists():
            raise ValueError("Legacy index left intact; build a fresh versioned index directory")
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(path=str(self.persist_directory),
            settings=Settings(anonymized_telemetry=False))
        self.collection = self.client.get_or_create_collection(name=self.collection_name,
            configuration={"hnsw": {"space": "cosine"}}, metadata=self.identity)
        if not release.exists():
            release.write_text(json.dumps(self.identity, indent=2))

    def add_documents(self, chunks, batch_size=100):
        if not chunks:
            raise ValueError("Cannot index an empty corpus")
        if len({chunk.chunk_id for chunk in chunks}) != len(chunks):
            raise ValueError("Duplicate chunk identifiers")
        vectors = self.embeddings.embed_batch([chunk.content for chunk in chunks], batch_size=batch_size)
        if len(vectors) != len(chunks) or any(len(vector) != self.embeddings.dimensions or
                not all(math.isfinite(value) for value in vector) or not any(vector) for vector in vectors):
            raise ValueError("Invalid embedding batch; nothing was indexed")
        for start in range(0, len(chunks), batch_size):
            batch = chunks[start:start + batch_size]
            self.collection.upsert(ids=[chunk.chunk_id for chunk in batch],
                documents=[chunk.content for chunk in batch],
                embeddings=vectors[start:start + batch_size], metadatas=[chunk.metadata for chunk in batch])
        # Remove old passages from replaced sources only after all new vectors were written.
        for source_id in {chunk.metadata["source_id"] for chunk in chunks}:
            wanted = {chunk.chunk_id for chunk in chunks if chunk.metadata["source_id"] == source_id}
            old = self.collection.get(where={"source_id": source_id})["ids"]
            obsolete = [identifier for identifier in old if identifier not in wanted]
            if obsolete:
                self.collection.delete(ids=obsolete)

    def query(self, query_text, n_results=None, where=None, where_document=None, query_embedding=None):
        count = self.collection.count()
        if count == 0:
            return {"ids": [[]], "documents": [[]], "metadatas": [[]], "distances": [[]]}
        return self.collection.query(query_embeddings=[query_embedding or self.embeddings.embed_query(query_text)],
            n_results=min(n_results or Config.TOP_K_DOCUMENTS, count), where=where,
            where_document=where_document, include=["documents", "metadatas", "distances"])

    def query_with_reranking(self, query_text, n_results=None, vehicle_info=None):
        limit = n_results or Config.TOP_K_DOCUMENTS
        vehicle_info = vehicle_info or {}
        vector = self.embeddings.embed_query(query_text)
        conditions = [{key: canonical_vehicle_value(value)} for key, value in vehicle_info.items()
                      if key in {"make", "model", "engine"} and value]
        if vehicle_info.get("year"):
            year = int(vehicle_info["year"])
            conditions += [{"year_start": {"$lte": year}}, {"year_end": {"$gte": year}}]
        where = conditions[0] if len(conditions) == 1 else {"$and": conditions} if conditions else None
        pools = [self.query(query_text, limit * 3, where=where, query_embedding=vector)]
        if where:
            pools.append(self.query(query_text, limit * 3, where={"scope": "generic"}, query_embedding=vector))
        found = {}
        for pool in pools:
            for index, identifier in enumerate(pool["ids"][0]):
                tags = pool["metadatas"][0][index]
                if tags.get("folder") == "09_workshop_rules":
                    continue
                doc = {"id": identifier, "content": pool["documents"][0][index],
                       "metadata": tags, "distance": pool["distances"][0][index]}
                doc["relevance_score"] = self._calculate_relevance_score(doc, query_text, vehicle_info)
                found[identifier] = doc
        ranked = sorted(found.values(), key=lambda doc: (-doc["relevance_score"], doc["id"]))
        selected, seen = [], set()
        for doc in ranked:
            fingerprint = re.sub(r"\s+", " ", doc["content"]).strip()
            if fingerprint not in seen:
                selected.append(doc)
                seen.add(fingerprint)
            if len(selected) == limit:
                break
        return selected

    def _calculate_relevance_score(self, doc, query_text, vehicle_info=None):
        score = max(0, 1 - doc["distance"]) * 100
        score += Config.FOLDER_PRIORITIES.get(doc["metadata"].get("folder"), 0)
        codes = re.findall(r"\b[PCBU][0-9A-F]{4}\b", query_text.upper())
        score += 20 * sum(bool(re.search(r"\b" + code + r"\b", doc["content"], re.IGNORECASE)) for code in set(codes))
        for key, value in (vehicle_info or {}).items():
            if key in {"make", "model", "engine"} and doc["metadata"].get(key) == canonical_vehicle_value(value):
                score += 15
        return score

    def get_workshop_rules(self):
        return Config.WORKSHOP_RULES_PATH.read_text(encoding="utf-8") if Config.WORKSHOP_RULES_PATH.exists() else ""

    def get_stats(self):
        docs = self.collection.get(include=["metadatas"])
        folders = {}
        for tags in docs["metadatas"]:
            folder = tags.get("folder", "unknown")
            folders[folder] = folders.get(folder, 0) + 1
        return {"total_documents": self.collection.count(), "folder_distribution": folders,
                "index_identity": self.identity}


def main():
    parser = argparse.ArgumentParser(description="Build a new index without touching the serving database")
    parser.add_argument("--knowledge-base", type=Path, default=Config.KNOWLEDGE_BASE_DIR)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Output already exists; choose a new release directory")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=args.output.name + ".building-", dir=args.output.parent))
    processor = DocumentProcessor(Config.CHUNK_SIZE, Config.CHUNK_OVERLAP)
    try:
        chunks = processor.process_knowledge_base(args.knowledge_base)
        store = VectorStore(str(staging))
        store.add_documents(chunks)
        if store.collection.count() != len(chunks):
            raise ValueError("Index count differs from processed corpus")
        manifest = {**processor.manifest, "chunk_size": Config.CHUNK_SIZE, "overlap": Config.CHUNK_OVERLAP}
        (staging / "corpus.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
        release = {**store.identity, "corpus_hash": hashlib.sha256(json.dumps(manifest, sort_keys=True).encode()).hexdigest()}
        (staging / "release.json").write_text(json.dumps(release, indent=2))
        os.rename(staging, args.output)
        print(f"Built {len(chunks)} chunks in {args.output}; restart the app with CHROMA_PERSIST_DIRECTORY set to this release")
    except Exception:
        (staging / "corpus.json").write_text(json.dumps(processor.manifest, ensure_ascii=False, indent=2))
        raise


if __name__ == "__main__":
    main()
