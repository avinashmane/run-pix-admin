from fastapi import FastAPI
from .lib import initialize_db

# Setup AgentOS with all configurations

def mount_coach(app=None):
    """
    Mount coach agents.
    
    Args:
        app: Optional FastAPI app to mount on
        
    Returns:
        FastAPI app with agents mounted
    """
    # Create a second, independent FastAPI sub-application
    if app is None:
        app = FastAPI(title="API v1", description="Version 1 of the API")

    # Initialize database before importing AgentOS/agents so registries are populated
    initialize_db()

    # Import after initialization to avoid creating agents before db/knowledge setup
    from .agent_os import setup_agent_os

    # Setup AgentOS with all configurations
    agent_os = setup_agent_os(app)
    
    return agent_os.get_app()

# Made with Bob
