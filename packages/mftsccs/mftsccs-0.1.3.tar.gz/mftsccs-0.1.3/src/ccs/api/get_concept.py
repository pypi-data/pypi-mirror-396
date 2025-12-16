"""
GetConcept API - Fetches a concept from the backend by ID.
"""

import aiohttp
from typing import Optional

from ccs.models.concept import Concept, create_default_concept
from ccs.config.base_url import BaseUrl
from ccs.config.token_storage import TokenStorage
from ccs.data.local_concept_data import LocalConceptsData
from ccs.api.http_client import post_with_retry, TokenRefreshError


async def GetConcept(id: int) -> Concept:
    """
    Fetches a concept from the backend API by its ID.

    This function first checks the local cache (LocalConceptsData). If the concept
    is not found locally, it makes an HTTP request to the backend API.

    **Process:**
    1. Returns empty concept if id is 0, None, or invalid
    2. Checks local cache first (LocalConceptsData)
    3. If not in cache, fetches from backend API
    4. Stores fetched concept in local cache for future use

    Args:
        id: The positive ID of the concept to fetch. Must be > 0.

    Returns:
        The Concept object if found, or a default empty Concept if not found.

    Example:
        >>> concept = await GetConcept(12345)
        >>> print(concept.characterValue)  # "Alice Smith"

    Note:
        This function only works with positive IDs (server concepts).
        For local concepts (negative IDs), use LocalConceptsData.GetConceptByGhostId()
    """
    result = create_default_concept()

    # Validate ID
    if id is None or id == 0:
        return result

    # Check local cache first
    cachedConcept = LocalConceptsData.GetConcept(id)
    if cachedConcept and cachedConcept.id != 0:
        return cachedConcept

    # Fetch from backend API
    try:
        url = BaseUrl.GetConceptUrl()
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }

        # Use form data like the JS version
        data = {"id": str(id)}

        # Use post_with_retry for automatic token refresh on 401
        response = await post_with_retry(url, headers=headers, data=data)

        if response.status == 200:
            json_data = await response.json()
            result = _parse_concept(json_data)

            # Add to local cache if valid
            if result.id > 0:
                LocalConceptsData.AddConcept(result)
        else:
            print(f"GetConcept error: HTTP {response.status}")

    except TokenRefreshError as e:
        print(f"GetConcept authentication error: {e}")
    except aiohttp.ClientError as e:
        print(f"GetConcept network error: {e}")
    except Exception as e:
        print(f"GetConcept unexpected error: {e}")

    return result


def _parse_concept(data: dict) -> Concept:
    """Parse a concept from JSON response data."""
    if not data or not isinstance(data, dict):
        return create_default_concept()

    try:
        concept = Concept(
            id=data.get("id", 0),
            userId=data.get("userId", 0),
            typeId=data.get("typeId", 0),
            categoryId=data.get("categoryId", 0),
            referentId=data.get("referentId", 0),
            characterValue=data.get("characterValue", ""),
            accessId=data.get("accessId", 4),
        )
        concept.typeCharacter = data.get("typeCharacter", "")
        concept.isComposition = data.get("isComposition", False)

        # Handle ghostId if present
        if "ghostId" in data:
            concept.ghostId = data["ghostId"]

        return concept

    except Exception as e:
        print(f"Error parsing concept: {e}")
        return create_default_concept()
