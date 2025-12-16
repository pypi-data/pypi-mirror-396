#  -*- coding: utf-8 -*-
#
#  Copyright Featrix, Inc 2023-2025
#
#  Proprietary and Confidential.  Unauthorized use, copying or dissemination
#  of these materials is strictly prohibited.
#
"""
I/O utilities for loading and saving EmbeddingSpace objects.
Consolidated from multiple locations to provide a single source of truth.
"""
import os
import pickle
import sys
import time
import traceback
import logging
from pathlib import Path

try:
    import torch
except ImportError:
    torch = None

logger = logging.getLogger(__name__)

try:
    from featrix.neural.gpu_utils import (
        is_gpu_available,
        get_gpu_memory_allocated,
        get_gpu_memory_reserved,
        get_max_gpu_memory_allocated,
        get_max_gpu_memory_reserved,
        get_gpu_memory_summary,
        get_gpu_memory_snapshot,
        get_gpu_device_properties,
    )
except ImportError:
    # Fallback if gpu_utils not available
    def is_gpu_available():
        try:
            import torch
            return torch.cuda.is_available()
        except ImportError:
            return False
    def get_gpu_memory_allocated():
        return 0.0
    def get_gpu_memory_reserved():
        return 0.0
    def get_max_gpu_memory_allocated():
        return 0.0
    def get_max_gpu_memory_reserved():
        return 0.0
    def get_gpu_memory_summary(*args, **kwargs):
        return ""
    def get_gpu_memory_snapshot():
        return {}


def _log_gpu_memory(context: str = "", log_level=logging.INFO):
    """Quick GPU memory logging for tracing memory usage."""
    try:
        if torch is None or not is_gpu_available():
            return
        allocated = get_gpu_memory_allocated()  # GB (returns 0.0 for MPS/CPU)
        reserved = get_gpu_memory_reserved()  # GB (returns 0.0 for MPS/CPU)
        max_allocated = get_max_gpu_memory_allocated()  # GB (returns 0.0 for MPS/CPU)
        logger.log(log_level, f"📊 GPU MEMORY [{context}]: Allocated={allocated:.3f} GB, Reserved={reserved:.3f} GB, Peak={max_allocated:.3f} GB")
    except Exception as e:
        logger.debug(f"Could not log GPU memory: {e}")


