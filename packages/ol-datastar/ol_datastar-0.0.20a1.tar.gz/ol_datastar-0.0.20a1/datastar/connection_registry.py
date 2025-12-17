"""
Helper mapping type as string to Connection subclasses
"""

from typing import Dict, Any

from .connections.delimited_connection import DelimitedConnection
from .connections.frog_model_connection import FrogModelConnection
from .connections.opti_connection import OptiConnection

# Note: This supports constructing the correct Connection subclass based on API response
CONNECTION_TYPE_MAP: Dict[str, Any] = {
    "dsv": DelimitedConnection,
    "optidb": OptiConnection,
    "cosmicfrog": FrogModelConnection,
}


def _get_connection_class(conn_type: str):
    return CONNECTION_TYPE_MAP[conn_type]
