import asyncio
from typing import Any, Dict, List, Optional, Sequence, cast

from google.cloud.firestore import Client, FieldFilter
from google.cloud.firestore_v1.base_vector_query import DistanceMeasure
from google.cloud.firestore_v1.vector import Vector

from agno.filters import FilterExpr
from agno.knowledge.document import Document
from agno.knowledge.embedder import Embedder
from agno.knowledge.reranker.base import Reranker
from agno.utils.log import log_debug, log_error, log_warning
from agno.utils.string import hash_string_sha256
from agno.vectordb.base import VectorDb
from agno.vectordb.distance import Distance
from agno.vectordb.search import SearchType


class FirestoreVectorDb(VectorDb):
    """Firestore-backed vector database using Firestore vector search."""

    def __init__(
        self,
        collection_name: str,
        db_client: Client,
        embedder: Optional[Embedder] = None,
        search_type: SearchType = SearchType.vector,
        distance: Distance = Distance.cosine,
        reranker: Optional[Reranker] = None,
        vector_field: str = "embedding",
        content_field: str = "content",
        metadata_field: str = "meta_data",
        name_field: str = "name",
        content_hash_field: str = "content_hash",
        content_id_field: str = "content_id",
        id_field: str = "id",
        similarity_threshold: Optional[float] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        id: Optional[str] = None,
    ):
        if not collection_name:
            raise ValueError("collection_name must be provided.")
        if db_client is None:
            raise ValueError("db_client must be provided.")
        if search_type != SearchType.vector:
            raise ValueError("FirestoreVectorDb only supports vector search.")
        if distance not in {Distance.cosine, Distance.l2, Distance.max_inner_product}:
            raise ValueError(f"Unsupported distance metric: {distance}")

        super().__init__(id=id, name=name or collection_name, description=description, similarity_threshold=similarity_threshold)

        if embedder is None:
            from agno.knowledge.embedder.openai import OpenAIEmbedder

            embedder = OpenAIEmbedder()
            log_debug("Embedder not provided, using OpenAIEmbedder as default.")

        self.collection_name = collection_name
        self.db_client = db_client
        self.embedder: Embedder = embedder
        self.search_type = search_type
        self.distance = distance
        self.reranker = reranker

        self.vector_field = vector_field
        self.content_field = content_field
        self.metadata_field = metadata_field
        self.name_field = name_field
        self.content_hash_field = content_hash_field
        self.content_id_field = content_id_field
        self.id_field = id_field

        self.dimensions = self.embedder.dimensions
        if self.dimensions is None:
            raise ValueError("Embedder.dimensions must be set.")

        self._collection = self.db_client.collection(self.collection_name)
        log_debug(f"Initialized FirestoreVectorDb with collection '{self.collection_name}'")

    @property
    def collection(self):
        return self._collection

    def _distance_measure(self) -> DistanceMeasure:
        mapping = {
            Distance.cosine: DistanceMeasure.COSINE,
            Distance.l2: DistanceMeasure.EUCLIDEAN,
            Distance.max_inner_product: DistanceMeasure.DOT_PRODUCT,
        }
        return mapping[self.distance]

    def _normalize_embedding(self, embedding: Optional[Sequence[float]]) -> List[float]:
        if embedding is None:
            raise ValueError("Embedding cannot be None.")

        vector = Vector(embedding) #[float(value) for value in embedding]
        if len(vector) != self.dimensions:
            raise ValueError(
                f"Embedding dimensions mismatch. Expected {self.dimensions}, got {len(vector)}."
            )
        return vector

    def _document_id(self, document: Document) -> str:
        return document.id or hash_string_sha256(document.content)

    def _serialize_document(self, content_hash: str, document: Document) -> Dict[str, Any]:
        if not document.embedding:
            document.embed(self.embedder)

        embedding = self._normalize_embedding(document.embedding)
        document_id = self._document_id(document)

        payload: Dict[str, Any] = {
            self.id_field: document_id,
            self.content_field: document.content,
            self.vector_field: embedding,
            self.metadata_field: document.meta_data or {},
            self.content_hash_field: content_hash,
        }

        if document.name is not None:
            payload[self.name_field] = document.name
        if document.content_id is not None:
            payload[self.content_id_field] = document.content_id

        return payload

    def _to_document(self, doc_snapshot: Any) -> Document:
        data: Any | dict[Any, Any] = doc_snapshot.to_dict() or {}
        metadata = data.get(self.metadata_field) or {}

        document = Document(
            id=data.get(self.id_field) or getattr(doc_snapshot, "id", None),
            name=data.get(self.name_field),
            content=data.get(self.content_field, ""),
            meta_data=metadata,
            embedding=data.get(self.vector_field),
            content_id=data.get(self.content_id_field),
        )

        distance = getattr(doc_snapshot, "distance", None)
        if distance is not None:
            document.meta_data = {**document.meta_data, "distance": distance}
            if self.similarity_threshold is not None:
                similarity = max(0.0, 1.0 - float(distance))
                document.meta_data["similarity"] = similarity

        return document

    def _passes_similarity_threshold(self, document: Document) -> bool:
        if self.similarity_threshold is None:
            return True

        distance = document.meta_data.get("distance")
        if distance is None:
            return True

        similarity = document.meta_data.get("similarity")
        if similarity is None:
            similarity = max(0.0, 1.0 - float(distance))
            document.meta_data["similarity"] = similarity

        return similarity >= self.similarity_threshold

    def _stream_query(self, query: Any) -> List[Any]:
        return list(query.stream())

    def _get_snapshot(self, doc_ref: Any) -> Any:
        snapshot = doc_ref.get()
        if hasattr(snapshot, "__await__"):
            raise RuntimeError("Async Firestore document references are not supported by FirestoreVectorDb.")
        return snapshot

    def create(self) -> None:
        log_warning(
            "Firestore collections and vector indexes must be created in Firebase/Google Cloud configuration. "
            "No runtime create operation is performed."
            "gcloud firestore" 
                "indexes composite create --project=indiathon"
                "--collection-group={vector_field} --query-scope=COLLECTION"
                "--field-config=vector-config='{\"dimension\":\"1536\",\"flat\":"
                "\"{}\"}',field-path=embedding                            "
        )

    async def async_create(self) -> None:
        await asyncio.to_thread(self.create)

    def name_exists(self, name: str) -> bool:
        try:
            docs = self.collection.where(filter=
                            FieldFilter(self.name_field, "==", name)).limit(1).stream()
            return next(docs, None) is not None
        except Exception as exc:
            log_error(f"Error checking if name exists: {exc}")
            return False

    async def async_name_exists(self, name: str):  # type: ignore[override]
        return await asyncio.to_thread(self.name_exists, name)

    def id_exists(self, id: str) -> bool:
        try:
            snapshot = self._get_snapshot(self.collection.document(id))
            return bool(snapshot.exists)
        except Exception as exc:
            log_error(f"Error checking if ID exists: {exc}")
            return False

    def content_hash_exists(self, content_hash: str) -> bool:
        try:
            docs = self.collection.where(filter=FieldFilter(self.content_hash_field, "==", content_hash)).limit(1).stream()
            return next(docs, None) is not None
        except Exception as exc:
            log_error(f"Error checking if content hash exists: {exc}")
            return False

    def insert(
        self,
        content_hash: str,
        documents: List[Document],
        filters: Optional[Dict[str, Any]] = None,
    ) -> None:
        try:
            batch = self.db_client.batch()
            for document in documents:
                payload = self._serialize_document(content_hash, document)
                doc_ref = self.collection.document(payload[self.id_field])
                batch.set(doc_ref, payload)
            batch.commit()
            log_debug(f"Inserted {len(documents)} documents with content_hash: {content_hash}")
        except Exception as exc:
            log_error(f"Error inserting documents: {exc}")
            raise

    async def async_insert(
        self,
        content_hash: str,
        documents: List[Document],
        filters: Optional[Dict[str, Any]] = None,
    ) -> None:
        await asyncio.to_thread(self.insert, content_hash, documents, filters)

    def upsert_available(self) -> bool:
        return True

    def upsert(
        self,
        content_hash: str,
        documents: List[Document],
        filters: Optional[Dict[str, Any]] = None,
    ) -> None:
        try:
            self.delete_by_metadata({self.content_hash_field: content_hash})
            self.insert(content_hash, documents, filters)
        except Exception as exc:
            log_error(f"Error upserting documents: {exc}")
            raise

    async def async_upsert(
        self,
        content_hash: str,
        documents: List[Document],
        filters: Optional[Dict[str, Any]] = None,
    ) -> None:
        await asyncio.to_thread(self.upsert, content_hash, documents, filters)

    def search(
        self,
        query: str,
        limit: int = 5,
        filters: Optional[Any] = None,
    ) -> List[Document]:
        if filters and isinstance(filters, list):
            log_warning("Filter expressions are not supported in FirestoreVectorDb. No filters will be applied.")
            filters = None

        try:
            query_embedding = self._normalize_embedding(self.embedder.get_embedding(query))
            firestore_query = self.collection

            if filters:
                filter_dict = cast(Dict[str, Any], filters)
                for key, value in filter_dict.items():
                    firestore_query = firestore_query.where(filter=
                        FieldFilter(f"{self.metadata_field}.{key}", "==", value))

            nearest_query = firestore_query.find_nearest(
                vector_field=self.vector_field,
                query_vector=query_embedding,
                distance_measure=self._distance_measure(),
                limit=limit,
            )

            documents = [self._to_document(doc) for doc in self._stream_query(nearest_query)]
            documents = [doc for doc in documents if self._passes_similarity_threshold(doc)]

            if self.reranker:
                documents = self.reranker.rerank(query=query, documents=documents)

            return documents
        except Exception as exc:
            log_error(f"Error in search: {exc}")
            return []

    async def async_search(
        self,
        query: str,
        limit: int = 5,
        filters: Optional[Any] = None,
    ) -> List[Document]:
        return await asyncio.to_thread(self.search, query, limit, filters)

    def drop(self) -> None:
        try:
            self.delete()
        except Exception as exc:
            log_error(f"Error dropping collection documents: {exc}")
            raise

    async def async_drop(self) -> None:
        await asyncio.to_thread(self.drop)

    def exists(self) -> bool:
        try:
            docs = self.collection.limit(1).stream()
            return next(docs, None) is not None
        except Exception:
            return False

    async def async_exists(self) -> bool:
        return await asyncio.to_thread(self.exists)

    def optimize(self) -> None:
        log_debug("Firestore optimization not required")

    def delete(self) -> bool:
        try:
            docs = list(self.collection.stream())
            if not docs:
                return True

            batch = self.db_client.batch()
            for doc in docs:
                batch.delete(doc.reference)
            batch.commit()
            return True
        except Exception as exc:
            log_error(f"Error deleting documents: {exc}")
            return False

    def delete_by_id(self, id: str) -> bool:
        try:
            doc_ref = self.collection.document(id)
            snapshot = self._get_snapshot(doc_ref)
            if not snapshot.exists:
                return False
            doc_ref.delete()
            return True
        except Exception as exc:
            log_error(f"Error deleting document by ID: {exc}")
            return False

    def _delete_by_field(self, field_name: str, value: Any) -> int:
        docs = list(self.collection.where(filter=
                    FieldFilter(field_name, "==", value)).stream())
        if not docs:
            return 0

        batch = self.db_client.batch()
        for doc in docs:
            batch.delete(doc.reference)
        batch.commit()
        return len(docs)

    def delete_by_name(self, name: str) -> bool:
        try:
            return self._delete_by_field(self.name_field, name) > 0
        except Exception as exc:
            log_error(f"Error deleting documents by name: {exc}")
            return False

    def delete_by_metadata(self, metadata: Dict[str, Any]) -> bool:
        try:
            query = self.collection
            for key, value in metadata.items():
                query = query.where(filter=
                    FieldFilter(f"{self.metadata_field}.{key}", "==", value))

            docs = list(query.stream())
            if not docs:
                return False

            batch = self.db_client.batch()
            for doc in docs:
                batch.delete(doc.reference)
            batch.commit()
            return True
        except Exception as exc:
            log_error(f"Error deleting documents by metadata: {exc}")
            return False

    def update_metadata(self, content_id: str, metadata: Dict[str, Any]) -> None:
        try:
            docs = list(self.collection.where(filter=
                                            FieldFilter(self.content_id_field, "==", content_id)).stream())
            batch = self.db_client.batch()
            for doc in docs:
                current = doc.to_dict() or {}
                merged_metadata = {**(current.get(self.metadata_field) or {}), **metadata}
                batch.update(doc.reference, {self.metadata_field: merged_metadata})
            if docs:
                batch.commit()
        except Exception as exc:
            log_error(f"Error updating metadata: {exc}")
            raise

    def delete_by_content_id(self, content_id: str) -> bool:
        try:
            return self._delete_by_field(self.content_id_field, content_id) > 0
        except Exception as exc:
            log_error(f"Error deleting documents by content_id: {exc}")
            return False

    def get_supported_search_types(self) -> List[str]:
        return [SearchType.vector.value]

# Made with Bob
