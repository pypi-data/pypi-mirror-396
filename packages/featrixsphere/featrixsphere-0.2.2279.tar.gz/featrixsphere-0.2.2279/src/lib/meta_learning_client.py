"""
Meta-Learning Client

Client for logging training metadata and querying optimal parameters
from the central sphere-api meta-learning database.
"""
import hashlib
import json
import logging
import requests
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

# Central meta-learning API endpoint
META_API_URL = "https://sphere-api.featrix.com/meta"


def get_dataset_characteristics(df) -> Dict[str, Any]:
    """
    Extract dataset characteristics for meta-learning.
    
    Args:
        df: pandas DataFrame
        
    Returns:
        Dict with dataset characteristics
    """
    import pandas as pd
    import numpy as np
    
    # Column type analysis
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    
    # Text columns (strings with avg length > 20)
    text_cols = []
    for col in categorical_cols:
        if df[col].dtype == 'object':
            avg_len = df[col].astype(str).str.len().mean()
            if avg_len > 20:
                text_cols.append(col)
    
    # Remove text cols from categorical
    categorical_cols = [c for c in categorical_cols if c not in text_cols]
    
    # Cardinality analysis (for categorical columns)
    if categorical_cols:
        cardinalities = [df[col].nunique() for col in categorical_cols]
        avg_cardinality = np.mean(cardinalities)
        max_cardinality = max(cardinalities)
    else:
        avg_cardinality = 0
        max_cardinality = 0
    
    # Target analysis (assume last column or 'target')
    target_col = 'target' if 'target' in df.columns else df.columns[-1]
    target_cardinality = df[target_col].nunique()
    
    if target_cardinality == 2:
        target_type = 'binary_classification'
        # Class imbalance
        value_counts = df[target_col].value_counts()
        class_imbalance = value_counts.min() / value_counts.max()
    elif target_cardinality > 2 and target_cardinality < 50:
        target_type = 'multiclass_classification'
        class_imbalance = None
    else:
        target_type = 'regression'
        class_imbalance = None
    
    # Privacy-preserving column names hash
    col_names_str = '|'.join(sorted(df.columns))
    column_names_hash = hashlib.sha256(col_names_str.encode()).hexdigest()[:16]
    
    return {
        "n_rows": len(df),
        "n_cols": len(df.columns) - 1,  # Exclude target
        "column_types": {
            "numeric": len(numeric_cols),
            "categorical": len(categorical_cols),
            "text": len(text_cols)
        },
        "column_names_hash": column_names_hash,
        "avg_cardinality": float(avg_cardinality),
        "max_cardinality": int(max_cardinality),
        "target_type": target_type,
        "class_imbalance": float(class_imbalance) if class_imbalance is not None else None
    }


