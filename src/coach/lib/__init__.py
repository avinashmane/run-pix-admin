from .db import get_db
from .model import get_model
from .knowledge import get_kb, get_pinecone_vector_db

# List of all databases
dbs={ }

# List of all knowledgebases
knowledge_bases= {}

# List of all vector databases
def initialize_db() -> None:
    """
    Initializes the database by creating the required collections and indexes.  
    """

    dbs["firestore"] = get_db()

    knowledge_bases["test"] = get_kb( name="test", 
                    contents_db= dbs["firestore"] ,
                    vectordb_type = "firestore"
                )


__all__ = ["dbs", "get_db", "get_model", "get_kb", "initialize_db", "knowledge_bases"]

# Made with Bob