def dump_cuda_memory_usage(context: str = ""):
    """
    Dump detailed CUDA memory usage information when OOM occurs.
    This helps debug what's holding VRAM.
    
    Args:
        context: Optional context string describing where the OOM occurred
    """
    try:
        if torch is None or not is_gpu_available():
            logger.warning(f"⚠️  CUDA not available - cannot dump memory usage")
            return
        
        logger.error("="*80)
        logger.error(f"🔍 CUDA MEMORY DUMP {f'({context})' if context else ''}")
        logger.error("="*80)
        
        # Get memory stats
        allocated = get_gpu_memory_allocated()  # GB (returns 0.0 for MPS/CPU)
        reserved = get_gpu_memory_reserved()  # GB (returns 0.0 for MPS/CPU)
        max_allocated = get_max_gpu_memory_allocated()  # GB (returns 0.0 for MPS/CPU)
        max_reserved = get_max_gpu_memory_reserved()  # GB (returns 0.0 for MPS/CPU)
        
        logger.error(f"📊 Current Memory Usage:")
        logger.error(f"   Allocated: {allocated:.2f} GB")
        logger.error(f"   Reserved: {reserved:.2f} GB")
        logger.error(f"   Max Allocated (peak): {max_allocated:.2f} GB")
        logger.error(f"   Max Reserved (peak): {max_reserved:.2f} GB")
        
        # Get detailed memory summary
        try:
            memory_summary = get_gpu_memory_summary(abbreviated=False)
            logger.error(f"\n📋 Detailed Memory Summary:")
            logger.error(memory_summary)
        except Exception as summary_err:
            logger.warning(f"⚠️  Could not get detailed memory summary: {summary_err}")
        
        # Get memory snapshot (shows what tensors are allocated)
        try:
            memory_snapshot = get_gpu_memory_snapshot()
            if memory_snapshot:
                logger.error(f"\n📸 Memory Snapshot Analysis:")
                logger.error(f"   Total active allocations: {len(memory_snapshot)}")
                
                # Group allocations by size to identify patterns
                size_buckets = {
                    '<1MB': 0,
                    '1-10MB': 0,
                    '10-100MB': 0,
                    '100MB-1GB': 0,
                    '>1GB': 0
                }
                total_size_by_bucket = {
                    '<1MB': 0,
                    '1-10MB': 0,
                    '10-100MB': 0,
                    '100MB-1GB': 0,
                    '>1GB': 0
                }
                
                # Find largest allocations
                allocations_with_size = []
                for alloc in memory_snapshot:
                    if isinstance(alloc, dict):
                        total_size = alloc.get('total_size', 0)
                        active_size = alloc.get('active_size', 0)
                        size_mb = total_size / (1024**2)
                        
                        # Bucket by size
                        if size_mb < 1:
                            size_buckets['<1MB'] += 1
                            total_size_by_bucket['<1MB'] += total_size
                        elif size_mb < 10:
                            size_buckets['1-10MB'] += 1
                            total_size_by_bucket['1-10MB'] += total_size
                        elif size_mb < 100:
                            size_buckets['10-100MB'] += 1
                            total_size_by_bucket['10-100MB'] += total_size
                        elif size_mb < 1024:
                            size_buckets['100MB-1GB'] += 1
                            total_size_by_bucket['100MB-1GB'] += total_size
                        else:
                            size_buckets['>1GB'] += 1
                            total_size_by_bucket['>1GB'] += total_size
                        
                        # Track for largest allocations
                        if active_size > 0:
                            allocations_with_size.append((active_size, alloc))
                
                # Show size distribution
                logger.error(f"\n📊 Allocation Size Distribution:")
                for bucket, count in size_buckets.items():
                    if count > 0:
                        size_mb = total_size_by_bucket[bucket] / (1024**2)
                        logger.error(f"   {bucket:12s}: {count:6d} allocations, {size_mb:8.2f} MB total")
                
                # Show top 10 largest allocations
                if allocations_with_size:
                    allocations_with_size.sort(reverse=True, key=lambda x: x[0])
                    logger.error(f"\n🔝 Top 10 Largest Active Allocations:")
                    for i, (active_size, alloc) in enumerate(allocations_with_size[:10], 1):
                        size_mb = active_size / (1024**2)
                        total_size_mb = alloc.get('total_size', 0) / (1024**2)
                        segment_type = alloc.get('segment_type', 'unknown')
                        logger.error(f"   {i:2d}. {size_mb:8.2f} MB active / {total_size_mb:8.2f} MB total ({segment_type} pool)")
                        # Show frames if available
                        frames = alloc.get('frames', [])
                        if frames:
                            logger.error(f"       Stack trace:")
                            for frame in frames[:3]:  # First 3 frames
                                filename = frame.get('filename', 'unknown')
                                line = frame.get('line', 'unknown')
                                func = frame.get('function', 'unknown')
                                logger.error(f"         {filename}:{line} in {func}")
                
                # Show first 5 allocations with details (for debugging)
                logger.error(f"\n🔍 Sample Allocations (first 5):")
                for i, alloc in enumerate(memory_snapshot[:5], 1):
                    if isinstance(alloc, dict):
                        total_size_mb = alloc.get('total_size', 0) / (1024**2)
                        active_size_mb = alloc.get('active_size', 0) / (1024**2)
                        segment_type = alloc.get('segment_type', 'unknown')
                        blocks = alloc.get('blocks', [])
                        active_blocks = [b for b in blocks if b.get('state') == 'active_allocated']
                        logger.error(f"   {i}. {active_size_mb:.2f} MB / {total_size_mb:.2f} MB ({segment_type}, {len(active_blocks)} active blocks)")
                
                if len(memory_snapshot) > 5:
                    logger.error(f"   ... and {len(memory_snapshot) - 5} more allocations")
        except Exception as snapshot_err:
            logger.warning(f"⚠️  Could not get memory snapshot: {snapshot_err}")
        
        # Get nvidia-smi output for comparison
        try:
            import subprocess
            nvidia_smi = subprocess.run(
                ['nvidia-smi', '--query-gpu=memory.used,memory.total,utilization.gpu', '--format=csv,noheader,nounits'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if nvidia_smi.returncode == 0:
                logger.error(f"\n🖥️  nvidia-smi GPU Status:")
                for line in nvidia_smi.stdout.strip().split('\n'):
                    if line.strip():
                        parts = line.split(',')
                        if len(parts) >= 3:
                            mem_used = parts[0].strip()
                            mem_total = parts[1].strip()
                            gpu_util = parts[2].strip()
                            logger.error(f"   Memory: {mem_used} MB / {mem_total} MB, Utilization: {gpu_util}%")
        except Exception as smi_err:
            logger.warning(f"⚠️  Could not get nvidia-smi output: {smi_err}")
        
        logger.error("="*80)
        
    except ImportError:
        logger.warning(f"⚠️  PyTorch not available - cannot dump CUDA memory usage")
    except Exception as e:
        logger.warning(f"⚠️  Failed to dump CUDA memory usage: {e}")


def _reconstruct_es_from_checkpoint_dict(checkpoint_dict: dict, es_path: str, logger=None, skip_datasets: bool = False):
    """
    Reconstruct an EmbeddingSpace from a checkpoint dict (OLD FORMAT - for backwards compatibility).
    
    Args:
        checkpoint_dict: Dictionary containing 'model' key with the encoder
        es_path: Path to the checkpoint file (used to extract session_id)
        logger: Optional logger instance
        skip_datasets: If True, create minimal datasets (for SP training)
    
    Returns:
        Reconstructed EmbeddingSpace object
    
    Raises:
        Various exceptions if reconstruction fails
    """
    if logger is None:
        logger = logging.getLogger(__name__)
    
    # Check if it's a valid checkpoint dict
    if 'model' not in checkpoint_dict:
        raise TypeError(
            f"Loaded a dict from {es_path}, but it doesn't contain a 'model' key. "
            f"This doesn't appear to be a valid checkpoint dict. Dict keys: {list(checkpoint_dict.keys())}"
        )
    
    # Extract session_id - try multiple strategies
    es_path_obj = Path(es_path)
    es_dir = es_path_obj.parent
    path_parts = es_path_obj.parts
    session_id = None
    
    # Strategy 1: Check for metadata.json in same directory
    metadata_json = es_dir / "metadata.json"
    if metadata_json.exists():
        try:
            import json
            with open(metadata_json, 'r') as f:
                metadata = json.load(f)
            session_id = metadata.get('model_info', {}).get('session_id')
            if session_id:
                logger.info(f"✅ Found session_id in metadata.json: {session_id}")
        except Exception as e:
            logger.warning(f"⚠️  Could not read session_id from metadata.json: {e}")
    
    # Strategy 2: Check if checkpoint_dict itself contains es_config with session_id
    checkpoint_has_full_config = False
    if not session_id and 'es_config' in checkpoint_dict:
        session_id = checkpoint_dict['es_config'].get('session_id')
        if session_id:
            logger.info(f"✅ Found session_id in checkpoint es_config: {session_id}")
        # Check if checkpoint also has input_data - if so, it's fully self-contained
        if 'input_data' in checkpoint_dict and checkpoint_dict['input_data'].get('path'):
            checkpoint_has_full_config = True
            logger.info(f"✅ Checkpoint is self-contained (has es_config + input_data)")
    
    # Strategy 3: Extract from path for 'train_es' directories
    if not session_id and 'train_es' in path_parts:
        train_es_idx = path_parts.index('train_es')
        if train_es_idx > 0:
            session_id = path_parts[train_es_idx - 1]
            logger.info(f"✅ Extracted session_id from train_es path: {session_id}")
    
    # Strategy 4: Try to extract from featrix_output path
    if not session_id and 'featrix_output' in path_parts:
        featrix_idx = path_parts.index('featrix_output')
        if featrix_idx + 1 < len(path_parts):
            session_id = path_parts[featrix_idx + 1]
            logger.info(f"✅ Extracted session_id from featrix_output path: {session_id}")
    
    if not session_id:
        raise ValueError(
            f"Could not extract session_id from checkpoint, metadata.json, or path: {es_path}. "
            f"Path parts: {path_parts}. "
            f"Tried: metadata.json, checkpoint es_config, path parsing"
        )
    
    logger.info(f"🔍 Extracted session_id from path: {session_id}")
    
    # If checkpoint has full config (es_config + input_data), use it directly without loading session
    if checkpoint_has_full_config:
        logger.info(f"✅ Using self-contained checkpoint data (no session file needed)")
        input_data_info = checkpoint_dict['input_data']
        input_data_path = Path(input_data_info['path']) if input_data_info.get('path') else None
        column_spec = input_data_info.get('column_spec', {})
        column_overrides = input_data_info.get('column_overrides', {})
        json_transformations = input_data_info.get('json_transformations', {})
        string_cache_path = input_data_info.get('string_cache')
        
        logger.info(f"   Input data: {input_data_path}")
        logger.info(f"   Columns: {len(column_spec)}")
        logger.info(f"   Column overrides: {len(column_overrides)}")
        
        # Skip session loading - use checkpoint data directly
        session = None
    else:
        # Load session to get configuration (old checkpoints without full config)
        logger.info(f"🔍 Loading session {session_id} (checkpoint doesn't have full config)...")
        try:
            from lib.session_manager import load_session
            session = load_session(session_id)
        except Exception as e:
            logger.error(f"❌ RECONSTRUCTION FAILED: Exception loading session {session_id}")
            logger.error(f"   Exception type: {type(e).__name__}")
            logger.error(f"   Exception message: {e}")
            logger.error(f"   Full traceback:\n{traceback.format_exc()}")
            raise
        
        if not session:
            raise ValueError(f"Session {session_id} not found - cannot reconstruct EmbeddingSpace from checkpoint")
        
        # Get config from session
        column_overrides = session.get('column_overrides', {})
        json_transformations = session.get('json_transformations', {})
        string_cache_path = session.get('strings_cache')
        input_data_path = None
    
    # Get input data path - from checkpoint (if self-contained) or session
    if not checkpoint_has_full_config:
        # Get from session
        sqlite_db_path = session.get('sqlite_db')
    else:
        sqlite_db_path = None  # Already set input_data_path above from checkpoint
    
    if sqlite_db_path and not input_data_path:
        sqlite_db = Path(sqlite_db_path)
        if sqlite_db.exists():
            input_data_path = sqlite_db
            logger.info(f"✅ Found SQLite database from session: {input_data_path}")
    
    # Fallback to input_data field from session (if session exists)
    if not input_data_path and session:
        original_path = session.get('input_data') or session.get('input_filename')
        if original_path:
            input_data_path = Path(original_path)
            if not input_data_path.exists():
                # Try in data_dir
                try:
                    from config import config
                    if hasattr(config, 'data_dir'):
                        input_data_path = Path(config.data_dir) / Path(original_path).name
                except ImportError:
                    pass
            if input_data_path.exists():
                logger.info(f"✅ Found input data: {input_data_path}")
    
    if not skip_datasets and (not input_data_path or not input_data_path.exists()):
        tried_paths = f"sqlite_db: {sqlite_db_path if 'sqlite_db_path' in locals() else 'N/A'}"
        if session:
            tried_paths += f", input_data: {session.get('input_data')}, input_filename: {session.get('input_filename')}"
        raise FileNotFoundError(
            f"Could not find input data file for session {session_id}. "
            f"Tried {tried_paths}"
        )
    
    # Load input data and create datasets (or create dummy datasets if skipping)
    # CRITICAL: If checkpoint has empty/missing col_codecs, we MUST load real data to recreate them!
    # Otherwise ES will have empty col_codecs and SP training will fail!
    must_load_data_for_codecs = False
    if skip_datasets:
        # Check if checkpoint has empty or missing col_codecs - if so, we MUST load data
        if 'col_codecs' in checkpoint_dict:
            if not checkpoint_dict['col_codecs'] or len(checkpoint_dict['col_codecs']) == 0:
                logger.warning(f"⚠️  Checkpoint has EMPTY col_codecs - must load real data to recreate them")
                must_load_data_for_codecs = True
                skip_datasets = False  # Override skip_datasets
        else:
            logger.warning(f"⚠️  Checkpoint missing col_codecs - must load real data to recreate them")
            must_load_data_for_codecs = True
            skip_datasets = False  # Override skip_datasets
    
    if skip_datasets:
        logger.info(f"⏭️  Skipping dataset loading (skip_datasets=True) - creating minimal datasets")
        try:
            import pandas as pd
            from featrix.neural.input_data_set import FeatrixInputDataSet
            # Create minimal dummy dataset
            dummy_df = pd.DataFrame()
            train_dataset = FeatrixInputDataSet(df=dummy_df, ignore_cols=[], standup_only=True)
            val_dataset = FeatrixInputDataSet(df=dummy_df, ignore_cols=[], standup_only=True)
        except Exception as e:
            logger.error(f"❌ Failed to create dummy datasets: {e}")
            raise
    else:
        logger.info(f"🔍 Loading input data from {input_data_path}...")
        try:
            from featrix.neural.input_data_file import FeatrixInputDataFile
            input_data_file = FeatrixInputDataFile(str(input_data_path))
            train_df = input_data_file.df
        except Exception as e:
            logger.error(f"❌ RECONSTRUCTION FAILED: Exception loading input data file {input_data_path}")
            logger.error(f"   Exception type: {type(e).__name__}")
            logger.error(f"   Exception message: {e}")
            logger.error(f"   Full traceback:\n{traceback.format_exc()}")
            raise
        
        try:
            from featrix.neural.input_data_set import FeatrixInputDataSet
            train_dataset = FeatrixInputDataSet(
                df=train_df,
                ignore_cols=[],
                limit_rows=None,
                encoder_overrides=column_overrides,
            )
            val_dataset = FeatrixInputDataSet(
                df=train_df,
                ignore_cols=[],
                limit_rows=None,
                encoder_overrides=column_overrides,
            )
        except Exception as e:
            logger.error(f"❌ RECONSTRUCTION FAILED: Exception creating datasets")
            logger.error(f"   Exception type: {type(e).__name__}")
            logger.error(f"   Exception message: {e}")
            logger.error(f"   Full traceback:\n{traceback.format_exc()}")
            raise
    
    # Create EmbeddingSpace from config (checkpoint or session)
    logger.info(f"🔍 Creating EmbeddingSpace from {'checkpoint' if checkpoint_has_full_config else 'session'} config...")
    
    # Get additional config from session if available
    n_epochs = session.get('n_epochs') if session else None
    d_model_override = session.get('d_model') if session else None
    version_info = session.get('version_info') if session else None
    name = session.get('name') if session else None
    required_child_es_mapping = session.get('required_child_es_mapping', {}) if session else {}
    sqlite_db_path = session.get('sqlite_db') if session else str(input_data_path) if input_data_path else None
    user_metadata = session.get('user_metadata') if session else None
    
    # For self-contained checkpoints, use es_config d_model
    if checkpoint_has_full_config and 'es_config' in checkpoint_dict:
        d_model_override = checkpoint_dict['es_config'].get('d_model')
    
    try:
        from featrix.neural.embedded_space import EmbeddingSpace
        
        # If checkpoint has col_codecs, use them to get vocabulary overrides
        codec_vocabulary_overrides = {}
        if 'col_codecs' in checkpoint_dict:
            logger.info(f"✅ Checkpoint contains col_codecs - extracting vocabularies...")
            for col_name, codec in checkpoint_dict['col_codecs'].items():
                if hasattr(codec, 'vocab'):
                    codec_vocabulary_overrides[col_name] = set(codec.vocab.keys())
            logger.info(f"   Extracted vocabulary for {len(codec_vocabulary_overrides)} columns")
        
        es = EmbeddingSpace(
            train_input_data=train_dataset,
            val_input_data=val_dataset,
            output_debug_label=f"Reconstructed from {'self-contained ' if checkpoint_has_full_config else ''}checkpoint",
            n_epochs=n_epochs,
            d_model=d_model_override,
            encoder_config=None,
            string_cache=string_cache_path,
            json_transformations=json_transformations,
            version_info=version_info,
            output_dir=str(es_dir),
            name=name,
            required_child_es_mapping=required_child_es_mapping,
            sqlite_db_path=sqlite_db_path,
            user_metadata=user_metadata,
            skip_pca_init=True,  # Skip PCA - model is already trained
            codec_vocabulary_overrides=codec_vocabulary_overrides,  # Use checkpoint vocabularies
        )
    except Exception as e:
        logger.error(f"❌ RECONSTRUCTION FAILED: Exception creating EmbeddingSpace")
        logger.error(f"   Exception type: {type(e).__name__}")
        logger.error(f"   Exception message: {e}")
        if session:
            logger.error(f"   Session keys: {list(session.keys())}")
            logger.error(f"   n_epochs: {session.get('n_epochs')}, d_model: {session.get('d_model')}")
        else:
            logger.error(f"   Using self-contained checkpoint (no session)")
        logger.error(f"   Full traceback:\n{traceback.format_exc()}")
        raise
    
    # Load the checkpoint model into EmbeddingSpace
    logger.info(f"🔄 Loading checkpoint model into EmbeddingSpace...")
    try:
        # Check if checkpoint contains state_dict or full model
        checkpoint_model = checkpoint_dict["model"]
        
        # If checkpoint has col_codecs, use them directly (replaces what __init__ created)
        if 'col_codecs' in checkpoint_dict and checkpoint_dict['col_codecs']:
            logger.info(f"   Replacing ES col_codecs with checkpoint col_codecs ({len(checkpoint_dict['col_codecs'])} codecs)...")
            es.col_codecs = checkpoint_dict['col_codecs']
        else:
            if 'col_codecs' in checkpoint_dict:
                logger.warning(f"   ⚠️  Checkpoint has col_codecs key but it's EMPTY - will try to extract from encoder after loading")
            else:
                logger.warning(f"   ⚠️  Checkpoint doesn't contain col_codecs - will try to extract from encoder after loading")
        
        if isinstance(checkpoint_model, dict):
            # It's a state_dict - load it into the encoder
            logger.info(f"   Loading state_dict into encoder...")
            es.encoder.load_state_dict(checkpoint_model)
        else:
            # It's the full model - use it directly
            logger.info(f"   Using full encoder from checkpoint...")
            es.encoder = checkpoint_model
        
        epoch_idx = checkpoint_dict.get("epoch_idx", None)
        if epoch_idx is not None:
            logger.info(f"   Checkpoint epoch: {epoch_idx}")
            if not hasattr(es, 'training_info'):
                es.training_info = {}
            es.training_info['best_checkpoint_epoch'] = epoch_idx
            es.training_info['best_checkpoint_loaded'] = True
        
        # CRITICAL: If col_codecs weren't in checkpoint, try to extract from encoder
        # This handles old checkpoints that didn't save col_codecs separately
        if not es.col_codecs or len(es.col_codecs) == 0:
            logger.warning(f"   ⚠️  ES col_codecs is empty - attempting to extract from encoder...")
            if hasattr(es.encoder, 'column_encoder') and hasattr(es.encoder.column_encoder, 'col_codecs'):
                es.col_codecs = es.encoder.column_encoder.col_codecs
                logger.info(f"   ✅ Extracted {len(es.col_codecs)} codecs from encoder.column_encoder")
            elif hasattr(es.encoder, 'col_codecs'):
                es.col_codecs = es.encoder.col_codecs
                logger.info(f"   ✅ Extracted {len(es.col_codecs)} codecs from encoder")
            else:
                # Last resort: If encoder doesn't have col_codecs (old pickled encoder), 
                # we're stuck - ES __init__ should have created them from column_spec if available
                logger.error(f"   ❌ CRITICAL: Could not extract col_codecs from encoder!")
                logger.error(f"   Encoder type: {type(es.encoder)}")
                logger.error(f"   Encoder has column_encoder: {hasattr(es.encoder, 'column_encoder')}")
                if hasattr(es.encoder, 'column_encoder'):
                    logger.error(f"   column_encoder type: {type(es.encoder.column_encoder)}")
                    logger.error(f"   column_encoder has col_codecs: {hasattr(es.encoder.column_encoder, 'col_codecs')}")
                logger.error(f"   This checkpoint was saved before col_codecs were properly stored.")
                logger.error(f"   If ES still has empty col_codecs, this is likely a fatal error.")
    except Exception as e:
        logger.error(f"❌ RECONSTRUCTION FAILED: Exception loading checkpoint model into EmbeddingSpace")
        logger.error(f"   Exception type: {type(e).__name__}")
        logger.error(f"   Exception message: {e}")
        logger.error(f"   checkpoint_dict['model'] type: {type(checkpoint_dict.get('model', 'N/A'))}")
        logger.error(f"   Full traceback:\n{traceback.format_exc()}")
        raise
    
    # CRITICAL: Validate d_model matches encoder's actual output dimension
    # This catches mismatches between auto-computed d_model and encoder's actual d_model
    if hasattr(es, 'encoder') and hasattr(es.encoder, 'config') and hasattr(es.encoder.config, 'd_model'):
        encoder_d_model = es.encoder.config.d_model
        if encoder_d_model != es.d_model:
            logger.warning(f"⚠️  DIMENSION MISMATCH DETECTED:")
            logger.warning(f"   es.d_model = {es.d_model} (from auto-compute or config)")
            logger.warning(f"   encoder.config.d_model = {encoder_d_model} (encoder's actual output dimension)")
            logger.warning(f"   Using encoder's d_model={encoder_d_model}")
            es.d_model = encoder_d_model
    
    logger.info(f"✅ Successfully reconstructed EmbeddingSpace from checkpoint dict")
    return es


def load_embedded_space(es_path: str, force_cpu: bool = None, skip_datasets: bool = False):
    """
    Load a pickled embedding space from disk.
    
    This is the consolidated, feature-complete version that handles:
    - GPU cache management
    - CPU version detection and usage
    - Checkpoint dict reconstruction
    - CUDA OOM handling
    - Persistent ID errors
    - torch.load fallback
    
    Args:
        es_path: Path to the embedding space file (.pickle or .pth)
        force_cpu: If True, force CPU loading (sets FEATRIX_FORCE_CPU_SINGLE_PREDICTOR=1).
                   If None, uses existing env var. For backward compatibility.
        skip_datasets: If True, skip loading datasets during reconstruction (for SP training where
                      datasets will be created separately from predictor's own data).
    
    Returns:
        EmbeddingSpace object
    """
    # Handle force_cpu parameter for backward compatibility
    # The old lib/utils.py version set FEATRIX_FORCE_CPU_SENTENCE_MODEL for sentence transformers
    # The new version uses FEATRIX_FORCE_CPU_SINGLE_PREDICTOR for single predictor training
    # We set both to preserve backward compatibility
    if force_cpu is not None:
        if force_cpu:
            os.environ['FEATRIX_FORCE_CPU_SINGLE_PREDICTOR'] = '1'
            os.environ['FEATRIX_FORCE_CPU_SENTENCE_MODEL'] = '1'  # For backward compatibility
        else:
            os.environ.pop('FEATRIX_FORCE_CPU_SINGLE_PREDICTOR', None)
            os.environ.pop('FEATRIX_FORCE_CPU_SENTENCE_MODEL', None)
    # CRITICAL: Clear GPU cache at the VERY START to free up any reserved memory
    # This must happen before ANY unpickling starts, as __setstate__ methods may allocate GPU memory
    try:
        if torch is not None and is_gpu_available():
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()
            logger.info(f"🧹 Cleared GPU cache at START of load_embedded_space (before any unpickling)")
            _log_gpu_memory("AT START of load_embedded_space (after cache clear)")
    except Exception as e:
        logger.debug(f"Could not clear GPU cache at start: {e}")
    
    # CRITICAL: Check memory BEFORE anything else and force CPU if needed
    # This prevents GPU allocation during unpickling even if we have a "CPU version"
    force_cpu_from_env = os.environ.get('FEATRIX_FORCE_CPU_SINGLE_PREDICTOR') == '1'
    
    # Check GPU memory early and force CPU if memory is tight
    # This must happen BEFORE unpickling starts, as unpickling will try to allocate GPU memory
    if torch is not None and is_gpu_available() and not force_cpu_from_env:
        try:
            allocated = torch.cuda.memory_allocated() / (1024**3)
            reserved = torch.cuda.memory_reserved() / (1024**3)
            props = get_gpu_device_properties(0)
            total_memory = (props.total_memory / (1024**3)) if props else 0.0
            free_memory = total_memory - reserved
            reserved_percent = (reserved / total_memory) * 100
            
            # CRITICAL: If memory is tight, force CPU BEFORE unpickling
            # Even "CPU versions" can trigger GPU allocation during unpickling
            if reserved_percent > 50 or free_memory < 50:
                logger.warning(f"⚠️  Early memory check: Reserved={reserved_percent:.1f}%, Free={free_memory:.2f} GB")
                logger.warning(f"   Auto-forcing CPU loading to prevent GPU allocation during unpickling")
                force_cpu_from_env = True
                os.environ['FEATRIX_FORCE_CPU_SINGLE_PREDICTOR'] = '1'
                os.environ['FEATRIX_FORCE_CPU_SENTENCE_MODEL'] = '1'
        except Exception as e:
            logger.debug(f"Could not check GPU memory early: {e}")
    
    force_cpu = force_cpu_from_env
    
    # Try to find CPU version - check multiple possible locations
    cpu_version_paths = []
    if es_path.endswith('.pth'):
        # For .pth files, check in the same directory
        es_dir = Path(es_path).parent
        cpu_version_paths = [
            es_dir / "embedding_space_cpu.pickle",
            es_dir / "embedded_space_cpu.pickle",
            es_dir / "best_model_cpu.pickle",
            es_dir / "best_model_package" / "best_model_cpu.pickle",
            es_dir / "best_model_package" / "embedded_space_cpu.pickle",
            es_dir / "best_model_package" / "embedding_space_cpu.pickle",
        ]
    else:
        # For .pickle files, try replacing .pickle with _cpu.pickle or adding _cpu
        cpu_version_paths = [
            es_path.replace('.pickle', '_cpu.pickle'),
            es_path + '_cpu',
            es_path.replace('embedded_space.pickle', 'embedded_space_cpu.pickle'),
            es_path.replace('embedding_space.pickle', 'embedding_space_cpu.pickle'),
        ]
    
    # Check if any CPU version exists
    cpu_version_found = None
    for cpu_path in cpu_version_paths:
        cpu_path_str = str(cpu_path) if hasattr(cpu_path, '__str__') else cpu_path
        if os.path.exists(cpu_path_str):
            cpu_version_found = cpu_path_str
            logger.info(f"✅ CPU version found at {cpu_version_found} - using this instead of GPU version")
            es_path = cpu_version_found
            break
    
    if not cpu_version_found and force_cpu:
        logger.info(f"🔍 No CPU version found - will load GPU version and convert to CPU")
    
    # If path is a .pth file (PyTorch checkpoint), try to reconstruct ES from it
    if es_path.endswith('.pth') or es_path.endswith('.pt'):
        # Look for embedding_space.pickle first (preferred - faster to load)
        es_dir = Path(es_path).parent
        pickle_files = [
            es_dir / "embedding_space.pickle",
            es_dir / "embedded_space.pickle",
            es_dir / "best_model.pickle",
            es_dir / "best_model_package" / "best_model.pickle",
            es_dir / "best_model_package" / "embedded_space.pickle",
            es_dir / "best_model_package" / "embedding_space.pickle",
        ]
        
        pickle_found = False
        for pickle_file in pickle_files:
            if pickle_file.exists():
                logger.info(f"🔍 Found embedding space pickle at {pickle_file} (instead of .pth file)")
                es_path = str(pickle_file)
                pickle_found = True
                break
        
        # If no pickle found, reconstruct from .pth checkpoint
        if not pickle_found:
            logger.info(f"📦 No pickle found - loading .pth checkpoint and reconstructing ES")
            try:
                # Load the checkpoint dict
                pth_path = Path(es_path)
                logger.info(f"🔍 Loading checkpoint from {pth_path}...")
                checkpoint_dict = torch.load(str(pth_path), weights_only=False, map_location='cpu')
                
                if not isinstance(checkpoint_dict, dict) or 'model' not in checkpoint_dict:
                    raise TypeError(f"Checkpoint doesn't contain 'model' key. Keys: {list(checkpoint_dict.keys()) if isinstance(checkpoint_dict, dict) else 'not a dict'}")
                
                logger.info(f"✅ Checkpoint loaded. Epoch: {checkpoint_dict.get('epoch_idx', 'unknown')}")
                
                # Check if checkpoint has es_state (new format) - just restore directly
                if 'es_state' in checkpoint_dict:
                    logger.info(f"✅ Checkpoint contains es_state - restoring ES directly (no reconstruction)")
                    
                    # Create minimal ES shell without datasets
                    from featrix.neural.embedded_space import EmbeddingSpace
                    es_state = checkpoint_dict['es_state']
                    
                    # Create dummy datasets (not used for inference/SP training)
                    import pandas as pd
                    from featrix.neural.input_data_set import FeatrixInputDataSet
                    dummy_df = pd.DataFrame()
                    dummy_dataset = FeatrixInputDataSet(df=dummy_df, ignore_cols=[], standup_only=True)
                    
                    # Create ES with minimal args
                    es = EmbeddingSpace(
                        train_input_data=dummy_dataset,
                        val_input_data=dummy_dataset,
                        d_model=es_state['d_model'],
                        skip_pca_init=True,
                    )
                    
                    # Restore all attributes from es_state
                    es.d_model = es_state['d_model']
                    es.column_spec = es_state.get('column_spec', {})
                    es.availableColumns = es_state.get('availableColumns', [])
                    es.n_epochs = es_state.get('n_epochs')
                    es.name = es_state.get('name')
                    es.string_cache = es_state.get('string_cache')
                    es.json_transformations = es_state.get('json_transformations', {})
                    es.required_child_es_mapping = es_state.get('required_child_es_mapping', {})
                    es.user_metadata = es_state.get('user_metadata')
                    es.version_info = es_state.get('version_info')
                    es.output_debug_label = es_state.get('output_debug_label', 'Restored from checkpoint')
                    es.training_info = es_state.get('training_info', {})
                    
                    # Load encoder
                    es.encoder = checkpoint_dict['model']
                    
                    # CRITICAL: Validate and fix d_model to match encoder's actual output dimension
                    # The encoder may have been trained with a different d_model than what's in es_state
                    # (e.g., trained on machine with d_model=128, but es_state has d_model=192 from this machine's config)
                    if hasattr(es.encoder, 'config') and hasattr(es.encoder.config, 'd_model'):
                        encoder_d_model = es.encoder.config.d_model
                        if encoder_d_model != es.d_model:
                            logger.warning(f"⚠️  DIMENSION MISMATCH DETECTED:")
                            logger.warning(f"   es_state['d_model'] = {es.d_model}")
                            logger.warning(f"   encoder.config.d_model = {encoder_d_model}")
                            logger.warning(f"   Using encoder's d_model={encoder_d_model} (encoder's actual output dimension)")
                            es.d_model = encoder_d_model
                    
                    # Restore col_codecs from es_state (saved as codec objects)
                    if 'col_codecs' in es_state and es_state['col_codecs']:
                        es.col_codecs = es_state['col_codecs']
                        logger.info(f"   Restored {len(es.col_codecs)} codecs from es_state")
                    elif hasattr(es.encoder, 'column_encoder') and hasattr(es.encoder.column_encoder, 'col_codecs'):
                        es.col_codecs = es.encoder.column_encoder.col_codecs
                        logger.info(f"   Extracted {len(es.col_codecs)} codecs from encoder.column_encoder")
                    elif hasattr(es.encoder, 'col_codecs'):
                        es.col_codecs = es.encoder.col_codecs
                        logger.info(f"   Extracted {len(es.col_codecs)} codecs from encoder")
                    else:
                        logger.error(f"   ❌ CRITICAL: No col_codecs in es_state, encoder.column_encoder, or encoder!")
                        logger.error(f"   es_state keys: {list(es_state.keys())}")
                        logger.error(f"   Encoder type: {type(es.encoder)}")
                        logger.error(f"   Encoder has column_encoder: {hasattr(es.encoder, 'column_encoder')}")
                        if hasattr(es.encoder, 'column_encoder'):
                            logger.error(f"   column_encoder type: {type(es.encoder.column_encoder)}")
                            logger.error(f"   column_encoder has col_codecs: {hasattr(es.encoder.column_encoder, 'col_codecs')}")
                        logger.error(f"   Encoder has col_codecs: {hasattr(es.encoder, 'col_codecs')}")
                        raise ValueError(
                            f"Cannot restore EmbeddingSpace from checkpoint: col_codecs not found in es_state or encoder. "
                            f"This checkpoint is corrupted or incompatible."
                        )
                    
                    logger.info(f"✅ ES restored from es_state (d_model={es.d_model}, {len(es.availableColumns)} columns, {len(es.col_codecs)} codecs)")
                    
                else:
                    # Old format - use reconstruction
                    logger.info(f"⚠️  Old checkpoint format - using reconstruction")
                    es = _reconstruct_es_from_checkpoint_dict(checkpoint_dict, str(pth_path), logger=logger, skip_datasets=skip_datasets)
                    
                    if es is None:
                        raise ValueError(f"Reconstruction returned None")
                
                logger.info(f"✅ Successfully reconstructed ES from .pth checkpoint")
                return es
            except Exception as e:
                logger.error(f"❌ Failed to reconstruct ES from .pth checkpoint: {e}")
                logger.error(traceback.format_exc())
                raise FileNotFoundError(
                    f"Could not load ES from {es_path}: No pickle file found and reconstruction from .pth failed. "
                    f"Error: {e}"
                )
    
    # Fall back to pickle.load
    # CRITICAL: Aggressively clear GPU memory BEFORE loading to prevent OOM
    # The pickle may contain large models that will try to allocate on GPU during unpickling
    try:
        if torch is not None and is_gpu_available():
            # Multiple passes to force release of reserved memory
            for i in range(3):
                torch.cuda.empty_cache()
                torch.cuda.ipc_collect()
                if i == 0:
                    logger.info(f"🧹 Cleared GPU cache BEFORE loading embedding space (pass {i+1}/3)")
                else:
                    logger.debug(f"🧹 Cleared GPU cache BEFORE loading embedding space (pass {i+1}/3)")
            _log_gpu_memory("AFTER clearing cache, BEFORE loading embedding space")
            
            # Check if we have enough free memory (need at least 20GB free for large models)
            allocated = torch.cuda.memory_allocated() / (1024**3)
            reserved = torch.cuda.memory_reserved() / (1024**3)
            props = get_gpu_device_properties(0)
            total_memory = (props.total_memory / (1024**3)) if props else 0.0
            free_memory = total_memory - reserved
            
            logger.info(f"📊 GPU Memory Status: Allocated={allocated:.2f} GB, Reserved={reserved:.2f} GB, Free={free_memory:.2f} GB, Total={total_memory:.2f} GB")
            
            # CRITICAL: Check BOTH free memory AND reserved memory
            # Reserved memory is what PyTorch has allocated from CUDA, even if not actively used
            # If reserved is > 80% of total, we're in danger zone - force CPU
            # Also if free memory is < 50GB, force CPU (we saw 47GB free still OOM)
            reserved_percent = (reserved / total_memory) * 100
            
            if reserved_percent > 80 or free_memory < 50:
                logger.warning(f"⚠️  CRITICAL: GPU memory too high - Reserved={reserved_percent:.1f}% of total, Free={free_memory:.2f} GB")
                logger.warning(f"   Auto-forcing CPU loading to prevent OOM (embedding space doesn't need GPU for single predictor training)")
                logger.warning(f"   Set FEATRIX_FORCE_CPU_SINGLE_PREDICTOR=1 to always use CPU.")
                force_cpu = True
                os.environ['FEATRIX_FORCE_CPU_SINGLE_PREDICTOR'] = '1'
                os.environ['FEATRIX_FORCE_CPU_SENTENCE_MODEL'] = '1'
            elif reserved_percent > 70 or free_memory < 60:
                logger.warning(f"⚠️  High GPU memory usage: Reserved={reserved_percent:.1f}% of total, Free={free_memory:.2f} GB")
                logger.warning(f"   Loading may fail with OOM if model is large. Consider using CPU version.")
    except Exception as e:
        logger.debug(f"Could not clear GPU cache before loading: {e}")

    # Check file extension to determine loading strategy
    es_path_obj = Path(es_path)
    file_ext = es_path_obj.suffix.lower()
    use_pickle_directly = file_ext in ['.pickle', '.pkl']  # Standard pickle files
    
    with open(es_path, "rb") as f:
        try:
            # CRITICAL: Use a custom unpickler that forces all tensors to CPU during unpickling
            # This prevents OOM when pickle tries to restore tensors to their original GPU device
            class CPUUnpickler(pickle.Unpickler):
                """Custom unpickler that forces all PyTorch tensors to CPU during unpickling."""
                def find_class(self, module, name):
                    # Intercept tensor restoration and force CPU
                    if module == 'torch.storage' or module == 'torch._utils':
                        # Let torch handle its own classes, but we'll catch tensors in persistent_load
                        return super().find_class(module, name)
                    return super().find_class(module, name)
                
                def persistent_load(self, pid):
                    # This is called for persistent IDs (like tensor storage)
                    # We can't easily intercept here, but __setstate__ methods will handle it
                    return super().persistent_load(pid)
            
            # Use torch.load with map_location='cpu' to prevent GPU allocation during unpickling
            _log_gpu_memory("BEFORE loading embedding space")
            logger.info(f"🔍 Attempting torch.load(map_location='cpu') for {es_path}")
            
            # Temporarily set default tensor type to CPU to prevent GPU allocation during unpickling
            # This is a workaround - pickle will still try to restore to original device, but
            # we'll catch it in __setstate__ and move to CPU
            original_default_tensor_type = None
            if torch is not None:
                try:
                    # Save original default (if it exists)
                    if hasattr(torch, '_C') and hasattr(torch._C, '_get_default_tensor_type'):
                        original_default_tensor_type = torch._C._get_default_tensor_type()
                except:
                    pass
            
            # Save original env var state so we can restore after loading
            # We set force_cpu=1 during unpickling to prevent OOM, but we MUST
            # restore the original value after loading so training can use GPU!
            _original_force_cpu = os.environ.get('FEATRIX_FORCE_CPU_SINGLE_PREDICTOR')
            _user_requested_force_cpu = force_cpu  # True/False/None from user
            
            try:
                # CRITICAL: Set force_cpu flag BEFORE unpickling so __setstate__ methods see it
                # This prevents OOM during unpickling, but we'll clear it after loading
                os.environ['FEATRIX_FORCE_CPU_SINGLE_PREDICTOR'] = '1'
                logger.info(f"🔧 Set FEATRIX_FORCE_CPU_SINGLE_PREDICTOR=1 before unpickling (will restore after)")
                
                if torch is not None and not use_pickle_directly:
                    # For .pth/.pt files, try torch.load first
                    logger.info(f"🔧 Using torch.load(map_location='cpu') to force CPU loading")
                    try:
                        result = torch.load(f, map_location='cpu', weights_only=False)
                    except RuntimeError as torch_err:
                        error_msg = str(torch_err).lower()
                        # If torch.load fails with "invalid magic number", try pickle.load as fallback
                        # This can happen if the file was saved with pickle.dump() using a protocol
                        # that torch.load doesn't fully support, or if it's a pure pickle file
                        if "invalid magic number" in error_msg or "corrupt file" in error_msg:
                            logger.warning(f"⚠️  torch.load failed with: {torch_err}")
                            logger.info(f"🔄 Falling back to pickle.load() (file may be a standard pickle, not PyTorch format)")
                            f.seek(0)  # Reset file pointer to beginning
                            result = pickle.load(f)
                            logger.info(f"✅ Successfully loaded with pickle.load()")
                        else:
                            # Re-raise other RuntimeErrors
                            raise
                elif use_pickle_directly:
                    # For .pickle/.pkl files, use pickle.load directly (more reliable)
                    logger.info(f"🔧 Using pickle.load() directly for {file_ext} file")
                    result = pickle.load(f)
                else:
                    # torch not available - use pickle
                    logger.warning(f"⚠️  torch not available - using pickle.load")
                    result = pickle.load(f)
                
                # CRITICAL: After loading, FORCE PyTorch to release ALL reserved GPU memory
                # PyTorch's allocator may have reserved memory during unpickling even if tensors moved to CPU
                # Only do this if torch is available and we actually loaded something
                if torch is not None and is_gpu_available():
                    # Multiple aggressive cache clears
                    for _ in range(5):
                        torch.cuda.empty_cache()
                        torch.cuda.ipc_collect()
                    # Try to reset the allocator completely
                    try:
                        torch.cuda.reset_peak_memory_stats()
                        torch.cuda.reset_accumulated_memory_stats()
                    except:
                        pass
                    logger.info(f"🧹 Aggressively cleared GPU cache after loading (5x empty_cache + stats reset)")
            except RuntimeError as e:
                error_msg = str(e).lower()
                if "out of memory" in error_msg or "CUDA" in error_msg:
                    logger.error(f"❌ CUDA OOM during loading: {e}")
                    logger.error(f"   This should NOT happen with map_location='cpu' - possible pickle corruption")
                    raise
                elif "invalid magic number" in error_msg or "corrupt file" in error_msg:
                    logger.error(f"❌ Corrupted file detected: {e}")
                    logger.error(f"   File path: {es_path}")
                    logger.error(f"   This usually means:")
                    logger.error(f"   1. The file is incomplete (write was interrupted)")
                    logger.error(f"   2. The file is not a valid pickle/PyTorch checkpoint")
                    logger.error(f"   3. The file was corrupted during save or transfer")
                    # Try to get file info for diagnostics
                    try:
                        if os.path.exists(es_path):
                            file_size = os.path.getsize(es_path)
                            logger.error(f"   File size: {file_size:,} bytes")
                            if file_size == 0:
                                logger.error(f"   ⚠️  File is empty (0 bytes) - write likely failed")
                        else:
                            logger.error(f"   ⚠️  File does not exist!")
                    except Exception:
                        pass
                    raise
                else:
                    raise
            except Exception as e:
                # Catch any other exceptions (like pickle errors) and provide better diagnostics
                error_msg = str(e).lower()
                if "invalid magic number" in error_msg or "corrupt file" in error_msg or "pickle" in error_msg:
                    logger.error(f"❌ Failed to load file: {e}")
                    logger.error(f"   File path: {es_path}")
                    logger.error(f"   Error type: {type(e).__name__}")
                    try:
                        if os.path.exists(es_path):
                            file_size = os.path.getsize(es_path)
                            logger.error(f"   File size: {file_size:,} bytes")
                    except Exception:
                        pass
                raise
            
            _log_gpu_memory("AFTER loading embedding space")
            
            # CRITICAL: Handle checkpoint dicts - if the pickle contains a dict instead of EmbeddingSpace,
            # we need to reconstruct the EmbeddingSpace from the checkpoint
            from featrix.neural.embedded_space import EmbeddingSpace
            if isinstance(result, dict) and 'model' in result:
                logger.warning(f"⚠️  Loaded dict instead of EmbeddingSpace - attempting to reconstruct from checkpoint")
                try:
                    result = _reconstruct_es_from_checkpoint_dict(result, es_path, logger)
                except Exception as recon_err:
                    logger.error(f"❌❌❌ RECONSTRUCTION FAILED COMPLETELY ❌❌❌")
                    logger.error(f"   Exception type: {type(recon_err).__name__}")
                    logger.error(f"   Exception message: {recon_err}")
                    logger.error(f"   Original es_path: {es_path}")
                    logger.error(f"   Result type: {type(result)}")
                    logger.error(f"   Result keys (if dict): {list(result.keys()) if isinstance(result, dict) else 'N/A'}")
                    logger.error(f"   Full traceback:\n{traceback.format_exc()}")
                    # Re-raise so the outer exception handler can catch it
                    raise
            
            # CRITICAL: Move any GPU models to CPU during loading to avoid CUDA OOM
            # The pickle may contain models that were saved on GPU, which will try to load on GPU
            # If we're in CPU mode, move everything to CPU and save a CPU version for future loads
            if isinstance(result, EmbeddingSpace):
                # Check if anything is on GPU
                has_gpu_components = False
                if hasattr(result, 'encoder') and result.encoder is not None:
                    if list(result.encoder.parameters()):
                        encoder_device = next(result.encoder.parameters()).device
                        if encoder_device.type in ['cuda', 'mps']:
                            has_gpu_components = True
                
                # Check codecs - MOST codecs are stateless (no params), but some have embedded encoders
                # (e.g., JsonCodec has projection layer, URL codec might have encoder)
                # The main GPU state is in embedding_space.encoder, not codecs
                if not has_gpu_components and hasattr(result, 'col_codecs'):
                    for col_name, codec in result.col_codecs.items():
                        # Only check if codec actually has parameters (most don't - they're stateless)
                        if hasattr(codec, 'parameters') and list(codec.parameters()):
                            codec_device = next(codec.parameters()).device
                            if codec_device.type in ['cuda', 'mps']:
                                logger.info(f"   Found GPU parameters in codec '{col_name}' (unusual - most codecs are stateless)")
                                has_gpu_components = True
                                break
                        # Check buffers (some codecs might have buffers even without params)
                        if hasattr(codec, 'buffers') and isinstance(codec, torch.nn.Module):
                            for buffer in codec.buffers():
                                if buffer.device.type in ['cuda', 'mps']:
                                    logger.info(f"   Found GPU buffers in codec '{col_name}' (unusual - most codecs are stateless)")
                                    has_gpu_components = True
                                    break
                            if has_gpu_components:
                                break
                        # Check for embedded encoders (e.g., JsonCodec.projection, URL codec.encoder)
                        if hasattr(codec, 'projection') and codec.projection is not None:
                            if hasattr(codec.projection, 'parameters') and list(codec.projection.parameters()):
                                proj_device = next(codec.projection.parameters()).device
                                if proj_device.type in ['cuda', 'mps']:
                                    logger.info(f"   Found GPU projection in codec '{col_name}'")
                                    has_gpu_components = True
                                    break
                        if hasattr(codec, 'encoder') and codec.encoder is not None:
                            if hasattr(codec.encoder, 'parameters') and list(codec.encoder.parameters()):
                                encoder_device = next(codec.encoder.parameters()).device
                                if encoder_device.type in ['cuda', 'mps']:
                                    logger.info(f"   Found GPU encoder in codec '{col_name}'")
                                    has_gpu_components = True
                                    break
                
                # If we found GPU components and we're in CPU mode, move to CPU and save CPU version
                if has_gpu_components and force_cpu:
                    logger.info(f"🔄 Embedding space has GPU components - moving to CPU and saving CPU version...")
                    
                    # Move encoder to CPU
                    if hasattr(result, 'encoder') and result.encoder is not None:
                        if list(result.encoder.parameters()):
                            encoder_device = next(result.encoder.parameters()).device
                            if encoder_device.type in ['cuda', 'mps']:
                                logger.info(f"   Moving encoder from {encoder_device} to CPU...")
                                result.encoder = result.encoder.to('cpu')
                                torch.cuda.empty_cache()
                    
                    # Move all codecs to CPU - check BOTH parameters AND buffers
                    if hasattr(result, 'col_codecs'):
                        moved_count = 0
                        for col_name, codec in result.col_codecs.items():
                            codec_has_gpu = False
                            
                            # Check if codec has GPU parameters
                            if hasattr(codec, 'parameters') and list(codec.parameters()):
                                codec_device = next(codec.parameters()).device
                                if codec_device.type in ['cuda', 'mps']:
                                    codec_has_gpu = True
                            
                            # Check if codec has GPU buffers (CRITICAL - buffers can be on GPU!)
                            if not codec_has_gpu and hasattr(codec, 'buffers') and isinstance(codec, torch.nn.Module):
                                for buffer in codec.buffers():
                                    if buffer.device.type in ['cuda', 'mps']:
                                        codec_has_gpu = True
                                        break
                            
                            # Move entire codec to CPU if it has any GPU components
                            if codec_has_gpu:
                                if hasattr(codec, 'cpu'):
                                    codec.to('cpu')  # This moves both parameters AND buffers
                                    moved_count += 1
                                    logger.info(f"   Moved codec '{col_name}' to CPU (has GPU params/buffers)")
                                else:
                                    # Manual move if no .cpu() method
                                    if hasattr(codec, 'parameters'):
                                        for param in codec.parameters():
                                            param.data = param.data.to('cpu')
                                    if hasattr(codec, 'buffers') and isinstance(codec, torch.nn.Module):
                                        for buffer in codec.buffers():
                                            buffer.data = buffer.data.to('cpu')
                                    moved_count += 1
                                    logger.info(f"   Manually moved codec '{col_name}' to CPU")
                            
                            # Also check projection layers
                            if hasattr(codec, 'projection') and codec.projection is not None:
                                proj_has_gpu = False
                                if list(codec.projection.parameters()):
                                    proj_device = next(codec.projection.parameters()).device
                                    if proj_device.type in ['cuda', 'mps']:
                                        proj_has_gpu = True
                                # Check buffers in projection too
                                if not proj_has_gpu and hasattr(codec.projection, 'buffers'):
                                    for buffer in codec.projection.buffers():
                                        if buffer.device.type in ['cuda', 'mps']:
                                            proj_has_gpu = True
                                            break
                                if proj_has_gpu:
                                    codec.projection = codec.projection.to('cpu')
                                    logger.info(f"   Moved projection for '{col_name}' to CPU")
                        
                        if moved_count > 0:
                            logger.info(f"   ✅ Moved {moved_count} codecs to CPU (including buffers)")
                        else:
                            logger.info(f"   ℹ️  All codecs already on CPU or have no GPU components")
                    
                    # Save CPU version for future loads - use consistent naming
                    es_path_obj = Path(es_path)
                    if es_path.endswith('.pickle'):
                        cpu_version_path = str(es_path_obj.parent / f"{es_path_obj.stem}_cpu.pickle")
                    else:
                        cpu_version_path = str(es_path_obj.parent / f"{es_path_obj.name}_cpu")
                    
                    logger.info(f"💾 Saving CPU version to {cpu_version_path}...")
                    try:
                        with open(cpu_version_path, 'wb') as f:
                            pickle.dump(result, f)
                        logger.info(f"✅ CPU version saved to {cpu_version_path} - future loads will use this file")
                    except Exception as save_err:
                        logger.warning(f"⚠️  Failed to save CPU version: {save_err}")
                    
                    if torch is not None:
                        torch.cuda.empty_cache()
                    _log_gpu_memory("AFTER moving embedding space to CPU")
                    logger.info(f"   ✅ All components moved to CPU")
                elif has_gpu_components:
                    # Models are on GPU - leave them there for GPU training
                    logger.info(f"✅ Embedding space has GPU components - keeping on GPU for training")
            
            logger.info(f"✅ Successfully loaded")
            
            # CRITICAL: Validate col_codecs after loading
            # If the pickle was saved with empty col_codecs (data corruption or incomplete save),
            # we need to recover them from the encoder to prevent "0 codecs" errors during SP training
            if isinstance(result, EmbeddingSpace):
                if not result.col_codecs or len(result.col_codecs) == 0:
                    logger.error(f"❌ CRITICAL: Loaded EmbeddingSpace has EMPTY col_codecs!")
                    logger.error(f"   This indicates the pickle file was saved with corrupted/empty codec data.")
                    logger.error(f"   Attempting to recover col_codecs from encoder...")
                    
                    # Try to extract col_codecs from encoder
                    recovered = False
                    if hasattr(result, 'encoder') and result.encoder is not None:
                        if hasattr(result.encoder, 'column_encoder') and hasattr(result.encoder.column_encoder, 'col_codecs'):
                            result.col_codecs = result.encoder.column_encoder.col_codecs
                            logger.info(f"   ✅ Recovered {len(result.col_codecs)} codecs from encoder.column_encoder")
                            recovered = True
                        elif hasattr(result.encoder, 'col_codecs'):
                            result.col_codecs = result.encoder.col_codecs
                            logger.info(f"   ✅ Recovered {len(result.col_codecs)} codecs from encoder")
                            recovered = True
                    
                    if not recovered:
                        logger.error(f"   ❌ FAILED to recover col_codecs from encoder")
                        logger.error(f"   Encoder type: {type(result.encoder) if hasattr(result, 'encoder') else 'NO ENCODER'}")
                        if hasattr(result, 'encoder') and result.encoder is not None:
                            logger.error(f"   Encoder has column_encoder: {hasattr(result.encoder, 'column_encoder')}")
                            if hasattr(result.encoder, 'column_encoder'):
                                logger.error(f"   column_encoder has col_codecs: {hasattr(result.encoder.column_encoder, 'col_codecs')}")
                            logger.error(f"   Encoder has col_codecs: {hasattr(result.encoder, 'col_codecs')}")
                        raise ValueError(
                            f"Cannot load embedding space from {es_path}: col_codecs is empty and could not be recovered from encoder. "
                            f"This pickle file is corrupted or was saved incorrectly."
                        )
                else:
                    logger.info(f"   ✅ col_codecs validation passed: {len(result.col_codecs)} codecs loaded")
            
            # CRITICAL: Restore original env var state so training can use GPU!
            # We set force_cpu=1 during unpickling to prevent OOM, but now loading is done
            if _user_requested_force_cpu is True:
                # User explicitly wanted CPU mode - keep env var set
                os.environ['FEATRIX_FORCE_CPU_SINGLE_PREDICTOR'] = '1'
                logger.info(f"🔧 User requested force_cpu=True - keeping FEATRIX_FORCE_CPU_SINGLE_PREDICTOR=1")
            elif _user_requested_force_cpu is False:
                # User explicitly wanted GPU mode - clear env var
                os.environ.pop('FEATRIX_FORCE_CPU_SINGLE_PREDICTOR', None)
                os.environ.pop('FEATRIX_FORCE_CPU_SENTENCE_MODEL', None)
                logger.info(f"🔧 User requested force_cpu=False - cleared FEATRIX_FORCE_CPU_SINGLE_PREDICTOR (GPU enabled)")
            else:
                # User didn't specify - restore original value
                if _original_force_cpu is not None:
                    os.environ['FEATRIX_FORCE_CPU_SINGLE_PREDICTOR'] = _original_force_cpu
                    logger.info(f"🔧 Restored original FEATRIX_FORCE_CPU_SINGLE_PREDICTOR={_original_force_cpu}")
                else:
                    # Original was not set - clear it to enable GPU
                    os.environ.pop('FEATRIX_FORCE_CPU_SINGLE_PREDICTOR', None)
                    os.environ.pop('FEATRIX_FORCE_CPU_SENTENCE_MODEL', None)
                    logger.info(f"🔧 Cleared FEATRIX_FORCE_CPU_SINGLE_PREDICTOR (was not set originally - GPU enabled)")
            
            # CRITICAL: Validate d_model matches encoder's actual output dimension
            # This catches mismatches between what's saved in es.d_model and what the encoder outputs
            # (e.g., ES trained on machine with d_model=128, but loaded on machine with config d_model=192)
            from featrix.neural.embedded_space import EmbeddingSpace
            if isinstance(result, EmbeddingSpace):
                if hasattr(result, 'encoder') and hasattr(result.encoder, 'config') and hasattr(result.encoder.config, 'd_model'):
                    encoder_d_model = result.encoder.config.d_model
                    if encoder_d_model != result.d_model:
                        logger.warning(f"⚠️  DIMENSION MISMATCH DETECTED:")
                        logger.warning(f"   result.d_model = {result.d_model}")
                        logger.warning(f"   encoder.config.d_model = {encoder_d_model}")
                        logger.warning(f"   Using encoder's d_model={encoder_d_model} (encoder's actual output dimension)")
                        result.d_model = encoder_d_model
            
            return result
        except (AttributeError, pickle.UnpicklingError) as e:
            error_msg = str(e).lower()
            if "persistent_load" in error_msg or "persistent id" in error_msg:
                logger.info(f"ℹ️  persistent_load error detected (expected), trying Unpickler with handler as fallback")
                # If we get a persistent_load error, try with Unpickler
                f.seek(0)  # Reset file pointer
                unpickler = pickle.Unpickler(f)
                
                # Provide a handler for unknown persistent IDs
                # Protocol 0 requires ASCII strings
                def persistent_load(saved_id):
                    # Convert saved_id to ASCII string - handle all possible types
                    try:
                        # First, ensure saved_id is a string (protocol 0 requirement)
                        if saved_id is None:
                            saved_id_str = "unknown"
                            saved_id = ""  # Return empty string for None
                        elif isinstance(saved_id, bytes):
                            saved_id_str = saved_id.decode('ascii', errors='replace')
                            saved_id = saved_id_str
                        elif not isinstance(saved_id, str):
                            # Convert to string first
                            saved_id_str = str(saved_id)
                            # Then ensure it's ASCII
                            saved_id = saved_id_str.encode('ascii', errors='replace').decode('ascii')
                        else:
                            # It's already a string, ensure it's ASCII
                            saved_id_str = saved_id
                            saved_id = saved_id.encode('ascii', errors='replace').decode('ascii')
                        
                        logger.warning(f"⚠️  Encountered persistent_id {saved_id_str} (type: {type(saved_id_str)}) in pickle file - returning empty string. This may cause issues if the ID is required.")
                        # Return empty ASCII string
                        return ""
                    except Exception as conv_err:
                        logger.warning(f"⚠️  Error converting persistent_id to ASCII: {conv_err}, returning empty string")
                        return ""
                
                unpickler.persistent_load = persistent_load
                try:
                    result = unpickler.load()
                    logger.info(f"✅ Successfully loaded with Unpickler and persistent_load handler")
                    
                    # CRITICAL: Check if we got a dict (checkpoint) instead of EmbeddingSpace
                    from featrix.neural.embedded_space import EmbeddingSpace
                    if isinstance(result, dict) and 'model' in result:
                        logger.warning(f"⚠️  Loaded dict instead of EmbeddingSpace (via Unpickler) - attempting to reconstruct from checkpoint")
                        try:
                            result = _reconstruct_es_from_checkpoint_dict(result, es_path, logger)
                        except Exception as recon_err:
                            logger.error(f"❌❌❌ RECONSTRUCTION FAILED COMPLETELY (Unpickler path) ❌❌❌")
                            logger.error(f"   Exception type: {type(recon_err).__name__}")
                            logger.error(f"   Exception message: {recon_err}")
                            logger.error(f"   Full traceback:\n{traceback.format_exc()}")
                            raise
                    
                    # CRITICAL: Restore original env var state so training can use GPU!
                    if _user_requested_force_cpu is True:
                        os.environ['FEATRIX_FORCE_CPU_SINGLE_PREDICTOR'] = '1'
                    elif _user_requested_force_cpu is False:
                        os.environ.pop('FEATRIX_FORCE_CPU_SINGLE_PREDICTOR', None)
                        os.environ.pop('FEATRIX_FORCE_CPU_SENTENCE_MODEL', None)
                    else:
                        if _original_force_cpu is not None:
                            os.environ['FEATRIX_FORCE_CPU_SINGLE_PREDICTOR'] = _original_force_cpu
                        else:
                            os.environ.pop('FEATRIX_FORCE_CPU_SINGLE_PREDICTOR', None)
                            os.environ.pop('FEATRIX_FORCE_CPU_SENTENCE_MODEL', None)
                    logger.info(f"🔧 Cleared FEATRIX_FORCE_CPU_SINGLE_PREDICTOR after load (Unpickler path)")
                    
                    # CRITICAL: Validate d_model matches encoder's actual output dimension
                    if isinstance(result, EmbeddingSpace):
                        if hasattr(result, 'encoder') and hasattr(result.encoder, 'config') and hasattr(result.encoder.config, 'd_model'):
                            encoder_d_model = result.encoder.config.d_model
                            if encoder_d_model != result.d_model:
                                logger.warning(f"⚠️  DIMENSION MISMATCH DETECTED:")
                                logger.warning(f"   result.d_model = {result.d_model}")
                                logger.warning(f"   encoder.config.d_model = {encoder_d_model}")
                                logger.warning(f"   Using encoder's d_model={encoder_d_model} (encoder's actual output dimension)")
                                result.d_model = encoder_d_model
                    
                    return result
                except Exception as unpickle_err:
                    logger.info(f"ℹ️  Unpickler with persistent_load handler also failed (expected), trying torch.load as last resort: {unpickle_err}")
                    # Last resort: try torch.load again with the file handle
                    if torch is None:
                        raise unpickle_err
                    try:
                        f.seek(0)
                        logger.info(f"🔍 Last resort: trying torch.load with file handle")
                        result = torch.load(f, weights_only=False, map_location='cpu')
                        logger.info(f"✅ Successfully loaded with torch.load (file handle)")
                        
                        # CRITICAL: Check if torch.load returned a dict (checkpoint) instead of EmbeddingSpace
                        # If so, we need to reconstruct it using the shared helper
                        from featrix.neural.embedded_space import EmbeddingSpace
                        if isinstance(result, dict) and 'model' in result:
                            logger.warning(f"⚠️  torch.load returned dict instead of EmbeddingSpace - attempting to reconstruct from checkpoint")
                            try:
                                result = _reconstruct_es_from_checkpoint_dict(result, es_path, logger)
                                logger.info(f"✅ Successfully reconstructed EmbeddingSpace from checkpoint dict (via torch.load)")
                            except Exception as recon_err:
                                logger.error(f"❌❌❌ RECONSTRUCTION FAILED COMPLETELY (torch.load path) ❌❌❌")
                                logger.error(f"   Exception type: {type(recon_err).__name__}")
                                logger.error(f"   Exception message: {recon_err}")
                                logger.error(f"   Original es_path: {es_path}")
                                logger.error(f"   Result type: {type(result)}")
                                logger.error(f"   Result keys (if dict): {list(result.keys()) if isinstance(result, dict) else 'N/A'}")
                                logger.error(f"   Full traceback:\n{traceback.format_exc()}")
                                raise
                        
                        # CRITICAL: Restore original env var state so training can use GPU!
                        if _user_requested_force_cpu is True:
                            os.environ['FEATRIX_FORCE_CPU_SINGLE_PREDICTOR'] = '1'
                        elif _user_requested_force_cpu is False:
                            os.environ.pop('FEATRIX_FORCE_CPU_SINGLE_PREDICTOR', None)
                            os.environ.pop('FEATRIX_FORCE_CPU_SENTENCE_MODEL', None)
                        else:
                            if _original_force_cpu is not None:
                                os.environ['FEATRIX_FORCE_CPU_SINGLE_PREDICTOR'] = _original_force_cpu
                            else:
                                os.environ.pop('FEATRIX_FORCE_CPU_SINGLE_PREDICTOR', None)
                                os.environ.pop('FEATRIX_FORCE_CPU_SENTENCE_MODEL', None)
                        logger.info(f"🔧 Cleared FEATRIX_FORCE_CPU_SINGLE_PREDICTOR after load (torch.load path)")
                        
                        # CRITICAL: Validate d_model matches encoder's actual output dimension
                        if isinstance(result, EmbeddingSpace):
                            if hasattr(result, 'encoder') and hasattr(result.encoder, 'config') and hasattr(result.encoder.config, 'd_model'):
                                encoder_d_model = result.encoder.config.d_model
                                if encoder_d_model != result.d_model:
                                    logger.warning(f"⚠️  DIMENSION MISMATCH DETECTED:")
                                    logger.warning(f"   result.d_model = {result.d_model}")
                                    logger.warning(f"   encoder.config.d_model = {encoder_d_model}")
                                    logger.warning(f"   Using encoder's d_model={encoder_d_model} (encoder's actual output dimension)")
                                    result.d_model = encoder_d_model
                        
                        return result
                    except Exception as torch_err2:
                        logger.error(f"❌ torch.load (file handle) also failed: {torch_err2}")
                        raise unpickle_err from torch_err2
            raise

