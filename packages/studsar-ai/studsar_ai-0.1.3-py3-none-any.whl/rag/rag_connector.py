# rag_connector.py – integrate Retrieval-Augmented Generation natively into StudSar
# Author: Francesco Bulla (Brainverse.)
# I wrote this module so that StudSar can ingest PDFs, TXT, CSV,
# web pages and even DB rows, then memorise every meaningful
# segment inside the same neural memory used for day-to-day queries.
from __future__ import annotations
import importlib.util
import logging
import os
from typing import Any, Dict, List, Optional

#  logging 
logger = logging.getLogger("studsar.rag")
if not logger.handlers:
    _h = logging.StreamHandler()
    _h.setFormatter(
        logging.Formatter("%(asctime)s — %(name)s — %(levelname)s — %(message)s")
    )
    logger.addHandler(_h)
logger.setLevel(logging.INFO)

#  dependency verification 
def _check_dependencies() -> bool:
    """I make sure the main optional deps for RAG are available."""
    deps = {
        "langchain_community": "langchain-community",
        "langchain_core": "langchain-core",
        "sentence_transformers": "sentence-transformers",
    }
    missing: List[str] = []
    for mod, pip_name in deps.items():
        try:
            if mod == "langchain_core":
                importlib.import_module("langchain_core.documents")
            else:
                importlib.import_module(mod)
        except ImportError:
            missing.append(pip_name)

    if missing:
        logger.warning(
            "Missing dependencies: %s  → pip install %s",
            ", ".join(missing),
            " ".join(missing),
        )
        return False
    return True

DEPS_OK = _check_dependencies()

# optional imports 
if DEPS_OK:
    try:
        from langchain_community.document_loaders import (
            CSVLoader,
            PyPDFLoader,
            TextLoader,
            WebBaseLoader,
        )
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        from sentence_transformers import SentenceTransformer

        try:
            from langchain_core.documents import Document
        except ImportError:
            # older split of langchain_core
            from langchain_core.documents.base import Document
    except ImportError as e:
        logger.error("Dependency import failed after check: %s", e)
        DEPS_OK = False

# StudSar_V3  forward declaration ...import 
try:
    from ..managers.manager import StudSarManager as Manager
except Exception:
    # Fallback for standalone typing / tests
    class Manager:  # type: ignore
        def update_network(self, *a, **kw): ...
        def search(self, *a, **kw): ...
        @property
        def text_processor(self): ...
        @property
        def neural_network(self): ...


