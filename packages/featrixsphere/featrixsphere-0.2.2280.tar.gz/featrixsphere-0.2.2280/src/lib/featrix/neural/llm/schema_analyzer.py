#!/usr/bin/env python3
"""
LLM-based schema analysis using cache.featrix.com API.

Provides functions to query the LLM API for semantic column analysis,
including hybrid column detection, data type inference, and more.

Zero neural dependencies - only uses requests for HTTP calls.
"""

import json
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


def detect_hybrid_columns(columns: List[str], col_types: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """
    Ask LLM to detect hybrid column groups in a schema.
    
    Args:
        columns: List of column names to analyze
        col_types: Optional dict of column types (for context)
    
    Returns:
        Dict with 'groups' array containing detected hybrid groups
        Each group has: type, columns, prefix, confidence, reasoning
    
    Example:
        >>> result = detect_hybrid_columns(["shipping_addr", "shipping_city", "shipping_state"])
        >>> groups = result.get('groups', [])
        >>> print(f"Found {len(groups)} hybrid groups")
    """
    try:
        import requests
    except ImportError:
        logger.error("requests library not available - cannot call cache.featrix.com API")
        return {"groups": []}
    
    api_url = "https://cache.featrix.com/query-schema"
    
    # Build detailed prompt
    question = (
        "You are given the column names of a tabular dataset. "
        "Analyze the columns and identify SMALL GROUPS of semantically related columns "
        "that should be encoded or modeled together (i.e., they describe different aspects "
        "of the same underlying thing).\n\n"
        "Specifically look for (but do not limit yourself to):\n"
        "  1) Address components (e.g. street, city, state, zip, country)\n"
        "  2) Coordinate pairs or sets (e.g. latitude/longitude)\n"
        "  3) Entity attributes (e.g. customer_name, customer_id, customer_type, account_status)\n"
        "  4) Temporal ranges or pairs (e.g. start_date, end_date; created_at, updated_at)\n\n"
        "Rules:\n"
        "  - Only group columns that clearly refer to the SAME entity/concept.\n"
        "  - Each group must have at least 2 columns.\n"
        "  - Do NOT invent new column names; use only the ones provided.\n"
        "  - 'type' should be one of: 'address', 'coordinates', 'entity_attributes', "
        "'temporal_range', or 'other'.\n"
        "  - 'prefix' should be a short, descriptive base name for the group "
        "(often the shared prefix of the columns, if meaningful).\n"
        "  - 'confidence' is a number from 0.0 to 1.0.\n"
        "  - 'reasoning' should be a short sentence explaining why these columns belong together.\n\n"
        "Return ONLY a valid JSON object with a single key 'groups', where 'groups' is an array. "
        "Each group must be an object with keys: type, columns (list of strings), prefix, "
        "confidence, reasoning."
    )
    
    payload = {
        "columns": columns,
        "question": question
    }
    
    logger.info(f"🤖 Calling cache.featrix.com for hybrid column detection ({len(columns)} columns)")
    logger.info(f"   API endpoint: {api_url}")
    logger.info(f"   Timeout: 10s (reduced from 30s for faster failure detection)")
    logger.info(f"   Payload size: {len(json.dumps(payload))} bytes")
    
    try:
        import time
        start_time = time.time()
        logger.info(f"   📡 Sending POST request now...")
        response = requests.post(api_url, json=payload, timeout=10)
        elapsed = time.time() - start_time
        
        logger.info(f"   ✅ Request completed in {elapsed:.2f}s")
        logger.info(f"   API response: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            num_groups = len(result.get('groups', []))
            logger.info(f"✅ LLM analysis complete: found {num_groups} hybrid groups")
            return result
        else:
            logger.warning(f"⚠️  API returned {response.status_code}: {response.text[:200]}")
            logger.warning(f"   Falling back to pattern-based detection only")
            return {"groups": []}
            
    except requests.exceptions.Timeout:
        logger.warning("⚠️  API request timeout (10s) - service may be down")
        logger.warning("   Falling back to pattern-based detection only")
        return {"groups": []}
        
    except requests.exceptions.ConnectionError as e:
        logger.warning(f"⚠️  API connection error: {e}")
        return {"groups": []}
        
    except Exception as e:
        logger.warning(f"⚠️  API call failed: {e}")
        return {"groups": []}


def test_api():
    """Test the API with sample data."""
    test_columns = [
        "shipping_address",
        "shipping_city", 
        "shipping_state",
        "shipping_zip",
        "warehouse_latitude",
        "warehouse_longitude",
        "customer_name",
        "customer_id",
        "customer_type",
        "order_start_date",
        "order_end_date",
        "revenue",
        "quantity",
        "status"
    ]
    
    print("Testing cache.featrix.com API...")
    result = detect_hybrid_columns(test_columns)
    
    print(json.dumps(result, indent=2))
    print(f"\nDetected {len(result.get('groups', []))} groups")


if __name__ == "__main__":
    # Enable logging for standalone test
    logging.basicConfig(level=logging.INFO)
    test_api()

