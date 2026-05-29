from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.duckduckgo import DuckDuckGoTools


def get_basic_agent(db):
    """
    Create and return the basic agent configuration.
    
    Args:
        db: Firestore database instance
        
    Returns:
        Agent: Configured basic agent
    """
    basic_agent = Agent(
        id="basic-agent",
        model=Gemini(id="gemini-2.5-pro"),
        db=db,
        tools=[DuckDuckGoTools()],
        add_history_to_context=True,
    )
    
    return basic_agent

# Made with Bob
