from fastapi import FastAPI
from agno.os import AgentOS
from .lib import get_db
from .lib import get_model
from .agents import get_basic_agent
from .studio import registry

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

    # Setup the Firestore database
    db = get_db()

    # Setup agents
    basic_agent = get_basic_agent(db)

    # Create AgentOS
    agent_os = AgentOS(
        agents=[basic_agent],
        registry=registry,
        base_app=app  # Your custom FastAPI app
    )
    
    return agent_os.get_app()

# Made with Bob
