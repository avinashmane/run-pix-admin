from agno.agent import Agent
from agno.tools.website import WebsiteTools
from agno.tools.duckduckgo import DuckDuckGoTools
from coach.lib import get_model, dbs, knowledge_bases
from agno.tools.knowledge import KnowledgeTools

def get_basic_agent():
    """
    Create and return the basic agent configuration.
        
    Returns:
        Agent: Configured basic agent
    """

    kb = knowledge_bases["test"]

    basic_agent = Agent(
        id="basic-agent",
        model=get_model(),
        db=dbs["firestore"],
        knowledge=kb,
        tools=[ 
            WebsiteTools(), 
            KnowledgeTools(kb,),
            # DuckDuckGoTools()
            ],
        add_history_to_context=True,
    )
    
    return basic_agent

# Made with Bob
