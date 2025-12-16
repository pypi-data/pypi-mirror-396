"""
Feature Suggestion Tracker - Dynamic Feature Engineering During Training

Tracks feature engineering suggestions across epochs and applies high-confidence
features (suggested multiple times) dynamically during training.
"""
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import pandas as pd

logger = logging.getLogger(__name__)


class FeatureSuggestionTracker:
    """
    Track feature suggestions across training epochs and apply high-confidence features.
    
    Workflow:
        1. Every N epochs, analyze hard rows → generate suggestions
        2. Record suggestions in history with vote counts
        3. When a feature gets M+ votes, apply it to the dataset
        4. Continue training with enhanced features
    
    Example:
        tracker = FeatureSuggestionTracker(
            vote_threshold=3,        # Apply after 3 recommendations
            check_interval=10,       # Check every 10 epochs
            max_features_per_round=3 # Apply top 3 at a time
        )
        
        # In training loop:
        if epoch % tracker.check_interval == 0:
            suggestions = generate_suggestions(...)
            tracker.record_suggestions(suggestions, epoch)
            
            if tracker.should_apply_features():
                new_features = tracker.get_features_to_apply()
                df = tracker.apply_features(df, new_features)
    """
    
    def __init__(
        self,
        vote_threshold: int = 3,
        check_interval: int = 10,
        max_features_per_round: int = 3,
        min_epoch_before_apply: int = 30,
        apply_top_every_interval: bool = False
    ):
        """
        Initialize suggestion tracker.
        
        Args:
            vote_threshold: Minimum votes needed before applying a feature (ignored if apply_top_every_interval=True)
            check_interval: Check for suggestions every N epochs
            max_features_per_round: Maximum features to apply at once
            min_epoch_before_apply: Don't apply any features before this epoch
            apply_top_every_interval: If True, apply top N features every interval regardless of vote count
        """
        self.vote_threshold = vote_threshold
        self.check_interval = check_interval
        self.max_features_per_round = max_features_per_round
        self.min_epoch_before_apply = min_epoch_before_apply
        self.apply_top_every_interval = apply_top_every_interval
        
        # suggestion_history[feature_name] = {
        #     'suggestion': {...},        # Full suggestion dict
        #     'count': 5,                 # Number of times suggested
        #     'first_seen_epoch': 20,     # First epoch it appeared
        #     'last_seen_epoch': 50,      # Most recent epoch
        #     'suggested_at_epochs': [20, 30, 40, 45, 50],  # All epochs where suggested
        #     'applied': False,           # Whether it's been applied
        #     'applied_epoch': None       # Epoch when applied
        # }
        self.suggestion_history: Dict[str, Dict[str, Any]] = {}
        
        # Track applied features to avoid duplicates
        self.applied_features: set = set()
        
        # Track when features were applied (for logging/debugging)
        self.application_log: List[Dict[str, Any]] = []
    
    def record_suggestions(self, suggestions: List[Dict[str, Any]], epoch: int):
        """
        Record new suggestions from an epoch.
        
        Args:
            suggestions: List of suggestion dicts (from training_logger)
            epoch: Current training epoch
        """
        for suggestion in suggestions:
            feature_name = suggestion.get('name')
            if not feature_name:
                continue
            
            if feature_name not in self.suggestion_history:
                # New suggestion - create entry
                self.suggestion_history[feature_name] = {
                    'suggestion': suggestion,
                    'count': 1,
                    'first_seen_epoch': epoch,
                    'last_seen_epoch': epoch,
                    'suggested_at_epochs': [epoch],  # NEW: Track all epochs
                    'applied': False,
                    'applied_epoch': None
                }
                logger.debug(f"📝 New suggestion tracked: {feature_name} (epoch {epoch})")
            else:
                # Existing suggestion - increment count and add epoch to list
                self.suggestion_history[feature_name]['count'] += 1
                self.suggestion_history[feature_name]['last_seen_epoch'] = epoch
                self.suggestion_history[feature_name]['suggested_at_epochs'].append(epoch)  # NEW: Track this epoch
                
                # Update suggestion dict in case threshold changed
                self.suggestion_history[feature_name]['suggestion'] = suggestion
                
                count = self.suggestion_history[feature_name]['count']
                epochs_list = self.suggestion_history[feature_name]['suggested_at_epochs']
                logger.debug(f"🔁 Suggestion re-confirmed: {feature_name} (count={count}, epochs={epochs_list})")
    
    def get_features_to_apply(self, current_epoch: int) -> List[Tuple[str, Dict[str, Any]]]:
        """
        Get high-confidence features that should be applied now.
        
        Args:
            current_epoch: Current training epoch
        
        Returns:
            List of (feature_name, info_dict) tuples sorted by vote count
        """
        if current_epoch < self.min_epoch_before_apply:
            return []
        
        if self.apply_top_every_interval:
            # Mode 2: Apply top N features every interval, regardless of vote count
            # Just need at least 1 vote (i.e., it was suggested at least once)
            candidates = [
                (name, info) for name, info in self.suggestion_history.items()
                if (
                    info['count'] >= 1 and
                    not info['applied'] and
                    name not in self.applied_features
                )
            ]
        else:
            # Mode 1: Only apply features with vote_threshold+ votes
            candidates = [
                (name, info) for name, info in self.suggestion_history.items()
                if (
                    info['count'] >= self.vote_threshold and
                    not info['applied'] and
                    name not in self.applied_features
                )
            ]
        
        # Sort by count (descending), then by first seen (ascending)
        candidates.sort(key=lambda x: (-x[1]['count'], x[1]['first_seen_epoch']))
        
        # Return top N
        return candidates[:self.max_features_per_round]
    
    def should_apply_features(self, current_epoch: int) -> bool:
        """
        Check if we should apply features now.
        
        Args:
            current_epoch: Current training epoch
        
        Returns:
            True if there are features ready to apply
        """
        # Only check on interval boundaries
        if current_epoch % self.check_interval != 0:
            return False
        
        return len(self.get_features_to_apply(current_epoch)) > 0
    
    def apply_features(
        self,
        df: pd.DataFrame,
        features_to_apply: List[Tuple[str, Dict[str, Any]]],
        current_epoch: int,
        verbose: bool = True
    ) -> pd.DataFrame:
        """
        Apply selected features to DataFrame.
        
        Args:
            df: Input DataFrame
            features_to_apply: List of (feature_name, info_dict) tuples
            current_epoch: Current training epoch
            verbose: Log progress
        
        Returns:
            Enhanced DataFrame
        """
        if not features_to_apply:
            return df
        
        # Import FeatureEngineer dynamically to avoid circular imports
        try:
            from featrix.neural.feature_engineer import FeatureEngineer
        except ImportError:
            # Fallback for direct module loading
            import importlib.util
            import os
            module_path = os.path.join(os.path.dirname(__file__), 'feature_engineer.py')
            spec = importlib.util.spec_from_file_location("feature_engineer", module_path)
            feature_engineer_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(feature_engineer_module)
            FeatureEngineer = feature_engineer_module.FeatureEngineer
        
        if verbose:
            logger.info("")
            logger.info("=" * 80)
            if self.apply_top_every_interval:
                logger.info(f"🚀 APPLYING TOP {len(features_to_apply)} FEATURE(S) (Epoch {current_epoch})")
            else:
                logger.info(f"🚀 APPLYING HIGH-CONFIDENCE FEATURES (Epoch {current_epoch})")
            logger.info("=" * 80)
            for feature_name, info in features_to_apply:
                count = info['count']
                first_epoch = info['first_seen_epoch']
                epochs_list = info['suggested_at_epochs']
                epochs_str = ', '.join(map(str, epochs_list))
                logger.info(f"   • {feature_name}")
                logger.info(f"     - Votes: {count}")
                logger.info(f"     - Suggested at epochs: [{epochs_str}]")
                logger.info(f"     - First seen: epoch {first_epoch}")
            logger.info("=" * 80)
        
        # Extract suggestion dicts
        suggestions = [info['suggestion'] for _, info in features_to_apply]
        
        # Apply using FeatureEngineer
        engineer = FeatureEngineer(suggestions=suggestions)
        df_enhanced = engineer.fit_transform(df, verbose=verbose)
        
        # Mark as applied
        for feature_name, info in features_to_apply:
            self.suggestion_history[feature_name]['applied'] = True
            self.suggestion_history[feature_name]['applied_epoch'] = current_epoch
            self.applied_features.add(feature_name)
            
            # Log application
            self.application_log.append({
                'epoch': current_epoch,
                'feature_name': feature_name,
                'votes': info['count'],
                'first_seen_epoch': info['first_seen_epoch'],
                'suggestion': info['suggestion']
            })
        
        if verbose:
            logger.info(f"✅ Applied {len(features_to_apply)} new features")
            logger.info(f"   Total engineered features: {len(self.applied_features)}")
            logger.info("=" * 80)
            logger.info("")
        
        return df_enhanced
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get summary statistics about suggestions.
        
        Returns:
            Dict with statistics
        """
        total_suggestions = len(self.suggestion_history)
        applied_count = sum(1 for info in self.suggestion_history.values() if info['applied'])
        pending_count = sum(1 for info in self.suggestion_history.values() 
                          if info['count'] >= self.vote_threshold and not info['applied'])
        
        # Top suggestions by vote count
        top_suggestions = sorted(
            self.suggestion_history.items(),
            key=lambda x: x[1]['count'],
            reverse=True
        )[:10]
        
        return {
            'total_suggestions': total_suggestions,
            'applied_features': applied_count,
            'pending_high_confidence': pending_count,
            'vote_threshold': self.vote_threshold,
            'top_suggestions': [
                {
                    'name': name,
                    'votes': info['count'],
                    'applied': info['applied'],
                    'first_seen': info['first_seen_epoch'],
                    'last_seen': info['last_seen_epoch'],
                    'suggested_at_epochs': info['suggested_at_epochs']
                }
                for name, info in top_suggestions
            ]
        }
    
    def log_status(self, current_epoch: int):
        """
        Log current status of suggestion tracking.
        
        Args:
            current_epoch: Current training epoch
        """
        stats = self.get_statistics()
        
        logger.info("")
        logger.info("📊 FEATURE SUGGESTION TRACKER STATUS")
        logger.info(f"   Total suggestions tracked: {stats['total_suggestions']}")
        logger.info(f"   Features applied: {stats['applied_features']}")
        logger.info(f"   High-confidence pending: {stats['pending_high_confidence']} (≥{self.vote_threshold} votes)")
        
        if stats['top_suggestions']:
            logger.info("")
            logger.info("   Top Suggestions by Votes:")
            for item in stats['top_suggestions'][:5]:
                status = "✅ APPLIED" if item['applied'] else f"🔄 {item['votes']} votes"
                epochs_str = ', '.join(map(str, item['suggested_at_epochs']))
                logger.info(f"      • {item['name']}: {status} [epochs: {epochs_str}]")
        
        logger.info("")
    
    def export_history(self, output_path: str):
        """
        Export suggestion history to JSON for analysis.
        
        Args:
            output_path: Path to save JSON file
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        export_data = {
            'statistics': self.get_statistics(),
            'suggestion_history': {
                name: {
                    'suggestion': info['suggestion'],
                    'votes': info['count'],
                    'first_seen_epoch': info['first_seen_epoch'],
                    'last_seen_epoch': info['last_seen_epoch'],
                    'suggested_at_epochs': info['suggested_at_epochs'],  # NEW: Full epoch list
                    'applied': info['applied'],
                    'applied_epoch': info['applied_epoch']
                }
                for name, info in self.suggestion_history.items()
            },
            'application_log': self.application_log,
            'config': {
                'vote_threshold': self.vote_threshold,
                'check_interval': self.check_interval,
                'max_features_per_round': self.max_features_per_round,
                'min_epoch_before_apply': self.min_epoch_before_apply,
                'apply_top_every_interval': self.apply_top_every_interval,
                'mode': 'top_N_every_interval' if self.apply_top_every_interval else 'vote_threshold'
            }
        }
        
        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        logger.info(f"💾 Exported suggestion history to {output_path}")
    
    def __repr__(self):
        stats = self.get_statistics()
        return (f"FeatureSuggestionTracker("
                f"tracked={stats['total_suggestions']}, "
                f"applied={stats['applied_features']}, "
                f"pending={stats['pending_high_confidence']}, "
                f"threshold={self.vote_threshold})")

