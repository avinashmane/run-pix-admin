import os
import logging
from agno.db.firestore import FirestoreDb

PROJECT_ID = os.environ.get("AGENT_PROJECT_ID", "agno-os-test")


def get_db():
    """
    Setup and return the Firestore database instance.
    
    Returns:
        FirestoreDb: Configured Firestore database instance
    """
    db = FirestoreDb(project_id=PROJECT_ID)
    logging.info(f"Setting firestore {PROJECT_ID}")
    return db

# Made with Bob
