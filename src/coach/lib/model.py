import os

from agno.models.ollama import Ollama
from agno.models.google import Gemini
model_id = os.environ.get("AGNO_MODEL", "qwen3:1.7b")
print(f"MODEL={model_id}")


def get_model(id=model_id):
    m_id = id.split("/").pop()
    if id.startswith("google/"):
        return Gemini(id=m_id, model_id=id)

    else:
        return Ollama(id=m_id)