from typing import Any
import os
import logging
from agno.db.firestore import FirestoreDb
from google.cloud.firestore import Client
from google.oauth2 import service_account
import json




def get_db():
    """
    Setup and return the Firestore database instance.
    
    Returns:
        FirestoreDb: Configured Firestore database instance
    """
    try:
        # collections= {x : f"ag_{x.split("_")[0]}"
        #                                 for x in ["session_collection",
        #                                 "memory_collection",
        #                                 "metrics_collection",
        #                                 "eval_collection",
        #                                 "knowledge_collection",
        #                                 "culture_collection",
        #                                 "traces_collection",
        #                                 "spans_collection",]}
        
        # Add component_collection for agent storage
        # collections["component_collection"] = "ag_component"
        # collections["config_collection"] = "ag_config"
        
        db = FirestoreDb( db_client=get_firestore_client(),
        #    **collections,
           )
        # logging.info(f"Setting firestore {PROJECT_ID} with collections: {collections}")
        return db
    except Exception as e:
        logging.error(f"Error initializing Firestore database: {e}")
        raise

def get_firestore_client():
    """
    Setup and return the Firestore client instance.
    """
    PROJECT_ID = os.getenv("AGENT_PROJECT_ID", "agno-os-test")
    SERVICE_ACCOUNT = json.loads(os.environ['SERVICE_ACCOUNT'])
    credentials = service_account.Credentials.from_service_account_info(SERVICE_ACCOUNT)
    return Client(project= PROJECT_ID, credentials=credentials)
# Made with Bob
