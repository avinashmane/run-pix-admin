"""
Registry configuration for Agno agents.
"""
from agno.registry import Registry
from .lib import get_db


def create_registry():
    """
    Create and configure the Agno Registry with database.
    
    Returns:
        Registry: Configured Registry instance
    """
    db = get_db()
    
    registry = Registry(  id="pcmcrunners",
                                    models=get_model(),
                                    dbs=[db])
    
    return registry


# Create a singleton instance
registry = create_registry()

# Made with Bob
