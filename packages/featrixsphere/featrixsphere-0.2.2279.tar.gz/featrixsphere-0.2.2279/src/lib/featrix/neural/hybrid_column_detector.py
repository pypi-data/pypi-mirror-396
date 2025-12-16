#  -*- coding: utf-8 -*-
#
#  Copyright Featrix, Inc 2023-2025
#
#  Proprietary and Confidential.  Unauthorized use, copying or dissemination
#  of these materials is strictly prohibited.
#
"""
Hybrid Column Detector

Detects semantically related columns that should be encoded together or with 
relationship awareness. Supports two strategies:

1. MERGE: Columns are combined into a single composite encoder 
   (e.g., address components → AddressHybridEncoder)
   
2. RELATIONSHIP: Columns stay separate but JointEncoder is made aware of relationships
   (e.g., customer_name, customer_id, customer_type → marked as related)
"""
import hashlib
import json
import logging
import os
import sqlite3
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import pandas as pd

logger = logging.getLogger(__name__)

# Get Featrix root directory (firmware: /sphere, development: ~/sphere-workspace)
# Avoid importing platform_utils to keep this module torch-independent
def _get_featrix_root():
    """Get Featrix root directory without importing platform_utils."""
    # Check if we're on firmware (sphere server)
    if Path("/sphere/app").exists():
        return "/sphere"
    # Check environment variable
    root = os.environ.get("FEATRIX_ROOT")
    if root:
        return root
    # Default fallback
    return str(Path.home() / "sphere-workspace")

FEATRIX_ROOT = _get_featrix_root()

# Cache for LLM schema analysis results
HYBRID_COLUMN_CACHE_DIR = Path(FEATRIX_ROOT) / "app" / "featrix_hybrid_column_cache"
HYBRID_COLUMN_CACHE_FILE = HYBRID_COLUMN_CACHE_DIR / "llm_analysis.db"