def log_training_metadata(
    session_id: str,
    df,
    optimal_params: Dict[str, int],
    pre_analysis_epochs: Optional[list] = None,
    final_result: Optional[Dict[str, float]] = None,
    deployment_id: Optional[str] = None
) -> Optional[str]:
    """
    Log training metadata to central meta-learning API.
    
    Args:
        session_id: Session ID
        df: Training DataFrame (for extracting characteristics)
        optimal_params: Optimal parameters found
        pre_analysis_epochs: Epoch-by-epoch pre-analysis results
        final_result: Final training results
        deployment_id: Deployment identifier (e.g., 'churro', 'burrito')
        
    Returns:
        metadata_id if successful, None otherwise
    """
    try:
        # Get software version
        from version import get_version
        software_version = get_version()
        
        # Extract dataset characteristics
        dataset_chars = get_dataset_characteristics(df)
        
        # Build metadata payload
        payload = {
            "software_version": str(software_version),  # Convert VersionInfo to string
            "deployment_id": deployment_id or "unknown",
            "session_id": session_id,
            "dataset_characteristics": dataset_chars,
            "optimal_params": optimal_params,
        }
        
        if pre_analysis_epochs:
            payload["pre_analysis_epochs"] = pre_analysis_epochs
        
        if final_result:
            payload["final_result"] = final_result
        
        # POST to meta-learning API
        logger.info(f"📤 Logging training metadata to {META_API_URL}/log-training-metadata")
        response = requests.post(
            f"{META_API_URL}/log-training-metadata",
            json=payload,
            timeout=10
        )
        
        if response.status_code == 201:
            result = response.json()
            metadata_id = result.get('metadata_id')
            logger.info(f"✅ Training metadata logged successfully: {metadata_id}")
            return metadata_id
        else:
            logger.warning(f"⚠️  Failed to log training metadata: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"❌ Error logging training metadata: {e}")
        return None


def query_optimal_parameters(df, target_type: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Query meta-learning API for recommended parameters based on dataset characteristics.
    
    Args:
        df: pandas DataFrame
        target_type: Override target type detection
        
    Returns:
        Dict with recommendation, or None if no data available
    """
    try:
        # Extract dataset characteristics
        dataset_chars = get_dataset_characteristics(df)
        
        # Query API
        params = {
            "n_rows": dataset_chars["n_rows"],
            "n_cols": dataset_chars["n_cols"],
            "target_type": target_type or dataset_chars["target_type"],
            "limit": 10
        }
        
        logger.info(f"🔍 Querying meta-learning API for similar datasets...")
        logger.info(f"   n_rows={params['n_rows']}, n_cols={params['n_cols']}, target_type={params['target_type']}")
        
        response = requests.get(
            f"{META_API_URL}/query-training-metadata",
            params=params,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            recommendation = result.get('recommendation')
            similar_count = len(result.get('similar_datasets', []))
            
            if recommendation:
                logger.info(f"✅ Found recommendation based on {similar_count} similar datasets:")
                logger.info(f"   d_model: {recommendation['d_model']}")
                logger.info(f"   n_transformer_layers: {recommendation['n_transformer_layers']}")
                logger.info(f"   n_attention_heads: {recommendation['n_attention_heads']}")
                logger.info(f"   Confidence: {recommendation['confidence']:.2f}")
                logger.info(f"   Pre-analysis epochs: {recommendation['pre_analysis_epochs']}")
                return result
            else:
                logger.info(f"ℹ️  No recommendations available yet (found {similar_count} datasets)")
                return None
        else:
            logger.warning(f"⚠️  Failed to query meta-learning API: {response.status_code}")
            return None
            
    except Exception as e:
        logger.error(f"❌ Error querying meta-learning API: {e}")
        return None


def get_recommended_pre_analysis_config(df) -> Dict[str, Any]:
    """
    Get recommended pre-analysis configuration based on meta-learning.
    
    Falls back to defaults if no meta-learning data available.
    
    Args:
        df: Training DataFrame
        
    Returns:
        Dict with recommended config:
        {
            "n_configs": 20,
            "epochs": 10,
            "d_model_choices": [64, 128],
            "layer_choices": [4, 6, 8],
            "head_choices": [2, 4, 8],
            "skip_pre_analysis": False,
            "predicted_params": {...} or None
        }
    """
    # Query meta-learning API
    query_result = query_optimal_parameters(df)
    
    if query_result and query_result.get('recommendation'):
        rec = query_result['recommendation']
        confidence = rec['confidence']
        
        if confidence > 0.9:
            # High confidence - use prediction directly, skip pre-analysis
            logger.info(f"🎯 High confidence ({confidence:.2f}) - using meta-learning prediction directly")
            return {
                "skip_pre_analysis": True,
                "predicted_params": {
                    "d_model": rec['d_model'],
                    "n_transformer_layers": rec['n_transformer_layers'],
                    "n_attention_heads": rec['n_attention_heads']
                },
                "confidence": confidence,
                "based_on_n_datasets": rec['based_on_n_datasets']
            }
        elif confidence > 0.7:
            # Medium confidence - quick validation with neighbors
            logger.info(f"🎯 Medium confidence ({confidence:.2f}) - quick validation around prediction")
            pred_d_model = rec['d_model']
            pred_layers = rec['n_transformer_layers']
            pred_heads = rec['n_attention_heads']
            
            # Test prediction + neighbors
            d_model_choices = [pred_d_model]
            if pred_d_model == 64:
                d_model_choices.append(96)
            elif pred_d_model == 128:
                d_model_choices.extend([96, 192])
            elif pred_d_model == 192:
                d_model_choices.append(128)
            
            layer_choices = [pred_layers, max(2, pred_layers - 2), min(10, pred_layers + 2)]
            head_choices = [pred_heads]
            
            return {
                "skip_pre_analysis": False,
                "n_configs": 5,  # Test just 5 configs
                "epochs": max(3, rec['pre_analysis_epochs'] // 2),  # Quick validation
                "d_model_choices": sorted(set(d_model_choices)),
                "layer_choices": sorted(set(layer_choices)),
                "head_choices": head_choices,
                "predicted_params": {
                    "d_model": pred_d_model,
                    "n_transformer_layers": pred_layers,
                    "n_attention_heads": pred_heads
                },
                "confidence": confidence
            }
        else:
            # Low confidence - full search but guided by prediction
            logger.info(f"🎯 Low confidence ({confidence:.2f}) - guided search")
            return {
                "skip_pre_analysis": False,
                "n_configs": 15,
                "epochs": rec['pre_analysis_epochs'],
                "d_model_choices": [64, 96, 128, 192],
                "layer_choices": [2, 3, 4, 6, 8],
                "head_choices": [2, 4, 8, 16],
                "predicted_params": {
                    "d_model": rec['d_model'],
                    "n_transformer_layers": rec['n_transformer_layers'],
                    "n_attention_heads": rec['n_attention_heads']
                },
                "confidence": confidence
            }
    else:
        # No meta-learning data - use adaptive defaults
        logger.info(f"ℹ️  No meta-learning data available - using adaptive defaults")
        n_rows = len(df)
        n_cols = len(df.columns) - 1
        
        # Adaptive based on dataset size
        if n_cols <= 10:
            d_model_choices = [64, 96]
        elif n_cols <= 30:
            d_model_choices = [96, 128]
        else:
            d_model_choices = [128, 192]
        
        if n_rows < 1000:
            layer_choices = [2, 3, 4]
        elif n_rows < 10000:
            layer_choices = [3, 4, 6]
        else:
            layer_choices = [4, 6, 8, 10]
        
        return {
            "skip_pre_analysis": False,
            "n_configs": 20,
            "epochs": 10,
            "d_model_choices": d_model_choices,
            "layer_choices": layer_choices,
            "head_choices": [2, 4, 8, 16],
            "predicted_params": None,
            "confidence": 0.0
        }