# Class Rag guys 
class RAGConnector:
    """
    I plug *Retrieval-Augmented Generation* into StudSar's memory
    without using an external vector DB. Everything lives inside
    the same neural network.
    """
    def __init__(self, studsar_manager: Manager, embedding_model_name: str = "all-MiniLM-L6-v2") -> None:
        if not DEPS_OK:
            raise RuntimeError("RAGConnector initialised without its optional dependencies.")

        # sanity-check manager interface
        for attr in ("update_network", "search", "text_processor"):
            if not hasattr(studsar_manager, attr):
                raise ValueError(f"StudSarManager is missing required attribute: {attr}")

        self.manager: Manager = studsar_manager
        self.text_processor = self.manager.text_processor

        # I reuse the shared SentenceTransformer if the text processor already exposes it
        if hasattr(self.text_processor, "embedding_model"):
            self.embedding_model = self.text_processor.embedding_model
            logger.info("Embedding model reused from StudSar text_processor.")
        else:
            self.embedding_model = SentenceTransformer(embedding_model_name)
            logger.info("Embedding model %s loaded locally.", embedding_model_name)

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ". ", " ", ""],
            length_function=len,
        )

        self.external_sources: Dict[str, Dict[str, Any]] = {}
        logger.info("RAGConnector ready – unified memory online.")

    #  internal helpers 
    def _load_and_split(self, loader) -> List[Document]:
        try:
            docs = loader.load()
            return self.text_splitter.split_documents(docs)
        except Exception as err:
            logger.error("Load/split error: %s", err, exc_info=True)
            return []

    def _memorize_splits(self, splits: List[Document], source_id: str, base_meta: Dict[str, Any]) -> int:
        count = 0
        for idx, split in enumerate(splits):
            try:
                # Use StudSar's text processor for segmentation
                pieces = self.text_processor.segment_text(split.page_content)
            except Exception as err:
                logger.error("Segmentation error: %s", err, exc_info=True)
                pieces = [split.page_content]

            for seg in pieces:
                seg = seg.strip()
                if not seg:
                    continue

                tags = [
                    f"external_source_id:{source_id}",
                    f"source_type:{base_meta.get('type', 'unknown')}",
                ]

                meta = {**base_meta, **getattr(split, "metadata", {}), "original_split_index": idx}
                if "page" not in meta and hasattr(split, "metadata") and "page" in split.metadata:
                    meta["page"] = split.metadata["page"]

                try:
                    # Use StudSar's update_network method with emotion support
                    emotion = base_meta.get("emotion", "neutral")
                    self.manager.update_network(seg, emotion=emotion)
                    count += 1
                except Exception as err:
                    logger.error("Memorise error (%s): %s", source_id, err, exc_info=True)
        return count

    #  public ingestion API 
    def add_document(self, file_path: str, *, source_id: Optional[str] = None, metadata_extra: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Add a document (PDF, TXT, CSV) to StudSar's memory via RAG."""
        if not DEPS_OK:
            logger.error("Cannot add document, dependencies not satisfied.")
            return None
        if not os.path.exists(file_path):
            logger.error("File not found: %s", file_path)
            return None

        source_id = source_id or f"file_{os.path.basename(file_path)}_{len(self.external_sources)+1}"
        if source_id in self.external_sources:
            logger.warning("Source ID %s already exists – overwriting.", source_id)

        ext = os.path.splitext(file_path)[1].lower()
        loader, doc_type = None, "unknown"
        try:
            if ext == ".pdf":
                loader, doc_type = PyPDFLoader(file_path), "pdf"
            elif ext == ".txt":
                loader, doc_type = TextLoader(file_path, autodetect_encoding=True), "txt"
            elif ext == ".csv":
                loader, doc_type = CSVLoader(file_path, autodetect_encoding=True), "csv"
            else:
                logger.error("Unsupported file type: %s", ext)
                return None
        except Exception as err:
            logger.error("Loader init failed: %s", err, exc_info=True)
            return None

        logger.info("Loading document '%s' (type: %s) with source ID: %s...", file_path, doc_type, source_id)
        splits = self._load_and_split(loader)
        if not splits:
            logger.warning("No split content obtained from '%s'.", file_path)
            return None

        meta = {"original_path": file_path, "type": doc_type, **(metadata_extra or {})}
        memorised = self._memorize_splits(splits, source_id, meta)

        if memorised:
            self.external_sources[source_id] = {
                **meta,
                "segments_memorized": memorised,
                "total_splits_processed": len(splits),
                # "added_at": self.manager.get_timestamp(), # Metodo non trovato in StudSarManager
            }
            logger.info("Document %s → %d segments memorised.", file_path, memorised)
            return source_id
        logger.warning("No segments memorised from %s", file_path)
        return None

    def add_web_content(self, url: str, *, source_id: Optional[str] = None, metadata_extra: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Add web page content to StudSar's memory via RAG."""
        if not DEPS_OK:
            logger.error("Cannot add web content, dependencies not satisfied.")
            return None
        
        source_id = source_id or f"web_{url.split('//')[-1].split('/')[0].replace('.', '_')}_{len(self.external_sources)+1}"
        if source_id in self.external_sources:
            logger.warning("Source ID %s already exists – overwriting.", source_id)

        try:
            loader = WebBaseLoader(web_path=url)
        except Exception as err:
            logger.error("WebBaseLoader init failed for '%s': %s", url, err, exc_info=True)
            return None

        logger.info("Loading web content from '%s' with source ID: %s...", url, source_id)
        splits = self._load_and_split(loader)
        if not splits:
            logger.warning("No split content obtained from '%s'.", url)
            return None

        meta = {"original_url": url, "type": "web", **(metadata_extra or {})}
        memorised = self._memorize_splits(splits, source_id, meta)

        if memorised:
            self.external_sources[source_id] = {
                **meta,
                "segments_memorized": memorised,
                "total_splits_processed": len(splits),
                # "added_at": self.manager.get_timestamp(), # Metodo non trovato in StudSarManager
            }
            logger.info("Web %s → %d segments memorised.", url, memorised)
            return source_id
        logger.warning("No segments memorised from web content '%s'.", url)
        return None

    def add_database_content(  # simplified sqlite example
        self,
        db_connection: str,
        query: str,
        *,
        source_id: Optional[str] = None,
        metadata_extra: Optional[Dict[str, Any]] = None,
        row_to_text: Optional[callable] = None,
    ) -> Optional[str]:
        """Add database query results to StudSar's memory via RAG."""
        if not DEPS_OK:
            logger.error("Cannot add DB content, dependencies not satisfied.")
            return None

        import sqlite3

        source_id = source_id or f"db_{len(self.external_sources)+1}"
        if source_id in self.external_sources:
            logger.warning("Source ID %s already exists – overwriting.", source_id)

        try:
            conn = sqlite3.connect(db_connection)
            cur = conn.cursor()
            cur.execute(query)
            rows = cur.fetchall()
            cols = [d[0] for d in cur.description]
            conn.close()
        except Exception as err:
            logger.error("Database access failed: %s", err, exc_info=True)
            return None

        if not rows:
            logger.warning("DB query returned 0 rows.")
            return None

        logger.info("Processing data from database (source: %s), %d rows...", source_id, len(rows))
        docs: List[Document] = []
        base_meta = {"db_connection": db_connection, "original_query": query, "type": "database", **(metadata_extra or {})}
        
        for idx, row in enumerate(rows):
            row_dict = dict(zip(cols, row))
            text = row_to_text(row_dict, cols) if row_to_text else "\n".join(f"{k}: {v}" for k, v in row_dict.items() if v is not None)
            docs.append(Document(page_content=text, metadata={**base_meta, "row_index": idx}))

        memorised = self._memorize_splits(docs, source_id, base_meta)
        if memorised:
            self.external_sources[source_id] = {
                **base_meta,
                "segments_memorized": memorised,
                "total_rows_processed": len(rows),
                # "added_at": self.manager.get_timestamp(), # Metodo non trovato in StudSarManager
            }
            logger.info("DB source %s → %d segments memorised.", source_id, memorised)
            return source_id
        logger.warning("No segments memorised from database data.")
        return None

    #  search 
    def search_external_sources(
        self,
        query: str,
        *,
        limit: int = 5,
        source_id_filter: Optional[List[str]] = None,
        source_type_filter: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """Search for relevant information in indexed external sources."""
        tags = []
        if source_id_filter:
            tags += [f"external_source_id:{sid}" for sid in source_id_filter]
        if source_type_filter:
            tags += [f"source_type:{stype}" for stype in source_type_filter]

        logger.info("Searching external sources with query: '%s...', filters: %s", query[:50], tags)
        try:
            # Use StudSar's search method
            ids, similarities, segments = self.manager.search(query, k=limit)
            
            # Convert to expected format and filter by tags if needed
            raw = []
            for i, (marker_id, sim, seg) in enumerate(zip(ids, similarities, segments)):
                marker_details = self.manager.get_marker_details(marker_id)
                if marker_details:
                    # Check if this marker has external source tags
                    marker_tags = getattr(marker_details, 'tags', [])
                    if tags:
                        # Filter by required tags
                        if not any(tag in marker_tags for tag in tags):
                            continue
                    
                    raw.append({
                        "text": seg,
                        "score": sim,
                        "tags": marker_tags,
                        "metadata": getattr(marker_details, 'metadata', {})
                    })
        except Exception as err:
            logger.error("Search failed: %s", err, exc_info=True)
            return []

        enriched = []
        for item in raw:
            sid = next((t.split(":", 1)[1] for t in item.get("tags", []) if t.startswith("external_source_id:")), None)
            enriched.append(
                {
                    "text": item.get("text", ""),
                    "score": item.get("score", 0.0),
                    "source_id": sid,
                    "source_details": self.external_sources.get(sid, {}),
                    "original_metadata": item.get("metadata", {}),
                }
            )
        return enriched

    # housekeeping 
    def remove_external_source(self, source_id: str, *, purge_memory: bool = False) -> bool:
        """Remove an external source from RAG tracking and optionally from memory."""
        if source_id not in self.external_sources:
            logger.warning("Source '%s' not found in RAGConnector, cannot remove.", source_id)
            return False

        logger.info("Removing source '%s' from RAG tracking.", source_id)

        if purge_memory and hasattr(self.manager, "delete_segments_by_tag"):
            try:
                deleted = self.manager.delete_segments_by_tag(f"external_source_id:{source_id}")
                logger.info("Purged %d segments for %s from core memory.", deleted, source_id)
            except Exception as err:
                logger.error("Error purging segments for '%s': %s", source_id, err, exc_info=True)
        elif purge_memory:
            logger.warning("StudSar manager doesn't support 'delete_segments_by_tag'. Memory purge skipped.")

        self.external_sources.pop(source_id, None)
        logger.info("Source %s removed from RAG tracking.", source_id)
        return True

    def update_external_source(self, source_id: str, *, content_path: Optional[str] = None, metadata_update: Optional[Dict[str, Any]] = None) -> bool:
        """Update an existing external source with new content or metadata."""
        if source_id not in self.external_sources:
            logger.error("Unknown source id: %s", source_id)
            return False

        source_info_original = self.external_sources[source_id].copy()

        # Update metadata if provided
        if metadata_update:
            self.external_sources[source_id].update(metadata_update)
            # self.external_sources[source_id]["updated_at"] = self.manager.get_timestamp() # Metodo non trovato in StudSarManager
            logger.info("Metadata updated for %s", source_id)

        # If content update is requested
        if content_path:
            src_type = self.external_sources[source_id]["type"]
            logger.info("Updating content for source '%s' (type: %s) from new path: %s", source_id, src_type, content_path)
            
            # Remove existing source with memory purge
            self.remove_external_source(source_id, purge_memory=True)

            # Re-add with the same ID and updated metadata
            new_metadata_extra = {k: v for k, v in source_info_original.items() 
                                if k not in ['type', 'path', 'url', 'added_at', 'segments_memorized', 
                                           'total_splits_processed', 'db_connection', 'query']}
            if metadata_update:
                new_metadata_extra.update(metadata_update)
            if src_type in {"pdf", "txt", "csv"}:
                re_id = self.add_document(content_path, source_id=source_id, metadata_extra=new_metadata_extra)
            elif src_type == "web":
                re_id = self.add_web_content(content_path, source_id=source_id, metadata_extra=new_metadata_extra)
            else:
                logger.error("Content refresh not supported for type %s", src_type)
                # Restore original info if re-adding fails
                self.external_sources[source_id] = source_info_original
                return False
            if re_id == source_id:
                logger.info("Source '%s' content updated successfully.", source_id)
                return True
            else:
                logger.error("Failed to update content for source '%s'.", source_id)
                return False

        return True

    # diagnostics and stats
    def get_source_statistics(self) -> Dict[str, Any]:
        """Returns statistics about loaded external sources."""
        stats = {"total_sources": len(self.external_sources), "total_segments_memorized": 0, "by_type": {}}
        for info in self.external_sources.values():
            t = info.get("type", "unknown")
            stats["by_type"].setdefault(t, {"count": 0, "segments": 0})
            stats["by_type"][t]["count"] += 1
            stats["by_type"][t]["segments"] += info.get("segments_memorized", 0)
            stats["total_segments_memorized"] += info.get("segments_memorized", 0)
        logger.debug("Source statistics: %s", stats)
        return stats

    def debug_source(self, source_id: str) -> Dict[str, Any]:
        """Returns detailed information about a specific source for debugging."""
        if source_id not in self.external_sources:
            logger.warning("Source '%s' not found for debugging.", source_id)
            return {"error": "source not found"}

        dbg = self.external_sources[source_id].copy()
        try:
            # Try to find sample segments using the search method
            sample_results = self.search_external_sources(
                "", 
                limit=3, 
                source_id_filter=[source_id]
            )
            dbg["sample_segments_from_memory"] = sample_results
        except Exception as err:
            logger.error("Error retrieving sample segments for '%s': %s", source_id, err, exc_info=True)
            dbg["sample_segments_from_memory"] = {"error": str(err)}
        
        logger.debug("Debug information for source '%s': %s", source_id, dbg)
        return dbg

    def list_external_sources(self) -> Dict[str, Dict[str, Any]]:
        """Returns a dictionary of all loaded external sources."""
        return self.external_sources.copy()

# Now Demo "o yes"
if __name__ == "__main__":
    # quick smoke-test with the in-file MockManager
    class _MockTP:
        def __init__(self):
            from sentence_transformers import SentenceTransformer
            self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

        def segment_text(self, txt: str) -> List[str]:
            return [t.strip() for t in txt.split(".") if t.strip()]

    class _MockManager(Manager):  # type: ignore
        def __init__(self):
            self._memory_db: List[Dict[str, Any]] = []
            self._tp = _MockTP()
            self._counter = 0
            
        # StudSarManager contract 
        @property
        def text_processor(self):
            return self._tp
        def update_network(self, text, emotion=None):
            """Mock update_network to simulate StudSar behavior."""
            self._memory_db.append({
                "text": text, 
                "tags": [f"external_source_id:test"], 
                "metadata": {"emotion": emotion}
            })
            return len(self._memory_db) - 1

        def search(self, query, k=5):
            """Mock search that returns ids, similarities, segments."""
            ids, similarities, segments = [], [], []
            for i, e in enumerate(self._memory_db):
                if query and query.lower() not in e["text"].lower():
                    continue
                ids.append(i)
                similarities.append(0.9)
                segments.append(e["text"])
                if len(ids) >= k:
                    break
            return ids, similarities, segments

        def get_marker_details(self, marker_id):
            """Mock marker details retrieval."""
            if 0 <= marker_id < len(self._memory_db):
                return self._memory_db[marker_id]
            return None
        
        def get_timestamp(self):
            """Generate an ISO format timestamp to track when documents are added/updated."""
            from datetime import datetime
            return datetime.now().isoformat()

        def delete_segments_by_tag(self, tag):
            before = len(self._memory_db)
            self._memory_db = [e for e in self._memory_db if tag not in e.get("tags", [])]
            return before - len(self._memory_db)

    print("RAGConnector smoke test starting...")
    mgr = _MockManager()
    rag = RAGConnector(mgr)
    
    # Test document addition
    path = "tmp_demo.txt"
    with open(path, "w", encoding="utf-8") as f:
        f.write("Artificial intelligence is amazing. Machine learning is part of AI. Deep learning uses neural networks.")
    
    result = rag.add_document(path, metadata_extra={"topic": "AI"})
    print(f"Document added with source_id: {result}")
    
    # Test search
    search_results = rag.search_external_sources("machine learning")
    print(f"Search results: {len(search_results)} found")
    for i, res in enumerate(search_results):
        print(f"  {i+1}. Score: {res['score']:.2f} | Text: {res['text'][:50]}...")
    
    # Test statistics
    stats = rag.get_source_statistics()
    print(f"Statistics: {stats}")
   
    # Cleanup
    os.remove(path)
    print("Smoke test completed successfully!")