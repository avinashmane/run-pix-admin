from fastapi import FastAPI
from agno.agent import Agent
from agno.models.google import Gemini
from agno.os import AgentOS
from agno.db.firestore import FirestoreDb
import os, logging
from agno.tools.duckduckgo import DuckDuckGoTools

PROJECT_ID = os.environ.get("AGENT_PROJECT_ID","agno-os-test" )

def mount_coach(app=None):
    # Pass your app to AgentOS
    # Create a second, independent FastAPI sub-application
    if app==None:
        app = FastAPI(title="API v1", description="Version 1 of the API")

    # Setup the Firestore database

    db = FirestoreDb(project_id=PROJECT_ID)
    logging.info(f"Setting firestore {PROJECT_ID}")

    basic_agent=Agent(  id="basic-agent", model=Gemini(id="gemini-2.5-pro"),
                        db=db,
                        tools=[DuckDuckGoTools()],
                        add_history_to_context=True,)
    
    agent_os = AgentOS(
        agents=[basic_agent],
        # base_app=app  # Your custom FastAPI app
    )
    

    # # Get the combined app with both AgentOS and your routes
    return agent_os.get_app()