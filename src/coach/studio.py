"""
Registry configuration for Agno agents.
"""
from agno.registry import Registry
from .lib import dbs, get_model, get_pinecone_vector_db

def add_tool(a,b):
    return a+b

def create_registry():
    """
    Create and configure the Agno Registry with database.
    
    Returns:
        Registry: Configured Registry instance
    """
    db = dbs["firestore"]

    registry = Registry(  id="pcmcrunners",
                            models=[get_model()],
                            tools=[add_tool],
                            vector_dbs=[get_pinecone_vector_db("test")],
                            dbs=[db])
    
    return registry


# Create a singleton instance
registry = create_registry()

# Made with Bob
