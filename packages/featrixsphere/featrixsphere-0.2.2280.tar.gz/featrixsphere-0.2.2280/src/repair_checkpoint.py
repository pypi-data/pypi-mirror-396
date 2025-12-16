#!/usr/bin/env python3
"""
Repair Corrupted Checkpoint File

This tool repairs corrupted .pth checkpoint files by:
1. Making a backup of the original file
2. Attempting to load and validate the checkpoint
3. If corrupted, trying to repair it by loading with different methods
4. If repair succeeds, saving the repaired checkpoint

Usage:
    python3 repair_checkpoint.py <checkpoint.pth> [--session-id <session_id>]
    
If --session-id is provided, will search for foundation_checkpoint_*.pth in that session's directory.
"""

import argparse
import logging
import shutil
import sys
import traceback
from datetime import datetime
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def make_backup(checkpoint_path: Path) -> Path:
    """Make a backup of the checkpoint file with timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = checkpoint_path.parent / f"{checkpoint_path.stem}.backup_{timestamp}{checkpoint_path.suffix}"
    
    logger.info(f"📦 Creating backup: {backup_path}")
    shutil.copy2(checkpoint_path, backup_path)
    logger.info(f"✅ Backup created: {backup_path}")
    
    return backup_path


def try_load_checkpoint(checkpoint_path: Path, method: str = "default") -> dict:
    """Try to load checkpoint with different methods."""
    import torch
    
    try:
        if method == "default":
            checkpoint = torch.load(str(checkpoint_path), weights_only=False, map_location='cpu')
        elif method == "weights_only":
            checkpoint = torch.load(str(checkpoint_path), weights_only=True, map_location='cpu')
        elif method == "pickle_protocol":
            # Try with different pickle protocol
            checkpoint = torch.load(str(checkpoint_path), weights_only=False, map_location='cpu', pickle_module=None)
        else:
            raise ValueError(f"Unknown method: {method}")
        
        logger.info(f"✅ Checkpoint loaded successfully with method: {method}")
        return checkpoint
    except Exception as e:
        logger.warning(f"⚠️  Failed to load with method {method}: {e}")
        return None


def validate_checkpoint(checkpoint: dict) -> bool:
    """Validate that checkpoint has required keys."""
    required_keys = ['model']
    optional_keys = ['epoch_idx', 'optimizer', 'scheduler', 'train_loss', 'val_loss']
    
    if not isinstance(checkpoint, dict):
        logger.error(f"❌ Checkpoint is not a dict, got: {type(checkpoint)}")
        return False
    
    missing_required = [key for key in required_keys if key not in checkpoint]
    if missing_required:
        logger.error(f"❌ Checkpoint missing required keys: {missing_required}")
        logger.error(f"   Available keys: {list(checkpoint.keys())}")
        return False
    
    logger.info(f"✅ Checkpoint validation passed")
    logger.info(f"   Required keys: {required_keys} ✅")
    present_optional = [key for key in optional_keys if key in checkpoint]
    if present_optional:
        logger.info(f"   Optional keys present: {present_optional}")
    
    return True


def repair_checkpoint(checkpoint_path: Path) -> bool:
    """Repair a corrupted checkpoint file."""
    logger.info(f"🔧 Repairing checkpoint: {checkpoint_path}")
    
    # Step 1: Make backup
    backup_path = make_backup(checkpoint_path)
    
    # Step 2: Try different loading methods
    methods = ["default", "weights_only", "pickle_protocol"]
    checkpoint = None
    successful_method = None
    
    for method in methods:
        logger.info(f"🔍 Trying load method: {method}")
        checkpoint = try_load_checkpoint(checkpoint_path, method=method)
        if checkpoint is not None:
            successful_method = method
            break
    
    if checkpoint is None:
        logger.error(f"❌ Could not load checkpoint with any method")
        logger.error(f"   Checkpoint file may be completely corrupted")
        logger.error(f"   Backup saved at: {backup_path}")
        return False
    
    # Step 3: Validate checkpoint
    if not validate_checkpoint(checkpoint):
        logger.error(f"❌ Checkpoint validation failed")
        logger.error(f"   Backup saved at: {backup_path}")
        return False
    
    # Step 4: Save repaired checkpoint
    logger.info(f"💾 Saving repaired checkpoint...")
    try:
        import torch
        # Save to temporary file first
        temp_path = checkpoint_path.parent / f"{checkpoint_path.stem}.repaired{checkpoint_path.suffix}"
        torch.save(checkpoint, str(temp_path))
        
        # Verify the saved file can be loaded
        test_checkpoint = torch.load(str(temp_path), weights_only=False, map_location='cpu')
        if validate_checkpoint(test_checkpoint):
            # Replace original with repaired version
            shutil.move(str(temp_path), str(checkpoint_path))
            logger.info(f"✅ Checkpoint repaired and saved successfully")
            logger.info(f"   Original backed up to: {backup_path}")
            logger.info(f"   Loaded with method: {successful_method}")
            return True
        else:
            logger.error(f"❌ Repaired checkpoint failed validation")
            temp_path.unlink()  # Delete temp file
            return False
    except Exception as e:
        logger.error(f"❌ Failed to save repaired checkpoint: {e}")
        logger.error(traceback.format_exc())
        return False


def find_foundation_checkpoint(session_id: str) -> Path:
    """Find foundation checkpoint file for a session."""
    from config import config
    
    session_dir = config.output_dir / session_id
    
    if not session_dir.exists():
        raise FileNotFoundError(f"Session directory not found: {session_dir}")
    
    # Look for foundation_checkpoint_*.pth files
    checkpoint_files = list(session_dir.glob("foundation_checkpoint_*.pth"))
    
    if not checkpoint_files:
        raise FileNotFoundError(f"No foundation checkpoint found in {session_dir}")
    
    if len(checkpoint_files) > 1:
        logger.warning(f"⚠️  Found multiple checkpoint files, using first: {checkpoint_files[0]}")
        for cf in checkpoint_files:
            logger.info(f"   - {cf}")
    
    return checkpoint_files[0]


def find_foundation_model_checkpoint(foundation_model_id: str) -> Path:
    """Find checkpoint file in foundation model's train_es directory."""
    from config import config
    
    foundation_dir = config.output_dir / foundation_model_id / "train_es"
    
    if not foundation_dir.exists():
        raise FileNotFoundError(f"Foundation model directory not found: {foundation_dir}")
    
    # Look for training_state_*.pth files (prefer BEST, then last epoch)
    best_checkpoint = foundation_dir / "training_state_BEST.pth"
    if best_checkpoint.exists():
        logger.info(f"✅ Found BEST checkpoint: {best_checkpoint}")
        return best_checkpoint
    
    # Look for last epoch checkpoint
    epoch_checkpoints = sorted(foundation_dir.glob("training_state_e-*.pth"))
    if epoch_checkpoints:
        last_checkpoint = epoch_checkpoints[-1]
        logger.info(f"✅ Found last epoch checkpoint: {last_checkpoint}")
        return last_checkpoint
    
    raise FileNotFoundError(f"No checkpoint found in {foundation_dir}")


