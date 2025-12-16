"""
Quick Architecture Search

Runs a fast architecture search (25 epochs) to find optimal ES parameters
before full training. Uses random sampling + early stopping.
"""
import logging
import random
import asyncio
from pathlib import Path
from typing import Dict, Any, List
from itertools import product
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


def analyze_dataset(df) -> Dict[str, List[int]]:
    """
    Analyze dataset to determine intelligent search space.
    
    Args:
        df: Training DataFrame
    
    Returns:
        Dict with parameter choices based on dataset size/complexity
    """
    n_rows = len(df)
    n_cols = len(df.columns) - 1  # Exclude target
    
    # Adaptive d_model based on columns
    if n_cols <= 10:
        d_model_choices = [64, 96]
    elif n_cols <= 30:
        d_model_choices = [96, 128]
    else:
        d_model_choices = [128, 192]
    
    # Adaptive layers based on rows (more data = can go deeper)
    if n_rows < 1000:
        layer_choices = [2, 3, 4]  # Shallow - avoid overfitting
    elif n_rows < 10000:
        layer_choices = [3, 4, 6]
    else:
        layer_choices = [4, 6, 8, 10]  # Deep - can handle complexity
    
    # Heads: Keep 8-32 dims per head (d_model / n_heads)
    head_choices = []
    for d in d_model_choices:
        # Add heads that give reasonable dims/head
        for h in [2, 4, 8, 16]:
            dims_per_head = d / h
            if 8 <= dims_per_head <= 32:  # Sweet spot
                if h not in head_choices:
                    head_choices.append(h)
    head_choices.sort()
    
    logger.info(f"📊 Dataset analysis:")
    logger.info(f"   {n_rows} rows, {n_cols} columns")
    logger.info(f"   Search space: d_model={d_model_choices}, layers={layer_choices}, heads={head_choices}")
    
    return {
        'd_model': d_model_choices,
        'n_transformer_layers': layer_choices,
        'n_attention_heads': head_choices,
    }


def sample_configs(search_space: Dict[str, List], n_samples: int = 20) -> List[Dict[str, int]]:
    """
    Sample configurations intelligently from search space.
    
    Strategy:
    - Always test extremes (min/max of each dimension)
    - Random sample the middle
    
    Args:
        search_space: Dict of parameter choices
        n_samples: Number of configs to sample
    
    Returns:
        List of config dicts
    """
    all_configs = list(product(
        search_space['d_model'],
        search_space['n_transformer_layers'],
        search_space['n_attention_heads']
    ))
    
    if len(all_configs) <= n_samples:
        # Small space - test everything
        configs = all_configs
    else:
        # Sample strategically
        configs_to_test = set()
        
        # Add corner cases (min/max combinations)
        configs_to_test.add(all_configs[0])   # Min everything
        configs_to_test.add(all_configs[-1])  # Max everything
        
        # Add mid-range
        mid_idx = len(all_configs) // 2
        if mid_idx < len(all_configs):
            configs_to_test.add(all_configs[mid_idx])
        
        # Random sample the rest
        remaining = n_samples - len(configs_to_test)
        if remaining > 0:
            available = [c for c in all_configs if c not in configs_to_test]
            if available:
                sampled = random.sample(available, min(remaining, len(available)))
                configs_to_test.update(sampled)
        
        configs = list(configs_to_test)
    
    # Convert to list of dicts
    config_dicts = [
        {
            'd_model': d,
            'n_transformer_layers': layers,
            'n_attention_heads': heads
        }
        for d, layers, heads in configs
    ]
    
    logger.info(f"🎲 Sampled {len(config_dicts)} configurations to test")
    
    return config_dicts


