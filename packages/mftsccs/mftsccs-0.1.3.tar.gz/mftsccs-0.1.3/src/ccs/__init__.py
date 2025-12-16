"""
CCS - A Python library for Concept-Connection System functionality.

This package provides utilities and functions for creating and managing
concepts in a knowledge graph system with offline-first support.

Usage:
    >>> from ccs import init, MakeTheInstanceConceptLocal, LocalTransaction
    >>>
    >>> async def main():
    ...     # Initialize the library first
    ...     await init(
    ...         url="https://api.freeschema.com",
    ...         accessToken="your-jwt-token"
    ...     )
    ...
    ...     # Use LocalTransaction for batch operations
    ...     tx = LocalTransaction()
    ...     await tx.initialize()
    ...
    ...     person = await tx.MakeTheInstanceConceptLocal(
    ...         type="the_person",
    ...         referent="",
    ...         composition=True,
    ...         userId=101
    ...     )
    ...     name = await tx.MakeTheInstanceConceptLocal(
    ...         type="the_name",
    ...         referent="Alice",
    ...         userId=101
    ...     )
    ...
    ...     # Sync all at once
    ...     await tx.commitTransaction()
"""

from ccs.core import example_function, ExampleClass
from ccs.utils import helper_function

# Initialization
from ccs.init import init, updateAccessToken, isInitialized, getConfig

# Configuration
from ccs.config import BaseUrl, TokenStorage, CCSConfig

# Models
from ccs.models import Concept, create_default_concept, Connection, create_default_connection

# Data storage
from ccs.data import (
    LocalConceptsData,
    LocalConnectionData,
    LocalSyncData,
    LocalId,
    InnerActions,
)

# Services - Local
from ccs.services.local import (
    CreateTheConceptLocal,
    MakeTheConceptLocal,
    MakeTheTypeConceptLocal,
    MakeTheInstanceConceptLocal,
    GetConceptByCharacterAndCategoryLocal,
    SplitStrings,
    # Connection functions
    CreateTheConnectionLocal,
    CreateConnection,
    CreateConnectionBetweenTwoConceptsLocal,
)

# Transaction support
from ccs.services.transaction import LocalTransaction

# Get services
from ccs.services.get import GetTheConcept, AddTypeConcept

# API
from ccs.api import (
    GetConcept,
    getOAuthToken,
    refreshOAuthToken,
    OAuthResponse,
    request_with_retry,
    post_with_retry,
    get_with_retry,
    TokenRefreshError
)

__version__ = "0.1.0"
__author__ = "Boomconsole"

__all__ = [
    "__version__",
    "__author__",
    # Initialization
    "init",
    "updateAccessToken",
    "isInitialized",
    "getConfig",
    # Configuration
    "BaseUrl",
    "TokenStorage",
    "CCSConfig",
    # Legacy
    "example_function",
    "ExampleClass",
    "helper_function",
    # Models
    "Concept",
    "create_default_concept",
    "Connection",
    "create_default_connection",
    # Data storage
    "LocalConceptsData",
    "LocalConnectionData",
    "LocalSyncData",
    "LocalId",
    "InnerActions",
    # Local services - Concepts
    "CreateTheConceptLocal",
    "MakeTheConceptLocal",
    "MakeTheTypeConceptLocal",
    "MakeTheInstanceConceptLocal",
    "GetConceptByCharacterAndCategoryLocal",
    "SplitStrings",
    # Local services - Connections
    "CreateTheConnectionLocal",
    "CreateConnection",
    "CreateConnectionBetweenTwoConceptsLocal",
    # Get services
    "GetTheConcept",
    "AddTypeConcept",
    # API
    "GetConcept",
    "getOAuthToken",
    "refreshOAuthToken",
    "OAuthResponse",
    "request_with_retry",
    "post_with_retry",
    "get_with_retry",
    "TokenRefreshError",
    # Transaction
    "LocalTransaction",
]
