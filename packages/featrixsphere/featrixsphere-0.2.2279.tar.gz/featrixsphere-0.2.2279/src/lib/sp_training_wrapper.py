#!/usr/bin/env python3
"""
Wrapper script to run Single Predictor training in a non-daemon process.

This script is executed by Celery workers via fork/exec to create a new
session leader process for better GPU memory management and process isolation.
"""
import atexit
import json
import logging
import os
import signal
import socket
import sys
import traceback
from pathlib import Path

# CRITICAL: Redirect stderr to stdout IMMEDIATELY so all errors/crashes go to one log
sys.stderr = sys.stdout
print("🔧 STDERR REDIRECTED TO STDOUT - all output in one place!", flush=True)

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set up logging with same format as Celery job logging
# This ensures consistent log format in the job log file
logging.basicConfig(
    level=logging.INFO,
    format=f'%(asctime)s [{socket.gethostname()}] [%(levelname)-8s] %(name)-45s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    stream=sys.stdout  # Write to stdout (inherited from parent, redirected to log file)
)

logger = logging.getLogger(__name__)

from lib.single_predictor_training import train_single_predictor, LightSinglePredictorArgs


def cleanup_gpu_memory():
    """
    Clean up GPU memory on exit.
    
    This is called on exit to ensure we don't leave GPU memory allocated.
    """
    try:
        import torch
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
            logger.info("✅ GPU memory cache cleared")
    except Exception as e:
        logger.debug(f"Could not clear GPU cache: {e}")


if __name__ == "__main__":
    import argparse
    
    # Register cleanup to run on exit (normal or crash)
    atexit.register(cleanup_gpu_memory)
    
    # Also handle signals to ensure cleanup on kill/interrupt
    def signal_handler(signum, frame):
        logger.warning(f"⚠️  Received signal {signum} - cleaning up before exit")
        cleanup_gpu_memory()
        sys.exit(128 + signum)
    
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    parser = argparse.ArgumentParser(description='Single Predictor training wrapper')
    parser.add_argument('args_json_file', help='JSON file containing training arguments')
    parser.add_argument('--job-id', help='Job ID (visible in /proc for process identification)', default=None)
    parsed_args = parser.parse_args()
    
    args_file = parsed_args.args_json_file
    job_id = parsed_args.job_id
    
    # Store job_id in environment so child processes can inherit it
    # This makes it visible in /proc/<pid>/environ as well
    if job_id:
        os.environ['FEATRIX_JOB_ID'] = job_id
    
    # Load args from JSON file
    with open(args_file, 'r') as f:
        args_dict = json.load(f)
    
    # Create LightSinglePredictorArgs object
    args = LightSinglePredictorArgs(**args_dict)
    
    # Run training
    try:
        train_single_predictor(args)
        logger.info("✅ Training completed successfully")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Training failed: {e}")
        traceback.print_exc()
        # cleanup_gpu_memory() will be called automatically by atexit
        sys.exit(1)
