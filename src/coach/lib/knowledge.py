
from agno.knowledge.knowledge  import Knowledge
from agno.vectordb.pineconedb import PineconeDb
import os

from httpx import get

from coach.lib.db import get_firestore_client


def get_pinecone_vector_db(name: str, 
    embedder=None
    ) -> PineconeDb:
    """
    Create and configure a Pinecone vector database.
    
    Args:
        name: Index name for the Pinecone database
        embedder: Embedder instance to use for the vector database
        
    Returns:
        Configured PineconeDb instance
    """
    api_key: str | None = os.getenv("PINECONE_API_KEY")
    index_name = name #"thai-recipe-hybrid-search"
    embedder=embedder if embedder else get_embedder()
    # print("PINECONE_API_KEY: ",api_key)
    vector_db = PineconeDb(
        name= index_name,
        dimension= 1536,
        metric="cosine",
        spec={"serverless": {"cloud": "aws", "region": "us-east-1"}},
        api_key=api_key,
        use_hybrid_search=True,
        hybrid_alpha=0.5,
        embedder=embedder # Or any Agno embedder
    )
    return vector_db


def get_kb(name="knowledge-base", vectordb_type=None, contents_db=None):

    embedder=get_embedder()
    if vectordb_type=="firestore":

        # Define your custom knowledge base
        from .firestore_vectordb import FirestoreVectorDb
        vector_db = FirestoreVectorDb(
            db_client=get_firestore_client(),
            collection_name="vectors",
            embedder=embedder # Or any Agno embedder
        )
        knowledge_base = Knowledge(
            name=name,
            vector_db=vector_db,
            contents_db=contents_db
        )
    else:
        vector_db = get_pinecone_vector_db(name, embedder)

        knowledge_base = Knowledge(
            name=name,
            vector_db=vector_db,
            contents_db=contents_db
        )

    return knowledge_base

def get_embedder(dimensions=1536    ):

     EMBEDDER=os.getenv("AGNO_EMBEDDER","")

     embedding_model="/".join(EMBEDDER.split("/")[1:]) if EMBEDDER else None
     
     if EMBEDDER.startswith("ollama"):
        from agno.knowledge.embedder.ollama import OllamaEmbedder
        return OllamaEmbedder(dimensions=dimensions,id=embedding_model)
     else:
        from agno.knowledge.embedder.google import GeminiEmbedder
        return GeminiEmbedder(dimensions=dimensions,id=embedding_model)
    
