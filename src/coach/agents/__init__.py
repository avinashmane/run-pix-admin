from .basic_agent import get_basic_agent
from agno.team import Team
from coach.lib import get_model

# Initialize agents and teams immediately on import
agents = {
    "basic_agent": get_basic_agent()
}
    
teams = {
    "basic_team": Team(
        id='fitness-coach',
        model=get_model(),
        members=[agents["basic_agent"]],
        name='Fitness Coach'
    )
}

__all__ = ["agents", "teams"]

# Made with Bob
