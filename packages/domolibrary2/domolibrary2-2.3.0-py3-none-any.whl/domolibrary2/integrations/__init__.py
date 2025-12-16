# Integrations module - automatically imports all integration modules
# Users can import integrations like: from domolibrary2.integrations import Automation

# Import all integration modules
from . import Automation, RoleHierarchy, auth_utils, mermaid, shortcut_fn
from .auth_utils import get_auth_from_codeengine
from .DeployAccount import DeployAccount
from .mermaid import MermaidDiagram, MermaidNode, MermaidRelationship

# Define what gets imported with "from domolibrary2.integrations import *"
__all__ = [
    "Automation",
    "RoleHierarchy",
    "shortcut_fn",
    "auth_utils",
    "mermaid",
    "get_auth_from_codeengine",
    "MermaidDiagram",
    "MermaidNode",
    "MermaidRelationship",
    "DeployAccount",
]
