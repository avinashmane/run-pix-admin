from fastapi import FastAPI
from agno.os import AgentOS
from .lib import dbs, knowledge_bases

from .agents import agents, teams
# from .studio import registry


def setup_agent_os(app: FastAPI) -> AgentOS:
    """
    Setup and configure AgentOS with agents, knowledge base, and database.
    
    Args:
        app: FastAPI app to mount AgentOS on
        
    Returns:
        Configured AgentOS instance
    """
    import logging
    
    try:
        # Setup the Firestore database
        db = dbs["firestore"]
        logging.info(f"Database initialized: {db}")

        logging.info(f"Knowledge bases: {knowledge_bases}")

        # Create AgentOS
        agent_os = AgentOS(
            name="PCMCRunners coach",
            description="Coach for PCMCRunners",
            agents= [agents["basic_agent"]],
            teams=list(teams.values()),
            # registry= registry,
            knowledge= list(knowledge_bases.values()),
            a2a_interface=False,
            db=db,
            base_app=app  # Your custom FastAPI app
        )
        
        logging.info("AgentOS setup completed successfully")
        return agent_os
    except Exception as e:
        logging.error(f"Error setting up AgentOS: {e}", exc_info=True)
        raise

# Made with Bob