def run_quick_architecture_search(data_file: str, strings_cache: str, session_id: str,
                                   n_samples: int = 20, quick_epochs: int = 25, 
                                   suggested_configs: List[Dict[str, int]] = None) -> Dict[str, Any]:
    """
    Run quick architecture search on a dataset.
    
    Args:
        data_file: Path to SQLite database
        strings_cache: Path to strings cache
        session_id: Session ID (for loading data)
        n_samples: Number of configs to test (ignored if suggested_configs provided)
        quick_epochs: Epochs for quick search
        suggested_configs: Optional list of specific configs to test (from meta-learning)
                          Format: [{"d_model": 128, "n_transformer_layers": 6, "n_attention_heads": 8}, ...]
    
    Returns:
        Dict with optimal config
    """
    from lib.featrix.neural.input_data_file import FeatrixInputDataFile
    from lib.featrix.neural.input_data_set import FeatrixInputDataSet
    from lib.featrix.neural.embedded_space import EmbeddingSpace
    from lib.featrix.neural.single_predictor import FeatrixSinglePredictor
    from lib.featrix.neural.simple_mlp import SimpleMLP
    from lib.featrix.neural.model_config import SimpleMLPConfig
    import pandas as pd
    
    logger.info(f"📂 Loading dataset from: {data_file}")
    
    # Load data from SQLite database created by create_structured_data
    # NOTE: We use the data_file parameter (SQLite DB), NOT session.get('input_data') (original upload)
    if not data_file:
        from lib.session_manager import load_session
        session = load_session(session_id)
        data_file = session.get('sqlite_db')
        if not data_file:
            raise ValueError(f"No data_file provided and session {session_id} has no sqlite_db")
    
    # Load from SQLite database
    input_file = FeatrixInputDataFile(str(data_file))
    df = input_file.df
    
    logger.info(f"✅ Loaded {len(df)} rows, {len(df.columns)} columns from SQLite database")
    
    # Use suggested configs from meta-learning if provided, otherwise sample adaptively
    if suggested_configs:
        logger.info(f"🎯 Using {len(suggested_configs)} suggested configs from meta-learning API")
        configs_to_test = suggested_configs
    else:
        # Analyze dataset to determine search space
        search_space = analyze_dataset(df)
        
        # Sample configurations
        configs_to_test = sample_configs(search_space, n_samples=n_samples)
        logger.info(f"🔀 Using adaptive sampling strategy")
    
    logger.info(f"🧪 Testing {len(configs_to_test)} configurations with {quick_epochs} epochs each")
    
    results = []
    
    for i, config in enumerate(configs_to_test, 1):
        logger.info(f"\n[{i}/{len(configs_to_test)}] Testing: {config}")
        
        try:
            # Create dataset
            dataset = FeatrixInputDataSet(df=df, ignore_cols=[], limit_rows=None)
            detected_types = {col: det.get_codec_name() for col, det in dataset._detectors.items()}
            dataset.encoderOverrides = detected_types
            train_data, val_data = dataset.split(fraction=0.2)
            
            # Train ES with this config
            es = EmbeddingSpace(
                train_data, val_data,
                d_model=config['d_model'],
                n_transformer_layers=config['n_transformer_layers'],
                n_attention_heads=config['n_attention_heads'],
                output_debug_label=f"quick_search_{i}",
                string_cache=strings_cache
            )
            es.train(batch_size=0, n_epochs=quick_epochs, movie_frame_interval=None)
            
            # Train quick SP to get validation AUC
            sp_config = SimpleMLPConfig(
                d_in=config['d_model'],
                d_out=2,  # Binary for now
                d_hidden=256,
                n_hidden_layers=2,  # Simple predictor for quick test
                dropout=0.1,
                normalize=False,
                residual=True,
                use_batch_norm=True
            )
            predictor = SimpleMLP(sp_config)
            fsp = FeatrixSinglePredictor(es, predictor)
            
            # Get target column (first non-excluded column or 'target')
            target_col = 'target' if 'target' in df.columns else df.columns[-1]
            
            fsp.prep_for_training(
                train_df=df,
                target_col_name=target_col,
                target_col_type='set'
            )
            
            # Train SP briefly
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            training_results = loop.run_until_complete(
                fsp.train(n_epochs=quick_epochs, batch_size=128, fine_tune=False, val_pos_label=None)
            )
            loop.close()
            
            # Extract final AUC
            if training_results and len(training_results) > 0:
                final_metrics = training_results[-1].get('metrics', {})
                auc = final_metrics.get('auc', 0)
            else:
                auc = 0
            
            logger.info(f"   Result: AUC={auc:.4f}")
            
            results.append({
                **config,
                'auc': auc,
                'tested': True
            })
            
        except Exception as e:
            logger.error(f"   ❌ Config failed: {e}")
            results.append({
                **config,
                'auc': 0,
                'tested': False,
                'error': str(e)
            })
    
    # Pick best config
    successful_results = [r for r in results if r.get('tested', False)]
    if not successful_results:
        logger.error("❌ No configs succeeded - using defaults")
        optimal_config = {
            'd_model': 128,
            'n_transformer_layers': 4,
            'n_attention_heads': 8,
            'estimated_auc': 0,
            'used_default': True
        }
    else:
        best = max(successful_results, key=lambda x: x['auc'])
        optimal_config = {
            'd_model': best['d_model'],
            'n_transformer_layers': best['n_transformer_layers'],
            'n_attention_heads': best['n_attention_heads'],
            'estimated_auc': best['auc'],
            'configs_tested': len(results),
            'configs_succeeded': len(successful_results)
        }
    
    logger.info(f"🏆 Optimal config selected: {optimal_config}")
    
    return optimal_config

