# gapi package initializer - exposes GAPI, DrvDocument and Template and creates a module-level gapi instance
from .drive import GAPI

# create the global gapi instance (behaviour preserved from old code)
# Note: this will attempt to read SERVICE_ACCOUNT from environment when package is imported
gapi = GAPI()

# import document classes lazily to avoid circular imports during package import
from .document import DrvDocument, Template

__all__ = ["GAPI", "gapi", "DrvDocument", "Template"]
