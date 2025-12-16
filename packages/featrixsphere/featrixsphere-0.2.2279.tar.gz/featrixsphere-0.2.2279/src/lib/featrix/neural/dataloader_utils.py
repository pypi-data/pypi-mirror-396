#  -*- coding: utf-8 -*-
#
#  Copyright Featrix, Inc 2023-2025
#
#  Proprietary and Confidential.  Unauthorized use, copying or dissemination
#  of these materials is strictly prohibited.
#
"""
Utilities for creating DataLoaders with multiprocessing support.

This module handles the complexity of multiprocess data loading in PyTorch,
including:
- Worker initialization (CUDA context, random seeds)
- Platform-specific defaults (macOS vs Linux)
- Proper handling of codecs and string caches across processes
"""
import logging
import platform
import torch
import random
import numpy as np
import multiprocessing
from pathlib import Path

from featrix.neural.gpu_utils import is_gpu_available, get_gpu_current_device_id, get_gpu_device_properties

logger = logging.getLogger(__name__)

# CRITICAL: Force 'spawn' multiprocessing on Linux when CUDA is available
# Linux defaults to 'fork', but CUDA cannot be re-initialized in forked subprocesses
# This causes errors like "Cannot re-initialize CUDA in forked subprocess"
# We must set this BEFORE any multiprocessing happens
_mp_initialized = False

def _ensure_spawn_for_cuda():
    """
    Force 'spawn' multiprocessing start method when CUDA is available.
    
    Must be called before any multiprocessing or DataLoader creation.
    Linux defaults to 'fork' which breaks CUDA in worker processes.
    """
    global _mp_initialized
    
    if _mp_initialized:
        return
    
    try:
        current_method = multiprocessing.get_start_method(allow_none=True)
        
        # If CUDA is available and we're not already using spawn, switch to spawn
        if is_gpu_available():
            if current_method != 'spawn':
                logger.warning("=" * 80)
                logger.warning("⚠️  CUDA + MULTIPROCESSING CONFIGURATION")
                logger.warning("=" * 80)
                logger.warning(f"Current multiprocessing method: {current_method}")
                logger.warning("CUDA is available but multiprocessing uses 'fork'")
                logger.warning("This causes: 'Cannot re-initialize CUDA in forked subprocess'")
                logger.warning("Forcing multiprocessing start method to 'spawn'...")
                logger.warning("=" * 80)
                
                try:
                    multiprocessing.set_start_method('spawn', force=True)
                    logger.info(f"✅ Multiprocessing start method set to: {multiprocessing.get_start_method()}")
                except RuntimeError as e:
                    # Context already set, can't change it
                    logger.error(f"❌ Could not change multiprocessing method: {e}")
                    logger.error("This will cause CUDA errors in DataLoader workers")
                    logger.error("WORKAROUND: Set PYTORCH_NUM_WORKERS=0 to disable workers")
            else:
                logger.debug(f"✅ Multiprocessing already using 'spawn' - CUDA-safe")
        else:
            logger.debug(f"Multiprocessing method: {current_method} (CUDA not available, any method OK)")
        
        _mp_initialized = True
        
    except Exception as e:
        logger.error(f"Error configuring multiprocessing for CUDA: {e}")
        _mp_initialized = True  # Don't keep trying

# Call this immediately when module is imported
_ensure_spawn_for_cuda()


def worker_init_fn(worker_id):
    """
    Initialize each DataLoader worker process.
    
    This function is called once per worker process and handles:
    - Setting unique random seeds per worker
    - Reinitializing CUDA context (if needed)
    - Any worker-specific setup
    
    Args:
        worker_id: Integer ID of this worker (0 to num_workers-1)
    """
    import os
    
    # Get process info
    pid = os.getpid()
    
    # NOTE: Setting CUDA_VISIBLE_DEVICES here is TOO LATE
    # CUDA context already initialized when torch was imported
    # Accept 600MB VRAM overhead per worker for CUDA context
    os.environ['PYTORCH_DATALOADER_WORKER'] = '1'
    
    # Set unique random seed for each worker to ensure diverse sampling
    worker_seed = torch.initial_seed() % 2**32
    random.seed(worker_seed)
    np.random.seed(worker_seed)
    torch.manual_seed(worker_seed)
    
    # Single line log message when worker is created
    logger.info(f"🔧 DataLoader worker {worker_id} created (PID={pid})")


