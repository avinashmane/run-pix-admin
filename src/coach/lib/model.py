import os

from agno.models.ollama import Ollama
from agno.models.google import Gemini

# Flag to track if model has been printed
_model_printed = False

def get_model(id=None):
    global _model_printed
    
    model_id = id if id else os.getenv("AGNO_MODEL", "gemini-2.5-pro")
    
    if not _model_printed:
        print(f"MODEL={model_id}")
        _model_printed = True


    m_id = model_id.split("/").pop()

    if model_id.startswith("google/") or model_id.startswith("gemini"):
        return Gemini(id=m_id)
    else:
        return Ollama(id=m_id)