class HybridColumnCache:
    """SQLite cache for LLM schema analysis results."""
    
    def __init__(self, cache_file: Path = HYBRID_COLUMN_CACHE_FILE):
        self.cache_file = cache_file
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        
        self.conn = sqlite3.connect(str(self.cache_file))
        self.cursor = self.conn.cursor()
        
        # Create cache table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS llm_analysis_cache (
                cache_key TEXT PRIMARY KEY,
                analysis_result TEXT NOT NULL,
                created_at REAL NOT NULL,
                column_count INTEGER NOT NULL
            )
        """)
        self.conn.commit()
    
    def _make_cache_key(self, columns: List[str], col_types: Dict[str, str], sample_hash: str) -> str:
        """Generate deterministic cache key from schema."""
        # Sort columns for consistency
        sorted_cols = sorted(columns)
        schema_repr = json.dumps({
            "columns": sorted_cols,
            "types": {col: col_types.get(col, "unknown") for col in sorted_cols},
            "sample_hash": sample_hash
        }, sort_keys=True)
        return hashlib.sha256(schema_repr.encode()).hexdigest()
    
    def get(self, columns: List[str], col_types: Dict[str, str], sample_hash: str) -> Optional[Dict]:
        """Get cached analysis result."""
        cache_key = self._make_cache_key(columns, col_types, sample_hash)
        
        self.cursor.execute(
            "SELECT analysis_result FROM llm_analysis_cache WHERE cache_key = ?",
            (cache_key,)
        )
        row = self.cursor.fetchone()
        
        if row:
            logger.info(f"✅ Hybrid column detection: cache hit (key={cache_key[:16]}...)")
            return json.loads(row[0])
        return None
    
    def set(self, columns: List[str], col_types: Dict[str, str], sample_hash: str, result: Dict):
        """Cache analysis result."""
        cache_key = self._make_cache_key(columns, col_types, sample_hash)
        
        self.cursor.execute(
            """
            INSERT OR REPLACE INTO llm_analysis_cache 
            (cache_key, analysis_result, created_at, column_count)
            VALUES (?, ?, ?, ?)
            """,
            (cache_key, json.dumps(result), time.time(), len(columns))
        )
        self.conn.commit()
        logger.info(f"💾 Cached hybrid column analysis (key={cache_key[:16]}..., groups={len(result.get('groups', []))})")


class HybridColumnDetector:
    """
    Detects semantically related columns that should be encoded together.
    
    Supports two encoding strategies:
    1. MERGE: Combine columns into single composite encoder (addresses, coordinates)
    2. RELATIONSHIP: Keep separate but add relationship awareness (entity attributes)
    """
    
    def __init__(self, use_llm: bool = False, cache: Optional[HybridColumnCache] = None):
        self.use_llm = use_llm
        self.cache = cache or HybridColumnCache()
    
    def detect(self, df: pd.DataFrame, col_types: Dict[str, str]) -> Dict[str, Dict]:
        """
        Detect hybrid column groups in a DataFrame.
        
        Args:
            df: DataFrame with data
            col_types: Dictionary mapping column names to types ("set", "scalar", etc.)
            
        Returns:
            Dictionary of detected groups:
            {
                "hybrid_group_1": {
                    "type": "address",
                    "columns": ["shipping_addr1", "shipping_city", "shipping_state"],
                    "prefix": "shipping",
                    "strategy": "merge",  # or "relationship"
                    "confidence": 1.0,
                    "reasoning": "..."
                },
                "hybrid_group_2": {
                    "type": "entity",
                    "columns": ["customer_name", "customer_id", "customer_type"],
                    "prefix": "customer",
                    "strategy": "relationship",
                    "confidence": 0.95,
                    "reasoning": "..."
                }
            }
        """
        # Try pattern-based detection first (fast)
        pattern_groups = self._detect_with_patterns(list(df.columns), col_types)
        
        if not self.use_llm:
            return pattern_groups
        
        # Use LLM to find additional relationships
        logger.info("🤖 Running LLM analysis for hybrid column detection...")
        llm_groups = self._detect_with_llm(df, col_types)
        
        # Merge results (pattern takes precedence)
        combined_groups = {**llm_groups, **pattern_groups}
        
        return combined_groups
    
    def _detect_with_patterns(self, columns: List[str], col_types: Dict[str, str]) -> Dict[str, Dict]:
        """Fast pattern-based detection."""
        detected_groups = {}
        group_counter = 1
        used_columns = set()
        
        # Detect address patterns (MERGE strategy)
        address_groups = self._detect_address_patterns(columns)
        for group_info in address_groups:
            if any(col in used_columns for col in group_info["columns"]):
                continue
            group_name = f"hybrid_group_{group_counter}"
            detected_groups[group_name] = {
                **group_info,
                "strategy": "merge",
                "confidence": 1.0,
                "reasoning": "Pattern match: address components with common prefix"
            }
            used_columns.update(group_info["columns"])
            group_counter += 1
        
        # Detect coordinate patterns (MERGE strategy)
        coord_groups = self._detect_coordinate_patterns(columns)
        for group_info in coord_groups:
            if any(col in used_columns for col in group_info["columns"]):
                continue
            group_name = f"hybrid_group_{group_counter}"
            detected_groups[group_name] = {
                **group_info,
                "strategy": "merge",
                "confidence": 1.0,
                "reasoning": "Pattern match: latitude/longitude pair"
            }
            used_columns.update(group_info["columns"])
            group_counter += 1
        
        # Detect common-prefix entity groups (RELATIONSHIP strategy)
        entity_groups = self._detect_entity_patterns(columns, col_types, used_columns)
        for group_info in entity_groups:
            if any(col in used_columns for col in group_info["columns"]):
                continue
            group_name = f"hybrid_group_{group_counter}"
            detected_groups[group_name] = {
                **group_info,
                "strategy": "relationship",
                "confidence": 0.9,
                "reasoning": f"Pattern match: multiple attributes with common prefix '{group_info['prefix']}'"
            }
            used_columns.update(group_info["columns"])
            group_counter += 1
        
        if detected_groups:
            logger.info(f"🔍 Pattern detection found {len(detected_groups)} hybrid groups")
            for group_name, group_info in detected_groups.items():
                logger.info(f"   {group_name}: {group_info['type']} ({group_info['strategy']}) - {group_info['columns']}")
        
        return detected_groups
    
    def _detect_address_patterns(self, columns: List[str]) -> List[Dict]:
        """Detect address component patterns."""
        groups = []
        
        # Find all prefixes
        address_suffixes = ["addr1", "addr2", "address", "street", "city", "state", "zip", "postal_code", "country"]
        prefixes = set()
        
        for col in columns:
            col_lower = col.lower()
            for suffix in address_suffixes:
                if suffix in col_lower:
                    # Extract prefix (everything before the suffix)
                    idx = col_lower.find(suffix)
                    if idx > 0:
                        prefix = col[:idx].rstrip("_").rstrip("-")
                        if prefix:
                            prefixes.add(prefix)
        
        # For each prefix, find matching address columns
        for prefix in prefixes:
            prefix_lower = prefix.lower()
            matching_cols = []
            
            for col in columns:
                col_lower = col.lower()
                if col_lower.startswith(prefix_lower):
                    # Check if it has an address-like suffix
                    for suffix in address_suffixes:
                        if suffix in col_lower:
                            matching_cols.append(col)
                            break
            
            # Need at least 2 columns to form an address group
            if len(matching_cols) >= 2:
                groups.append({
                    "type": "address",
                    "columns": sorted(matching_cols),  # Sort for consistency
                    "prefix": prefix
                })
        
        return groups
    
    def _detect_coordinate_patterns(self, columns: List[str]) -> List[Dict]:
        """Detect lat/long coordinate pairs."""
        groups = []
        used_cols = set()
        
        for col in columns:
            if col in used_cols:
                continue
            
            col_lower = col.lower()
            
            # Check if this is a latitude column
            if "lat" in col_lower and "latitude" not in col_lower:
                # Look for corresponding longitude
                prefix = col_lower.replace("lat", "").rstrip("_").rstrip("-")
                long_candidates = [
                    col.replace("lat", "long"),
                    col.replace("lat", "lon"),
                    col.replace("lat", "lng"),
                    col.replace("Lat", "Long"),
                    col.replace("Lat", "Lon"),
                ]
                
                for long_col in long_candidates:
                    # CRITICAL: Skip if replacement didn't change the column name (no match found)
                    # This prevents matching a column to itself when case-sensitive replace fails
                    if long_col != col and long_col in columns:
                        groups.append({
                            "type": "coordinates",
                            "columns": [col, long_col],
                            "prefix": prefix if prefix else "location"
                        })
                        used_cols.add(col)
                        used_cols.add(long_col)
                        break
            
            elif "latitude" in col_lower:
                # Look for longitude
                prefix = col_lower.replace("latitude", "").rstrip("_").rstrip("-")
                long_col = col.replace("latitude", "longitude").replace("Latitude", "Longitude")
                # CRITICAL: Skip if replacement didn't change the column name
                if long_col != col and long_col in columns:
                    groups.append({
                        "type": "coordinates",
                        "columns": [col, long_col],
                        "prefix": prefix if prefix else "location"
                    })
                    used_cols.add(col)
                    used_cols.add(long_col)
        
        return groups
    
    def _detect_entity_patterns(self, columns: List[str], col_types: Dict[str, str], 
                               used_columns: set) -> List[Dict]:
        """
        Detect entity attribute patterns (same prefix, multiple attributes, different types).
        These use RELATIONSHIP strategy (keep separate, mark as related).
        """
        groups = []
        
        # Find all prefixes (at least 3 chars, followed by underscore)
        prefix_to_cols = {}
        for col in columns:
            if col in used_columns:
                continue
            
            # Look for underscore-separated prefix
            if "_" in col:
                parts = col.split("_")
                if len(parts) >= 2:
                    prefix = parts[0]
                    if len(prefix) >= 3:  # Reasonable prefix length
                        if prefix not in prefix_to_cols:
                            prefix_to_cols[prefix] = []
                        prefix_to_cols[prefix].append(col)
        
        # Find prefixes with 3+ columns and mixed types
        for prefix, cols in prefix_to_cols.items():
            if len(cols) < 3:
                continue
            
            # Check if columns have different types (good indicator of entity attributes)
            types_in_group = set()
            for col in cols:
                col_type = col_types.get(col, "unknown")
                types_in_group.add(col_type)
            
            # Require at least 2 different types
            if len(types_in_group) >= 2:
                groups.append({
                    "type": "entity",
                    "columns": sorted(cols),
                    "prefix": prefix
                })
        
        return groups
    
    def _detect_with_llm(self, df: pd.DataFrame, col_types: Dict[str, str]) -> Dict[str, Dict]:
        """
        LLM-based semantic detection with caching.
        
        Calls cache.featrix.com API via llm.schema_analyzer module.
        """
        # Hash sample data for cache key
        sample_data = df.head(5).to_dict(orient="records")
        sample_hash = hashlib.md5(json.dumps(sample_data, sort_keys=True, default=str).encode()).hexdigest()
        
        # Check cache
        cached_result = self.cache.get(list(df.columns), col_types, sample_hash)
        if cached_result:
            logger.info("✅ Using cached LLM analysis result")
            return self._format_llm_response(cached_result)
        
        # Call LLM API via schema_analyzer module
        logger.info(f"🤖 Calling LLM API (cache.featrix.com) for hybrid column detection...")
        logger.info(f"   Analyzing {len(df.columns)} columns")
        from featrix.neural.llm.schema_analyzer import detect_hybrid_columns
        
        llm_result = detect_hybrid_columns(list(df.columns), col_types)
        logger.info(f"✅ LLM API returned {len(llm_result.get('groups', []))} groups")
        
        # Deduplicate columns in each group (LLM sometimes returns duplicates)
        if llm_result and 'groups' in llm_result:
            groups_to_keep = []
            for i, group_info in enumerate(llm_result['groups']):
                # Skip non-dict entries (shouldn't happen, but be defensive)
                if not isinstance(group_info, dict):
                    logger.warning(f"⚠️  Skipping non-dict group at index {i}: {type(group_info)}")
                    continue
                
                if 'columns' in group_info:
                    original_cols = group_info['columns']
                    unique_cols = []
                    seen = set()
                    for col in original_cols:
                        if col not in seen:
                            unique_cols.append(col)
                            seen.add(col)
                    
                    if len(unique_cols) != len(original_cols):
                        group_name = group_info.get('prefix', f'group_{i}')
                        logger.warning(f"⚠️  {group_name}: Removed {len(original_cols) - len(unique_cols)} duplicate column(s)")
                        logger.warning(f"   Original: {original_cols}")
                        logger.warning(f"   Cleaned:  {unique_cols}")
                        group_info['columns'] = unique_cols
                    
                    # Skip groups with only 1 column after deduplication
                    if len(unique_cols) < 2:
                        group_name = group_info.get('prefix', f'group_{i}')
                        logger.warning(f"⚠️  {group_name}: Skipping - only {len(unique_cols)} unique column(s) after deduplication")
                    else:
                        groups_to_keep.append(group_info)
                else:
                    # No columns field, keep as-is
                    groups_to_keep.append(group_info)
            
            # Update the groups list with only valid groups
            llm_result['groups'] = groups_to_keep
        
        # Cache the result if we got groups
        if llm_result.get('groups'):
            self.cache.set(list(df.columns), col_types, sample_hash, llm_result)
        
        return self._format_llm_response(llm_result)
    
    def _format_llm_response(self, llm_result: Dict) -> Dict[str, Dict]:
        """Format LLM response into hybrid groups dict."""
        groups = {}
        
        for i, group_info in enumerate(llm_result.get("groups", []), 1):
            if group_info.get("confidence", 0) < 0.7:
                continue
            
            group_name = f"llm_group_{i}"
            group_type = group_info["type"]
            
            # Determine strategy based on type
            if group_type in ["address", "coordinates"]:
                strategy = "merge"
            else:
                strategy = "relationship"
            
            groups[group_name] = {
                "type": group_type,
                "columns": group_info["columns"],
                "prefix": group_info.get("prefix", f"group_{i}"),
                "strategy": strategy,
                "confidence": group_info["confidence"],
                "reasoning": group_info.get("reasoning", "LLM analysis")
            }
        
        return groups