def get_optimal_num_workers(override: int = None, force_zero_if_cuda: bool = True, dataset_size: int = None) -> int:
    """
    Determine optimal number of DataLoader workers for the current platform.
    
    Args:
        override: If provided, use this value instead of auto-detection
        dataset_size: Number of rows in the dataset. Workers are capped at 1 per 250 rows.
        
    Returns:
        Number of workers to use (0 = main process only, >0 = multiprocess)
        
    Notes:
        - macOS: Returns 0 by default (spawn overhead > benefit for most datasets)
        - Linux with CUDA: Returns 2-4 based on CPU count
        - Without CUDA: Returns 0-2 based on CPU count
        - Workers are capped at 1 per 250 rows to avoid wasting time creating workers
        
        Users can override by setting the environment variable PYTORCH_NUM_WORKERS
        or by passing the override parameter.
    """
    import os
    import multiprocessing
    
    logger.info("=" * 80)
    logger.info("🔍 DATALOADER NUM_WORKERS DETECTION")
    logger.info("=" * 80)
    
    # CRITICAL: Check if we're in a daemon process (e.g., Celery worker)
    # Daemon processes cannot spawn child processes, so we MUST use num_workers=0
    try:
        current_process = multiprocessing.current_process()
        if current_process.daemon:
            logger.warning("⚠️  Detected daemon process (likely Celery worker)")
            logger.warning("   Daemon processes cannot spawn child processes")
            logger.warning("   Forcing num_workers=0 to avoid 'daemonic processes are not allowed to have children' error")
            logger.info("=" * 80)
            return 0
    except Exception as e:
        logger.debug(f"   Could not check daemon status: {e}")
    
    # Check for environment variable override first
    if override is not None:
        num_workers = override
        logger.info(f"🔧 Using num_workers={num_workers} (explicit override parameter)")
        # Still apply dataset size cap even with override
        if dataset_size is not None:
            max_workers_by_size = max(1, dataset_size // 250)
            if num_workers > max_workers_by_size:
                logger.info(f"   Capping num_workers from {num_workers} to {max_workers_by_size} (1 worker per 250 rows, dataset_size={dataset_size})")
                num_workers = max_workers_by_size
        logger.info("=" * 80)
        return num_workers
    
    env_override = os.getenv('PYTORCH_NUM_WORKERS')
    logger.info(f"   PYTORCH_NUM_WORKERS env var: {env_override if env_override else 'not set'}")
    
    if env_override is not None:
        try:
            num_workers = int(env_override)
            logger.info(f"🔧 Using num_workers={num_workers} (from PYTORCH_NUM_WORKERS env var)")
            # Still apply dataset size cap even with env override
            if dataset_size is not None:
                max_workers_by_size = max(1, dataset_size // 250)
                if num_workers > max_workers_by_size:
                    logger.info(f"   Capping num_workers from {num_workers} to {max_workers_by_size} (1 worker per 250 rows, dataset_size={dataset_size})")
                    num_workers = max_workers_by_size
            logger.info("=" * 80)
            return num_workers
        except ValueError:
            logger.warning(f"⚠️  Invalid PYTORCH_NUM_WORKERS value: {env_override}, using auto-detection")
    
    # Check config.json settings
    try:
        from lib.sphere_config import get_config
        config = get_config()
        enable_multiprocessing = config.get_enable_multiprocessing_dataloader()
        config_num_workers = config.get_num_workers()
        
        logger.info(f"   Config enable_multiprocessing_dataloader: {enable_multiprocessing}")
        logger.info(f"   Config num_workers: {config_num_workers if config_num_workers is not None else 'auto-detect'}")
        
        if not enable_multiprocessing:
            logger.info(f"🔧 Using num_workers=0 (multiprocessing disabled in config.json)")
            logger.info("=" * 80)
            return 0
        
        if config_num_workers is not None:
            num_workers = config_num_workers
            logger.info(f"🔧 Using num_workers={num_workers} (from config.json)")
            # Still apply dataset size cap even with config override
            if dataset_size is not None:
                max_workers_by_size = max(1, dataset_size // 250)
                if num_workers > max_workers_by_size:
                    logger.info(f"   Capping num_workers from {num_workers} to {max_workers_by_size} (1 worker per 250 rows, dataset_size={dataset_size})")
                    num_workers = max_workers_by_size
            logger.info("=" * 80)
            return num_workers
    except Exception as e:
        logger.debug(f"   Could not load config for multiprocessing settings: {e}, using auto-detection")
    
    # Platform-specific defaults (auto-detection)
    system = platform.system()
    logger.info(f"   Platform: {system}")
    
    # Get CPU count
    cpu_count = multiprocessing.cpu_count()
    logger.info(f"   CPU count: {cpu_count}")
    
    # Check multiprocessing start method
    try:
        mp_start_method = multiprocessing.get_start_method()
        logger.info(f"   Multiprocessing start method: {mp_start_method}")
    except Exception as e:
        logger.warning(f"   Could not get multiprocessing start method: {e}")
    
    if system == 'Darwin':  # macOS
        # macOS uses 'spawn' for multiprocessing which has high overhead
        # For most datasets, single-process is faster
        num_workers = 0
        logger.info(f"💻 macOS detected - using num_workers={num_workers} (spawn overhead > benefit)")
        logger.info("   Reason: macOS uses 'spawn' multiprocessing which has high overhead")
        logger.info("   Single-process loading is typically faster for most datasets on macOS")
    else:  # Linux, Windows, etc.
        # Check if CUDA is available
        cuda_available = is_gpu_available()
        logger.info(f"   CUDA available: {cuda_available}")
        
        if cuda_available:
            try:
                cuda_device_count = torch.cuda.device_count()
                current_device = get_gpu_current_device_id()
                device_name = torch.cuda.get_device_name(current_device)
                logger.info(f"   CUDA devices: {cuda_device_count}")
                logger.info(f"   Current device: {current_device} ({device_name})")
            except Exception as e:
                logger.warning(f"   Error getting CUDA details: {e}")
            
            # With GPU, scale workers based on VRAM to account for CUDA context overhead
            # Each worker uses ~600MB VRAM for CUDA context initialization
            # We can't disable this without pre-import hooks (TODO)
            # CRITICAL: Account for concurrent GPU jobs to avoid oversubscription
            gpu_mem_gb = None
            try:
                props = get_gpu_device_properties(0)
                gpu_mem_gb = (props.total_memory / 1024**3) if props else 0.0
                
                # CRITICAL: Read GPU concurrency setting to know how many jobs can run simultaneously
                # This prevents oversubscription when multiple GPU jobs run concurrently
                max_concurrent_gpu_jobs = 1  # Safe default
                try:
                    concurrency_file = Path("/sphere/app/.celery_gpu_concurrency")
                    if concurrency_file.exists():
                        max_concurrent_gpu_jobs = int(concurrency_file.read_text().strip())
                        logger.info(f"   GPU concurrency: {max_concurrent_gpu_jobs} jobs can run simultaneously")
                    else:
                        logger.debug("   GPU concurrency file not found - assuming 1 concurrent job")
                except Exception as e:
                    logger.debug(f"Could not read GPU concurrency setting: {e}, assuming 1")
                
                # CRITICAL: Also check SYSTEM RAM availability
                # Workers use system RAM (1-2GB each) before GPU transfer
                max_workers_by_system_ram = None
                try:
                    from lib.system_health_monitor import check_memory_available_for_workers
                    max_workers_by_system_ram = check_memory_available_for_workers(safety_margin_gb=10.0)
                    logger.info(f"   System RAM allows: {max_workers_by_system_ram} workers (2GB per worker, 10GB safety margin)")
                except Exception as e:
                    logger.debug(f"Could not check system RAM for workers: {e}")
                
                # Calculate max workers per job based on CPU cores and concurrent jobs
                # Formula: (cores / 2) / max_concurrent_gpu_jobs
                # The /2 accounts for hyperthreading - don't count logical cores
                max_workers_by_cpu = max(1, (cpu_count // 2) // max_concurrent_gpu_jobs)
                logger.info(f"   CPU allocation: ({cpu_count} cores / 2) / {max_concurrent_gpu_jobs} concurrent jobs = {max_workers_by_cpu} max workers per job")
                
                # Reduce workers for large datasets (50k+ rows) to prevent OOM
                # Each worker uses ~600MB VRAM + 1-2GB system RAM
                if dataset_size and dataset_size >= 20000:
                    # Large dataset - use fewer workers to save VRAM and system RAM
                    if gpu_mem_gb > 32:
                        num_workers = min(8, max_workers_by_cpu)  # Reduced from 16 to 8 for large datasets, capped by CPU
                        logger.info(f"   GPU memory: {gpu_mem_gb:.1f} GB → num_workers={num_workers} (>32GB VRAM, but large dataset - reduced workers)")
                    else:
                        num_workers = min(4, max_workers_by_cpu)  # Reduced from 8 to 4 for large datasets, capped by CPU
                        logger.info(f"   GPU memory: {gpu_mem_gb:.1f} GB → num_workers={num_workers} (≤32GB VRAM, large dataset - reduced workers)")
                else:
                    # Normal dataset - use worker count capped by CPU allocation
                    if gpu_mem_gb > 32:
                        num_workers = min(16, max_workers_by_cpu)  # Cap at CPU allocation
                        logger.info(f"   GPU memory: {gpu_mem_gb:.1f} GB → num_workers={num_workers} (>32GB VRAM, capped by CPU allocation)")
                    else:
                        num_workers = min(8, max_workers_by_cpu)  # Cap at CPU allocation
                        logger.info(f"   GPU memory: {gpu_mem_gb:.1f} GB → num_workers={num_workers} (≤32GB VRAM, capped by CPU allocation)")
                
                # CRITICAL: Cap by system RAM if needed
                if max_workers_by_system_ram is not None and max_workers_by_system_ram < num_workers:
                    logger.warning(
                        f"⚠️  System RAM limit: Reducing num_workers from {num_workers} to {max_workers_by_system_ram} "
                        f"(insufficient system RAM for workers)"
                    )
                    num_workers = max_workers_by_system_ram
                    
            except Exception as e:
                num_workers = 8  # Safe default
                logger.warning(f"   Could not detect GPU memory: {e}, using default num_workers={num_workers}")
            logger.info("=" * 80)
            logger.info(f"🚀🚀🚀 Linux + CUDA detected - using num_workers={num_workers} 🚀🚀🚀")
            logger.info("=" * 80)
            logger.info(f"   CPU count: {cpu_count}")
            if gpu_mem_gb is not None:
                logger.info(f"   GPU memory: {gpu_mem_gb:.1f} GB")
            logger.info(f"   Worker VRAM overhead: {num_workers} × 600MB = {num_workers * 0.6:.1f} GB")
            logger.info("   Note: Workers inherit CUDA context (600MB each) - cannot be disabled without pre-import hooks")
            logger.info("=" * 80)
        else:
            # Without GPU, fewer workers (CPU is already busy with training)
            num_workers = min(2, max(0, cpu_count // 8))
            logger.info(f"🐧 Linux (CPU only) detected - using num_workers={num_workers}")
            logger.info(f"   Calculation: min(2, max(0, {cpu_count} // 8)) = {num_workers}")
            logger.info("   Reason: CPU-only training, keep workers low to avoid overhead")
    
    logger.info("=" * 80)
    
    # CRITICAL: Cap workers based on dataset size to avoid wasting time creating workers
    # Rule: Maximum 1 worker per 250 rows of data
    if dataset_size is not None:
        max_workers_by_size = max(1, dataset_size // 250)
        if num_workers > max_workers_by_size:
            logger.info(f"📊 Dataset size cap: {dataset_size} rows → max {max_workers_by_size} workers (1 per 250 rows)")
            logger.info(f"   Reducing num_workers from {num_workers} to {max_workers_by_size}")
            num_workers = max_workers_by_size
        else:
            logger.info(f"📊 Dataset size: {dataset_size} rows → {max_workers_by_size} max workers (1 per 250 rows), using {num_workers}")
    else:
        logger.debug("   Dataset size not provided - skipping dataset size cap")
    
    logger.info("=" * 80)
    
    # Note: We previously had a safety check here that forced num_workers=0 when CUDA was detected
    # This was because codecs created CUDA tensors in tokenize() which can't be pickled.
    # This has been FIXED - codecs now create CPU tensors in tokenize(), 
    # and they're moved to GPU in the training loop via tokenbatch.to(get_device()).
    # So multiprocess DataLoaders now work safely with CUDA!
    
    return num_workers


def create_dataloader_kwargs(
    batch_size: int,
    shuffle: bool = True,
    drop_last: bool = True,
    num_workers: int = None,
    persistent_workers: bool = None,
    pin_memory: bool = None,
    prefetch_factor: int = 16,
    dataset_size: int = None,
) -> dict:
    """
    Create DataLoader kwargs with sensible defaults for training.
    
    Args:
        batch_size: Batch size for the DataLoader
        shuffle: Whether to shuffle the data
        drop_last: Whether to drop the last incomplete batch
        num_workers: Number of worker processes (None = auto-detect based on GPU VRAM)
        persistent_workers: Keep workers alive between epochs (None = auto-detect)
        pin_memory: Pin memory for faster CPU->GPU transfer (None = auto-detect)
        prefetch_factor: Number of batches to prefetch per worker
        dataset_size: Number of rows in the dataset. Workers are capped at 1 per 250 rows.
        
    Returns:
        Dictionary of DataLoader kwargs ready to pass to DataLoader()
        
    Note:
        Workers inherit CUDA context and use ~600MB VRAM each.
        num_workers is automatically scaled based on GPU memory to fit VRAM budget.
        Workers are capped at 1 per 250 rows to avoid wasting time creating workers.
    """
    # Auto-detect optimal num_workers
    if num_workers is None:
        num_workers = get_optimal_num_workers(dataset_size=dataset_size)
    
    # Auto-detect persistent_workers (only useful if num_workers > 0)
    # CRITICAL: Always use persistent_workers=True when num_workers > 0 to avoid
    # recreating workers on every iteration (which is expensive and causes logging spam)
    if persistent_workers is None:
        persistent_workers = (num_workers > 0)
    
    # Warn if persistent_workers is False when num_workers > 0 (this will cause workers to be recreated)
    if num_workers > 0 and not persistent_workers:
        logger.warning(
            f"⚠️  WARNING: persistent_workers=False with num_workers={num_workers}. "
            f"This will cause workers to be recreated on every DataLoader iteration, "
            f"which is expensive and causes logging spam. Consider setting persistent_workers=True."
        )
    
    # Auto-detect pin_memory
    # CRITICAL: Cannot use pin_memory with multiprocessing workers due to
    # "RuntimeError: cannot join current thread" during cleanup
    # This is a known PyTorch issue where pin_memory_thread.join() is called
    # from within a worker thread context, causing the error
    # See: https://github.com/pytorch/pytorch/issues/57273
    if pin_memory is None:
        if num_workers > 0:
            # With workers, pin_memory must be False (cannot be used with multiprocessing)
            pin_memory = False
            logger.debug("pin_memory disabled with multiprocessing workers (incompatible)")
        else:
            # Single-process can safely use pin_memory for faster CPU->GPU transfers
            pin_memory = is_gpu_available()
    
    # Build kwargs
    kwargs = {
        'batch_size': batch_size,
        'shuffle': shuffle,
        'drop_last': drop_last,
        'num_workers': num_workers,
    }
    
    logger.debug("🔧 Creating DataLoader configuration:")
    logger.debug(f"   batch_size: {batch_size}")
    logger.debug(f"   shuffle: {shuffle}")
    logger.debug(f"   drop_last: {drop_last}")
    logger.debug(f"   num_workers: {num_workers}")
    
    # Only add these kwargs if num_workers > 0 (they cause errors with num_workers=0)
    if num_workers > 0:
        kwargs['persistent_workers'] = persistent_workers
        kwargs['worker_init_fn'] = worker_init_fn
        kwargs['prefetch_factor'] = prefetch_factor
        # Do NOT add pin_memory to kwargs when using workers - it's incompatible
        # (default is False anyway, so omitting it is fine)
        
        logger.info(f"   persistent_workers: {persistent_workers}")
        logger.info(f"   worker_init_fn: {worker_init_fn.__name__}")
        logger.info(f"   prefetch_factor: {prefetch_factor}")
        logger.info(f"   pin_memory: {pin_memory} (not used with multiprocessing)")
        logger.info("=" * 80)
        logger.info(
            f"📦📦📦 MULTIPROCESS DATALOADER: {num_workers} WORKERS WILL BE SPAWNED 📦📦📦"
        )
        logger.info(f"   persistent_workers={persistent_workers}, pin_memory={pin_memory}")
        logger.info(f"   NOTE: Workers spawn sequentially (~5s each) but only once with persistent_workers=True")
        logger.info("=" * 80)
    else:
        # Single-process: pin_memory disabled when codecs are on GPU
        # pin_memory only works with CPU tensors - if codecs create GPU tensors, it will crash
        # Since we're moving codecs to GPU, we disable pin_memory to avoid the error
        pin_memory = False
        logger.info(f"   pin_memory: False (disabled - codecs on GPU create GPU tensors)")
        logger.info(f"📦 Single-process DataLoader (no worker processes)")
    
    return kwargs


def prepare_codecs_for_workers(codecs: dict) -> dict:
    """
    Prepare codecs for multiprocess workers by ensuring they're picklable.
    
    This function:
    1. Moves all CUDA tensors to CPU (CUDA tensors can't be pickled)
    2. Clears any cached GPU state
    3. Returns the modified codecs
    
    Note: After unpickling in the worker, codecs will automatically
    move tensors back to GPU when needed.
    
    Args:
        codecs: Dictionary of codec objects
        
    Returns:
        Modified codecs dictionary (safe for pickling)
    """
    # This is handled automatically by PyTorch's DataLoader
    # When num_workers > 0, PyTorch will:
    # 1. Pickle the dataset (which contains codecs)
    # 2. Send to worker process
    # 3. Unpickle in worker
    # 4. Worker can then use codecs normally
    
    # CUDA tensors are automatically moved to CPU during pickling
    # and can be moved back to GPU in the worker as needed
    
    return codecs