def main():
    parser = argparse.ArgumentParser(description="Repair corrupted checkpoint file")
    parser.add_argument("checkpoint_path", nargs="?", help="Path to checkpoint .pth file")
    parser.add_argument("--session-id", help="Session ID to find foundation checkpoint")
    parser.add_argument("--foundation-model-id", help="Foundation model ID to find checkpoint in train_es directory")
    parser.add_argument("--dry-run", action="store_true", help="Don't modify files, just test loading")
    
    args = parser.parse_args()
    
    # Find checkpoint file
    if args.foundation_model_id:
        logger.info(f"🔍 Searching for checkpoint in foundation model: {args.foundation_model_id}")
        checkpoint_path = find_foundation_model_checkpoint(args.foundation_model_id)
        logger.info(f"✅ Found checkpoint: {checkpoint_path}")
    elif args.session_id:
        logger.info(f"🔍 Searching for foundation checkpoint in session: {args.session_id}")
        checkpoint_path = find_foundation_checkpoint(args.session_id)
        logger.info(f"✅ Found checkpoint: {checkpoint_path}")
    elif args.checkpoint_path:
        checkpoint_path = Path(args.checkpoint_path)
    else:
        parser.error("Must provide checkpoint_path, --session-id, or --foundation-model-id")
    
    if not checkpoint_path.exists():
        logger.error(f"❌ Checkpoint file not found: {checkpoint_path}")
        return 1
    
    logger.info(f"📂 Checkpoint file: {checkpoint_path}")
    logger.info(f"   Size: {checkpoint_path.stat().st_size / (1024**2):.2f} MB")
    
    if args.dry_run:
        logger.info("🔍 DRY RUN: Testing checkpoint loading only")
        checkpoint = try_load_checkpoint(checkpoint_path)
        if checkpoint and validate_checkpoint(checkpoint):
            logger.info("✅ Checkpoint is valid, no repair needed")
            return 0
        else:
            logger.error("❌ Checkpoint is corrupted")
            return 1
    
    # Repair checkpoint
    success = repair_checkpoint(checkpoint_path)
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

