#  -*- coding: utf-8 -*-
#
#  Copyright Featrix, Inc 2023-2025
#
#  Proprietary and Confidential.  Unauthorized use, copying or dissemination
#  of these materials is strictly prohibited.
#
"""
Structured training logging for clean, comprehensive, easy-to-scan output.

Provides:
- MetricTracker: Multi-epoch delta tracking (Δ1, Δ5, Δ10)
- RowErrorTracker: Hard example analysis with feature commonality
- StructuredLogger: Formatted output with visual structure
"""
import logging
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict, Counter

logger = logging.getLogger(__name__)


# ============================================================================
# MetricTracker - Multi-Epoch Delta Tracking
# ============================================================================

class MetricTracker:
    """
    Track metrics across epochs and compute multi-epoch deltas.
    
    Usage:
        tracker = MetricTracker()
        tracker.add_epoch(0, {"auc": 0.612, "accuracy": 0.550})
        tracker.add_epoch(1, {"auc": 0.643, "accuracy": 0.580})
        
        deltas = tracker.get_deltas("auc", epochs=[1, 5, 10])
        # Returns: {"delta_1": 0.031, "delta_5": None, "delta_10": None}
    """
    
    def __init__(self):
        self.history = []  # [(epoch_idx, metrics_dict), ...]
        self.epoch_to_idx = {}  # {epoch_idx: position in history list}
    
    def add_epoch(self, epoch_idx: int, metrics: Dict[str, float]):
        """Add metrics for an epoch."""
        self.epoch_to_idx[epoch_idx] = len(self.history)
        self.history.append((epoch_idx, metrics.copy()))
    
    def get_metric_at_epoch(self, metric_name: str, epoch_idx: int) -> Optional[float]:
        """Get metric value at specific epoch."""
        if epoch_idx not in self.epoch_to_idx:
            return None
        idx = self.epoch_to_idx[epoch_idx]
        return self.history[idx][1].get(metric_name)
    
    def get_deltas(self, metric_name: str, current_epoch: int, lookback_epochs: List[int] = [1, 5, 10]) -> Dict[str, Optional[float]]:
        """
        Compute deltas for a metric.
        
        Returns: {"delta_1": 0.031, "delta_5": 0.142, "delta_10": None}
        """
        current_value = self.get_metric_at_epoch(metric_name, current_epoch)
        if current_value is None:
            return {f"delta_{n}": None for n in lookback_epochs}
        
        deltas = {}
        for n in lookback_epochs:
            prev_epoch = current_epoch - n
            if prev_epoch < 0:
                deltas[f"delta_{n}"] = None
            else:
                prev_value = self.get_metric_at_epoch(metric_name, prev_epoch)
                if prev_value is None:
                    deltas[f"delta_{n}"] = None
                else:
                    deltas[f"delta_{n}"] = current_value - prev_value
        
        return deltas
    
    def get_trend_indicator(self, metric_name: str, current_epoch: int, strong_threshold: float = 0.05) -> str:
        """
        Get trend indicator based on recent deltas.
        
        Returns: "↗↗" (strong up), "↗" (up), "→" (flat), "↘" (down), "↘↘" (strong down)
        """
        deltas = self.get_deltas(metric_name, current_epoch, lookback_epochs=[1, 5])
        delta_1 = deltas.get("delta_1")
        delta_5 = deltas.get("delta_5")
        
        # Use delta_5 for trend if available, otherwise delta_1
        primary_delta = delta_5 if delta_5 is not None else delta_1
        
        if primary_delta is None:
            return "→"
        
        if abs(primary_delta) < 0.001:  # Effectively flat
            return "→"
        elif primary_delta > strong_threshold:
            return "↗↗"  # Strong improvement
        elif primary_delta > 0:
            return "↗"   # Improvement
        elif primary_delta < -strong_threshold:
            return "↘↘"  # Strong decline
        else:
            return "↘"   # Decline


# ============================================================================
# RowErrorTracker - Hard Example Analysis
# ============================================================================

class RowErrorTracker:
    """
    Track per-row correct/wrong status and analyze hard examples.
    
    Finds patterns in features that make certain rows harder to classify.
    """
    
    def __init__(self, num_rows: int, features: List[Dict[str, Any]], ground_truth: List[Any]):
        self.num_rows = num_rows
        self.features = features  # List of feature dicts
        self.ground_truth = ground_truth
        self.epoch_results = {}  # {epoch: [1,0,1,0,...]}
        self.error_counts = np.zeros(num_rows, dtype=int)  # Total errors per row
        self.total_epochs = 0
    
    def update(self, epoch_idx: int, correct_flags: List[int]):
        """Update with results from an epoch."""
        if len(correct_flags) != self.num_rows:
            logger.warning(f"RowErrorTracker: Expected {self.num_rows} flags, got {len(correct_flags)}")
            return
        
        self.epoch_results[epoch_idx] = correct_flags
        self.total_epochs = max(self.total_epochs, epoch_idx + 1)
        
        # Update error counts
        for i, flag in enumerate(correct_flags):
            if flag == 0:  # Wrong
                self.error_counts[i] += 1
    
    def get_error_rates(self) -> np.ndarray:
        """Get error rate per row (fraction of epochs where row was wrong)."""
        if self.total_epochs == 0:
            return np.zeros(self.num_rows)
        return self.error_counts / self.total_epochs
    
    def get_hardest_rows(self, n: int = 5, window: Optional[int] = None) -> List[Tuple[int, float, Any]]:
        """
        Get N hardest rows (highest error rate).
        
        Args:
            n: Number of rows to return
            window: If set, only consider last N epochs (default: all epochs)
        
        Returns: [(row_idx, error_rate, ground_truth), ...]
        """
        if window is not None and window > 0:
            # Compute error rate over window
            recent_epochs = sorted([e for e in self.epoch_results.keys()])[-window:]
            if not recent_epochs:
                return []
            
            error_rates = np.zeros(self.num_rows)
            for epoch in recent_epochs:
                for i, flag in enumerate(self.epoch_results[epoch]):
                    if flag == 0:
                        error_rates[i] += 1
            error_rates /= len(recent_epochs)
        else:
            # All-time error rate
            error_rates = self.get_error_rates()
        
        # Get top N
        top_indices = np.argsort(error_rates)[::-1][:n]
        return [(int(idx), float(error_rates[idx]), self.ground_truth[idx]) for idx in top_indices]
    
    def get_category_counts(self) -> Dict[str, int]:
        """Get counts for error rate categories."""
        error_rates = self.get_error_rates()
        return {
            "always_wrong": int((error_rates > 0.95).sum()),
            "frequently_wrong": int(((error_rates > 0.7) & (error_rates <= 0.95)).sum()),
            "sometimes_wrong": int(((error_rates > 0.3) & (error_rates <= 0.7)).sum()),
            "rarely_wrong": int(((error_rates > 0) & (error_rates <= 0.3)).sum()),
            "never_wrong": int((error_rates == 0).sum()),
        }
    
    def get_recently_learned(self, n: int = 5, min_wrong_epochs: int = 5) -> List[Tuple[int, int]]:
        """
        Find rows that were wrong for several epochs then became correct.
        
        Returns: [(row_idx, epoch_became_correct), ...]
        """
        if len(self.epoch_results) < min_wrong_epochs + 1:
            return []
        
        sorted_epochs = sorted(self.epoch_results.keys())
        recently_learned = []
        
        for row_idx in range(self.num_rows):
            # Find first epoch where row became correct
            first_correct = None
            wrong_count_before = 0
            
            for epoch in sorted_epochs:
                if self.epoch_results[epoch][row_idx] == 1:  # Correct
                    if wrong_count_before >= min_wrong_epochs:
                        first_correct = epoch
                        break
                else:  # Wrong
                    wrong_count_before += 1
            
            if first_correct is not None:
                recently_learned.append((row_idx, first_correct, wrong_count_before))
        
        # Sort by when they became correct (most recent first)
        recently_learned.sort(key=lambda x: x[1], reverse=True)
        return recently_learned[:n]
    
    def find_feature_commonality(self, hard_row_indices: List[int], easy_row_indices: Optional[List[int]] = None) -> Dict[str, Any]:
        """
        Analyze features of hard rows to find common patterns.
        
        Compares hard rows vs easy rows to find distinctive features.
        """
        if not hard_row_indices or not self.features:
            return {}
        
        # Get easy rows for comparison if not provided
        if easy_row_indices is None:
            error_rates = self.get_error_rates()
            easy_indices = np.argsort(error_rates)[:len(hard_row_indices)]
            easy_row_indices = easy_indices.tolist()
        
        hard_features = [self.features[i] for i in hard_row_indices if i < len(self.features)]
        easy_features = [self.features[i] for i in easy_row_indices if i < len(self.features)]
        
        if not hard_features or not easy_features:
            return {}
        
        commonalities = {
            "categorical_patterns": [],
            "numeric_patterns": [],
            "distinctive_features": []
        }
        
        # Get all feature names
        feature_names = set()
        for f in hard_features + easy_features:
            if isinstance(f, dict):
                feature_names.update(f.keys())
        
        # Analyze each feature
        for feature_name in feature_names:
            # Extract values for this feature
            hard_values = [f.get(feature_name) for f in hard_features if isinstance(f, dict) and feature_name in f]
            easy_values = [f.get(feature_name) for f in easy_features if isinstance(f, dict) and feature_name in f]
            
            if not hard_values or not easy_values:
                continue
            
            # Check if categorical or numeric
            sample_value = hard_values[0]
            is_numeric = isinstance(sample_value, (int, float)) and not isinstance(sample_value, bool)
            
            if is_numeric:
                # Numeric feature - compare means
                hard_mean = np.mean([v for v in hard_values if v is not None and isinstance(v, (int, float))])
                easy_mean = np.mean([v for v in easy_values if v is not None and isinstance(v, (int, float))])
                hard_std = np.std([v for v in hard_values if v is not None and isinstance(v, (int, float))])
                easy_std = np.std([v for v in easy_values if v is not None and isinstance(v, (int, float))])
                
                # Simple t-test-like comparison (difference relative to pooled std)
                pooled_std = np.sqrt((hard_std**2 + easy_std**2) / 2)
                if pooled_std > 0:
                    effect_size = abs(hard_mean - easy_mean) / pooled_std
                    if effect_size > 0.5:  # Medium effect size
                        commonalities["numeric_patterns"].append({
                            "feature": feature_name,
                            "hard_mean": float(hard_mean),
                            "hard_std": float(hard_std),
                            "easy_mean": float(easy_mean),
                            "easy_std": float(easy_std),
                            "effect_size": float(effect_size)
                        })
            else:
                # Categorical feature - compare frequencies
                hard_counter = Counter([str(v) for v in hard_values])
                easy_counter = Counter([str(v) for v in easy_values])
                
                # Find values that appear much more in hard rows
                for value, hard_count in hard_counter.most_common(5):
                    hard_freq = hard_count / len(hard_values)
                    easy_count = easy_counter.get(value, 0)
                    easy_freq = easy_count / len(easy_values) if easy_values else 0
                    
                    # Significant if appears >50% more frequently in hard rows
                    if hard_freq > easy_freq + 0.3:  # 30 percentage point difference
                        commonalities["categorical_patterns"].append({
                            "feature": feature_name,
                            "value": value,
                            "hard_freq": float(hard_freq),
                            "hard_count": hard_count,
                            "easy_freq": float(easy_freq),
                            "easy_count": easy_count
                        })
        
        # Sort patterns by strength
        commonalities["categorical_patterns"].sort(key=lambda x: x["hard_freq"] - x["easy_freq"], reverse=True)
        commonalities["numeric_patterns"].sort(key=lambda x: x["effect_size"], reverse=True)
        
        return commonalities


# ============================================================================
# StructuredLogger - Formatted Output
# ============================================================================

class StructuredLogger:
    """
    Format training output in clean, structured format.
    
    Uses box drawing, tables, and visual hierarchy for easy scanning.
    """
    
    def __init__(self, logger_instance: logging.Logger, target_col_name: str = None):
        self.logger = logger_instance
        self.current_epoch = None  # Set by set_epoch() for prefix
        self.target_col_name = target_col_name or "unknown"
    
    def set_epoch(self, epoch: int):
        """Set current epoch for prefix."""
        self.current_epoch = epoch
    
    def _prefix(self, msg: str) -> str:
        """Add epoch and target prefix for grepability - SAME FORMAT AS single_predictor.py."""
        if self.current_epoch is not None:
            return f"epoch={self.current_epoch}, target={self.target_col_name}: {msg}"
        return f"target={self.target_col_name}: {msg}"
    
    def log_epoch_header(self, epoch: int, total_epochs: int, elapsed_time: float):
        """Log epoch header with progress bar."""
        self.current_epoch = epoch  # Store for prefix
        pct = (epoch / total_epochs * 100) if total_epochs > 0 else 0
        self.logger.info(f"[epoch={epoch}] ╔════════════════════════════════════════════════════════════════════╗")
        self.logger.info(f"[epoch={epoch}] ║  EPOCH {epoch}/{total_epochs} ({pct:.0f}% complete) - {elapsed_time:.2f}s{' ' * (47 - len(f'EPOCH {epoch}/{total_epochs} ({pct:.0f}% complete) - {elapsed_time:.2f}s'))}║")
        self.logger.info(f"[epoch={epoch}] ╚════════════════════════════════════════════════════════════════════╝")
    
    def log_loss_section(self, train_loss: float, val_loss: float, 
                        train_deltas: Dict[str, Optional[float]], 
                        val_deltas: Dict[str, Optional[float]], 
                        is_new_best: bool,
                        learning_rate: float = None):
        """Log loss section with deltas and learning rate."""
        self.logger.info(self._prefix(""))
        
        # Include LR in header if provided
        if learning_rate is not None:
            self.logger.info(self._prefix(f"📉 LOSS (LR={learning_rate:.6e}):"))
        else:
            self.logger.info(self._prefix("📉 LOSS:"))
        
        # Format deltas
        train_delta_str = self._format_deltas(train_deltas)
        val_delta_str = self._format_deltas(val_deltas)
        
        best_marker = "  ⭐ NEW BEST" if is_new_best else ""
        
        self.logger.info(self._prefix(f"   Training:   {train_loss:.4f}  {train_delta_str}"))
        self.logger.info(self._prefix(f"   Validation: {val_loss:.4f}  {val_delta_str}{best_marker}"))
    
    def _format_deltas(self, deltas: Dict[str, Optional[float]]) -> str:
        """Format delta dict as compact string."""
        parts = []
        for key in ["delta_1", "delta_5", "delta_10"]:
            delta = deltas.get(key)
            if delta is None:
                parts.append("Δ?=N/A")
            else:
                sign = "+" if delta > 0 else ""
                parts.append(f"Δ{key.split('_')[1]}={sign}{delta:.4f}")
        return "  ".join(parts)
    
    def log_health_section(self, gradient_unclipped: float, gradient_clipped: float,
                          learning_rate: float, lr_phase: str,
                          class_distribution: Dict[str, float],
                          prob_std: float, logit_range: float,
                          warnings: List[str] = None):
        """Log training health diagnostics."""
        self.logger.info(self._prefix(""))
        self.logger.info(self._prefix("🏥 TRAINING HEALTH:"))
        
        # Gradients
        grad_ratio = gradient_clipped / gradient_unclipped if gradient_unclipped > 0 else 1.0
        grad_status = "✅" if 0.1 <= gradient_unclipped <= 10 else "⚠️"
        self.logger.info(self._prefix(f"   {grad_status} Gradients:     {gradient_unclipped:.2f} unclipped, {gradient_clipped:.2f} clipped (ratio={grad_ratio:.2f}x)  [healthy: 0.1-10]"))
        
        # Learning rate (handle list or float)
        if isinstance(learning_rate, list):
            lr_value = learning_rate[0] if len(learning_rate) > 0 else 0
        else:
            lr_value = learning_rate
        self.logger.info(self._prefix(f"   ✅ Learning Rate: {lr_value:.2e} ({lr_phase})"))
        
        # Class distribution
        if class_distribution and len(class_distribution) > 0:
            class_str = ", ".join([f"'{k}'({v:.0%})" for k, v in class_distribution.items()])
            both_predicted = len(class_distribution) >= 2
            status = "✅" if both_predicted else "❌"
            self.logger.info(self._prefix(f"   {status} Classes predicted: {class_str}"))
        else:
            self.logger.info(self._prefix(f"   ⚠️  Classes predicted: (not available)"))
        
        # Probability spread
        prob_status = "✅" if prob_std > 0.10 else ("⚠️" if prob_std > 0.05 else "❌")
        self.logger.info(self._prefix(f"   {prob_status} Probability spread: std={prob_std:.3f}  [healthy: >0.10, collapse: <0.05]"))
        
        # Logit range
        logit_status = "✅" if logit_range > 1.0 else ("⚠️" if logit_range > 0.5 else "❌")
        self.logger.info(self._prefix(f"   {logit_status} Logit range: {logit_range:.2f}  [healthy: >1.0, saturated: <0.5]"))
        
        # Warnings
        if warnings and isinstance(warnings, list) and len(warnings) > 0:
            self.logger.info(self._prefix(f"   ⚠️  Active warnings: {', '.join(warnings)}"))
        else:
            self.logger.info(self._prefix(f"   ✅ No warnings active"))
    
    def log_metrics_table(self, current_metrics: Dict[str, float], 
                         metric_tracker: MetricTracker,
                         current_epoch: int,
                         best_metrics: Dict[str, bool] = None):
        """Log comprehensive metrics table with deltas."""
        self.logger.info(self._prefix(""))
        self.logger.info(self._prefix("📊 CLASSIFICATION METRICS:"))
        
        # Header
        self.logger.info(self._prefix("   Metric          Current   Δ1 Epoch  Δ5 Epochs  Δ10 Epochs  Trend    Quality"))
        self.logger.info(self._prefix("   " + "─" * 77))
        
        # Metrics to show (in order) - group percentages together, then ratios
        metrics_config = [
            ("auc", "AUC-ROC", 0.70, 0.80, False),  # (key, name, good_threshold, excellent_threshold, lower_is_better)
            ("pr_auc", "PR-AUC", 0.50, 0.70, False),
            ("accuracy", "Accuracy", 0.70, 0.80, False),
            ("precision", "Precision", 0.60, 0.75, False),
            ("recall", "Recall", 0.65, 0.80, False),
            ("specificity", "Specificity", 0.70, 0.80, False),
            ("f1", "F1 Score", 0.60, 0.75, False),  # After percentages
            ("mcc", "MCC", 0.40, 0.60, False),
            ("brier_score", "Brier Score", 0.20, 0.15, True),  # Lower is better
        ]
        
        for metric_key, metric_name, good_thresh, exc_thresh, lower_better in metrics_config:
            value = current_metrics.get(metric_key)
            if value is None:
                continue
            
            # Get deltas
            deltas = metric_tracker.get_deltas(metric_key, current_epoch, [1, 5, 10])
            delta_1 = deltas.get("delta_1")
            delta_5 = deltas.get("delta_5")
            delta_10 = deltas.get("delta_10")
            
            # Format value (handle percentages)
            if metric_key in ["accuracy", "precision", "recall", "specificity"]:
                value_str = f"{value*100:5.1f}%"
            else:
                value_str = f"{value:7.3f}"
            
            # Format deltas
            d1_str = self._format_delta_value(delta_1, is_pct=(metric_key in ["accuracy", "precision", "recall", "specificity"]))
            d5_str = self._format_delta_value(delta_5, is_pct=(metric_key in ["accuracy", "precision", "recall", "specificity"]))
            d10_str = self._format_delta_value(delta_10, is_pct=(metric_key in ["accuracy", "precision", "recall", "specificity"]))
            
            # Trend indicator
            trend = metric_tracker.get_trend_indicator(metric_key, current_epoch)
            
            # Best marker
            is_best = best_metrics.get(metric_key, False) if best_metrics else False
            best_marker = " ⭐" if is_best else "  "
            
            # Quality assessment
            if lower_better:
                if value < exc_thresh:
                    quality = "EXCELLENT"
                elif value < good_thresh:
                    quality = "GOOD"
                else:
                    quality = "FAIR"
            else:
                if value > exc_thresh:
                    quality = "EXCELLENT"
                elif value > good_thresh:
                    quality = "GOOD"
                else:
                    quality = "FAIR"
            
            self.logger.info(self._prefix(f"   {metric_name:15s} {value_str:9s} {d1_str:10s} {d5_str:11s} {d10_str:11s} {trend:5s}{best_marker}  {quality}"))
        
        self.logger.info(self._prefix(""))
        self.logger.info(self._prefix("   Trend Key: ↗↗=strong up, ↗=up, →=flat, ↘=down, ↘↘=strong down"))
    
    def _format_delta_value(self, delta: Optional[float], is_pct: bool = False) -> str:
        """Format a delta value."""
        if delta is None:
            return "N/A"
        sign = "+" if delta >= 0 else ""
        if is_pct:
            return f"{sign}{delta*100:.1f}%"
        else:
            return f"{sign}{delta:.3f}"
    
    def log_confusion_matrix(self, tp: int, fp: int, tn: int, fn: int,
                            pos_label: str, neg_label: str,
                            threshold: float,
                            precision: float, recall: float, specificity: float,
                            prev_tp: int = None, prev_fp: int = None,
                            prev_tn: int = None, prev_fn: int = None):
        """Log confusion matrix with interpretation."""
        self.logger.info(self._prefix(""))
        self.logger.info(self._prefix(f"📊 CONFUSION MATRIX (Threshold: {threshold:.3f}):"))
        self.logger.info(self._prefix(""))
        
        # Matrix visualization
        self.logger.info(self._prefix("            ┌────────────────────────────┐"))
        self.logger.info(self._prefix("            │      PREDICTED             │"))
        self.logger.info(self._prefix("            ├──────────┬─────────────────┤"))
        self.logger.info(self._prefix(f"            │Positive  │  Negative       │"))
        self.logger.info(self._prefix(" A ┌────────┼──────────┼─────────────────┤"))
        
        # TP row
        recall_pct = recall * 100
        miss_rate = 100 - recall_pct
        delta_str = ""
        if prev_tp is not None and prev_fn is not None:
            prev_recall = prev_tp / (prev_tp + prev_fn) if (prev_tp + prev_fn) > 0 else 0
            delta_recall = recall - prev_recall
            delta_str = f"  (Δ {delta_recall*100:+.1f}%)"
        self.logger.info(self._prefix(f" C │Positive│   {tp:4d}   │    {fn:4d}         │  Recall: {recall_pct:.1f}%{delta_str}"))
        self.logger.info(self._prefix(f" T │        │   (TP)   │    (FN)         │  Miss rate: {miss_rate:.1f}%"))
        self.logger.info(self._prefix(" U ├────────┼──────────┼─────────────────┤"))
        
        # TN row  
        spec_pct = specificity * 100
        false_alarm = 100 - spec_pct
        delta_str = ""
        if prev_tn is not None and prev_fp is not None:
            prev_spec = prev_tn / (prev_tn + prev_fp) if (prev_tn + prev_fp) > 0 else 0
            delta_spec = specificity - prev_spec
            delta_str = f"  (Δ {delta_spec*100:+.1f}%)"
        self.logger.info(self._prefix(f" A │Negative│   {fp:4d}   │   {tn:4d}          │  Specificity: {spec_pct:.1f}%{delta_str}"))
        self.logger.info(self._prefix(f" L │        │   (FP)   │    (TN)         │  False alarm: {false_alarm:.1f}%"))
        self.logger.info(self._prefix("   └────────┴──────────┴─────────────────┘"))
        self.logger.info(self._prefix(""))
        
        # Predictive values
        ppv = tp / (tp + fp) if (tp + fp) > 0 else 0
        npv = tn / (tn + fn) if (tn + fn) > 0 else 0
        self.logger.info(self._prefix(f"   Positive Predictive Value: {ppv*100:.1f}%  [Of predicted positive, {ppv*100:.0f}% correct]"))
        self.logger.info(self._prefix(f"   Negative Predictive Value: {npv*100:.1f}%  [Of predicted negative, {npv*100:.0f}% correct]"))
    
    def log_probability_bands(self, bands_data: any, band_trends: Dict[int, float] = None):
        """Log probability band analysis."""
        if not bands_data:
            return
        
        # Handle both dict with 'bands' key and plain list
        if isinstance(bands_data, dict) and 'bands' in bands_data:
            bands_list = bands_data['bands']
        elif isinstance(bands_data, list):
            bands_list = bands_data
        else:
            self.logger.warning("Probability bands data in unexpected format")
            return
        
        if not bands_list:
            return
        
        self.logger.info(self._prefix(""))
        self.logger.info(self._prefix("📊 PROBABILITY BANDS (10 deciles):"))
        self.logger.info(self._prefix(""))
        
        # Header - aligned to match data format string exactly
        # Data format: f"   {band:15s}  {w:5.3f}  {c:5d}  {a:6.3f}  {pa:5d}  {na:5d}    {pp:5d}  {np:5d}   {cor:7d}   {acc:5.1f}%  "
        # Spacing: 3sp + 15ch + 2sp + 5ch + 2sp + 5ch + 2sp + 6ch + 2sp + 5ch + 2sp + 5ch + 4sp + 5ch + 2sp + 5ch + 3sp + 7ch + 3sp + 6ch
        # First line: main column labels
        header_line1 = f"   {'Band':15s}  {'Width':>5s}  {'Count':>5s}  {' ':>6s}  {'Actual Classes':^12s}    {'Predicted':^12s}   {'Correct':>7s}   {'Accuracy':>6s}"
        # Second line: sub-labels (Prob, Pos, Neg)
        header_line2 = f"   {' ':15s}  {' ':>5s}  {' ':>5s}  {'Prob':>6s}  {'Pos':>5s}  {'Neg':>5s}    {'Pos':>5s}  {'Neg':>5s}   {' ':>7s}   {' ':>6s}"
        
        if band_trends:
            header_line1 += "     (Δ5)"
        
        self.logger.info(self._prefix(header_line1))
        self.logger.info(self._prefix(header_line2))
        self.logger.info(self._prefix("   " + "─" * (len(header_line1) - 3)))
        
        # Bands - handle both key formats (min_prob/max_prob or band_lower/band_upper)
        for i, band in enumerate(bands_list):
            # Get band range (handle both formats)
            if 'min_prob' in band and 'max_prob' in band:
                min_p, max_p = band['min_prob'], band['max_prob']
            elif 'band_lower' in band and 'band_upper' in band:
                min_p, max_p = band['band_lower'], band['band_upper']
            else:
                continue
            
            band_range = f"[{min_p:.2f},{max_p:.2f}]"
            width = max_p - min_p
            avg_pred = band.get('avg_pred', 0)
            count = band.get('count', band.get('n', 0))
            pos_actual = band.get('positive_actual', band.get('actual_pos', 0))
            neg_actual = band.get('negative_actual', band.get('actual_neg', 0))
            pos_pred = band.get('positive_predicted', band.get('pred_pos', 0))
            neg_pred = band.get('negative_predicted', band.get('pred_neg', 0))
            correct = band.get('correct', 0)
            accuracy = band.get('accuracy', band.get('correct_pct', 0) / 100 if 'correct_pct' in band else 0)
            
            # Quality indicator
            if accuracy > 0.80:
                indicator = "✅"
            elif accuracy > 0.60:
                indicator = "⚠️"
            else:
                indicator = "❌"
            
            # Trend if available
            trend_str = ""
            if band_trends and i in band_trends:
                trend = band_trends[i]
                trend_str = f"  {trend:+.0%}"
            
            self.logger.info(self._prefix(f"   {band_range:15s}  {width:5.3f}  {count:5d}  {avg_pred:6.3f}  {pos_actual:5d}  {neg_actual:5d}    {pos_pred:5d}  {neg_pred:5d}   {correct:7d}   {accuracy*100:5.1f}%  {indicator}{trend_str}"))
        
        # Interpretation
        self.logger.info(self._prefix(""))
        self.logger.info(self._prefix("   💡 Interpretation:"))
        low_bands_acc = np.mean([b.get('accuracy', b.get('correct_pct', 0) / 100 if 'correct_pct' in b else 0) for b in bands_list[:3]])
        mid_bands_acc = np.mean([b.get('accuracy', b.get('correct_pct', 0) / 100 if 'correct_pct' in b else 0) for b in bands_list[3:7]])
        high_bands_acc = np.mean([b.get('accuracy', b.get('correct_pct', 0) / 100 if 'correct_pct' in b else 0) for b in bands_list[7:]])
        
        self.logger.info(self._prefix(f"      - Low prob bands: {low_bands_acc*100:.0f}% avg accuracy  {'✅' if low_bands_acc > 0.75 else '⚠️'}"))
        self.logger.info(self._prefix(f"      - Mid prob bands: {mid_bands_acc*100:.0f}% avg accuracy  {'✅' if mid_bands_acc > 0.60 else '⚠️'}"))
        self.logger.info(self._prefix(f"      - High prob bands: {high_bands_acc*100:.0f}% avg accuracy  {'✅' if high_bands_acc > 0.75 else '⚠️'}"))
    
    def log_row_tracking(self, row_tracker: RowErrorTracker, current_epoch: int):
        """Log row-level error analysis with feature commonality."""
        if current_epoch not in row_tracker.epoch_results:
            return
        
        self.logger.info(self._prefix(""))
        self.logger.info(self._prefix(f"📊 PER-ROW ERROR TRACKING ({row_tracker.num_rows} validation samples):"))
        self.logger.info(self._prefix(""))
        
        # This epoch summary
        correct_flags = row_tracker.epoch_results[current_epoch]
        correct_count = sum(correct_flags)
        wrong_count = len(correct_flags) - correct_count
        accuracy_pct = correct_count / len(correct_flags) * 100 if correct_flags else 0
        
        # Delta from previous epoch
        if current_epoch > 0 and (current_epoch - 1) in row_tracker.epoch_results:
            prev_correct = sum(row_tracker.epoch_results[current_epoch - 1])
            delta_correct = correct_count - prev_correct
            delta_str = f"  (Δ {delta_correct:+d} from ep{current_epoch-1})"
        else:
            delta_str = ""
        
        self.logger.info(self._prefix(f"   This Epoch:     {correct_count} correct, {wrong_count} wrong ({accuracy_pct:.1f}% accuracy){delta_str}"))
        self.logger.info(self._prefix(""))
        
        # Cumulative patterns
        if current_epoch >= 1:
            self.logger.info(self._prefix(f"   Cumulative Patterns (epochs 0-{current_epoch}):"))
            
            cats = row_tracker.get_category_counts()
            total = row_tracker.num_rows
            
            # Show change from 5 epochs ago if available
            change_markers = {}
            if current_epoch >= 5:
                # Would need to store historical category counts - skip for now, just show current
                pass
            
            self.logger.info(self._prefix(f"   ├─ Always wrong:   {cats['always_wrong']:3d} rows ({cats['always_wrong']/total*100:4.1f}%)  {'⚠️  Check for mislabels' if cats['always_wrong'] > 0 else ''}"))
            self.logger.info(self._prefix(f"   ├─ Always right:   {cats['never_wrong']:3d} rows ({cats['never_wrong']/total*100:4.1f}%)  ✅ Easy examples"))
            self.logger.info(self._prefix(f"   ├─ Frequently wrong: {cats['frequently_wrong']:3d} rows ({cats['frequently_wrong']/total*100:4.1f}%)"))
            self.logger.info(self._prefix(f"   ├─ Sometimes wrong:  {cats['sometimes_wrong']:3d} rows ({cats['sometimes_wrong']/total*100:4.1f}%)"))
            self.logger.info(self._prefix(f"   └─ Rarely wrong:     {cats['rarely_wrong']:3d} rows ({cats['rarely_wrong']/total*100:4.1f}%)"))
            self.logger.info(self._prefix(""))
        
        # Hardest rows (in last 10 epochs)
        window = min(10, current_epoch + 1)
        hardest = row_tracker.get_hardest_rows(n=5, window=window)
        if hardest:
            self.logger.info(self._prefix(f"   Hardest 5 rows (in last {window} epochs):"))
            for row_idx, error_rate, gt in hardest:
                epochs_wrong = int(error_rate * window)
                self.logger.info(self._prefix(f"      Row {row_idx:4d}:  {epochs_wrong}/{window} wrong ({error_rate*100:.0f}%)  class='{gt}'"))
            self.logger.info(self._prefix(""))
        
        # Feature commonality analysis for hard rows
        if hardest and len(hardest) >= 3:
            hard_indices = [row_idx for row_idx, _, _ in hardest]
            commonalities = row_tracker.find_feature_commonality(hard_indices)
            
            if commonalities.get("categorical_patterns") or commonalities.get("numeric_patterns"):
                self.logger.info(self._prefix("   🔍 HARD ROW FEATURE ANALYSIS:"))
                self.logger.info(self._prefix(""))
                
                # Categorical patterns
                cat_patterns = commonalities.get("categorical_patterns", [])[:5]
                if cat_patterns:
                    self.logger.info(self._prefix("   Common Categorical Patterns (hard vs easy):"))
                    for pattern in cat_patterns:
                        hard_pct = pattern['hard_freq'] * 100
                        easy_pct = pattern['easy_freq'] * 100
                        diff = hard_pct - easy_pct
                        # Use len(hard_indices) for both - easy sample size matches hard sample size
                        self.logger.info(self._prefix(f"   ├─ {pattern['feature']}='{pattern['value']}': {pattern['hard_count']}/{len(hard_indices)} hard ({hard_pct:.0f}%) vs {pattern['easy_count']}/{len(hard_indices)} easy ({easy_pct:.0f}%)  Δ={diff:+.0f}% ⚠️"))
                    self.logger.info(self._prefix(""))
                
                # Numeric patterns
                num_patterns = commonalities.get("numeric_patterns", [])[:5]
                if num_patterns:
                    self.logger.info(self._prefix("   Numeric Feature Differences (hard vs easy):"))
                    for pattern in num_patterns:
                        self.logger.info(self._prefix(f"   ├─ {pattern['feature']}: hard={pattern['hard_mean']:.1f}±{pattern['hard_std']:.1f}  easy={pattern['easy_mean']:.1f}±{pattern['easy_std']:.1f}  (effect={pattern['effect_size']:.2f}) ⚠️"))
                    self.logger.info(self._prefix(""))
                
                self.logger.info(self._prefix("   💡 Hard rows tend to have these distinctive features"))
                self.logger.info(self._prefix(""))
                
                # Generate feature engineering suggestions and save to JSON
                suggestions = self._log_feature_engineering_suggestions(cat_patterns, num_patterns)
                
                # Export to JSON file if output directory exists
                if suggestions:
                    self._export_feature_suggestions_json(suggestions, cat_patterns, num_patterns)
        
        # Recently learned rows
        recently_learned = row_tracker.get_recently_learned(n=3, min_wrong_epochs=5)
        if recently_learned and current_epoch >= 10:
            self.logger.info(self._prefix("   Recently Learned (became correct after being wrong >5 epochs):"))
            for row_idx, learned_epoch, wrong_count in recently_learned:
                self.logger.info(self._prefix(f"      Row {row_idx:4d}: wrong(ep0-{learned_epoch-1}) → right(ep{learned_epoch}+)  took {learned_epoch} epochs"))
            self.logger.info(self._prefix(""))
    
    def _log_feature_engineering_suggestions(self, cat_patterns: list, num_patterns: list):
        """Generate and log feature engineering suggestions based on hard row patterns."""
        suggestions = []  # Structured suggestions for JSON export
        
        # Store for feature tracker access
        self._last_generated_suggestions = []
        
        # Detect text fields (free-form strings) vs true categorical fields
        # Text fields: long strings, spaces, high cardinality - suggest text features not interactions
        text_field_indicators = ['description', 'comment', 'notes', 'text', 'message', 'body', 'content']
        
        def is_likely_text_field(feature_name: str, value: str) -> bool:
            """Detect if a 'categorical' feature is actually free-form text."""
            name_lower = feature_name.lower()
            # Check for common text field name patterns
            if any(indicator in name_lower for indicator in text_field_indicators):
                return True
            # Check value characteristics
            if len(value) > 50:  # Long strings are likely text
                return True
            if ' ' in value and len(value.split()) > 5:  # Multi-word text
                return True
            return False
        
        # Separate text patterns from categorical patterns
        true_categorical = []
        text_patterns = []
        for pattern in cat_patterns[:5]:
            if is_likely_text_field(pattern['feature'], pattern['value']):
                text_patterns.append(pattern)
            else:
                true_categorical.append(pattern)
        
        # Suggest text-based features for detected text fields
        for pattern in text_patterns[:2]:  # Top 2 text fields
            feature = pattern['feature']
            suggestions.append({
                "type": "text_features",
                "features": [feature],
                "name": f"{feature}_text_stats",
                "description": f"Text features: {feature}_len, {feature}_words (text field detected)",
                "implementation": f"df['{feature}_len'] = df['{feature}'].astype(str).str.len(); df['{feature}_words'] = df['{feature}'].astype(str).str.split().str.len()",
                "rationale": f"{feature} appears to be free-form text - length/word count may be predictive"
            })
        
        # Suggest categorical interactions only for true categorical fields
        if true_categorical and len(true_categorical) >= 2:
            # Suggest interactions between top categorical features (excluding text fields)
            top_cats = [p['feature'] for p in true_categorical[:3]]
            if len(top_cats) >= 2:
                suggestions.append({
                    "type": "categorical_interaction",
                    "features": [top_cats[0], top_cats[1]],
                    "name": f"{top_cats[0]}_x_{top_cats[1]}",
                    "description": f"Interaction: {top_cats[0]} × {top_cats[1]} (categorical combo)",
                    "implementation": f"df['{top_cats[0]}_x_{top_cats[1]}'] = df['{top_cats[0]}'].astype(str) + '_' + df['{top_cats[1]}'].astype(str)",
                    "rationale": f"Both {top_cats[0]} and {top_cats[1]} distinguish hard rows from easy rows"
                })
        
        # Analyze numeric patterns for transformations and interactions
        if num_patterns:
            for pattern in num_patterns[:3]:
                feature = pattern['feature']
                hard_mean = pattern['hard_mean']
                easy_mean = pattern['easy_mean']
                effect_size = pattern['effect_size']
                
                # Large effect size (>0.8) suggests this feature is important
                if effect_size > 1.5:
                    # Suggest binning if means are very different
                    if hard_mean > easy_mean * 1.5:
                        threshold = hard_mean
                        suggestions.append({
                            "type": "numeric_binning",
                            "features": [feature],
                            "name": f"{feature}_high_risk",
                            "description": f"Binning: {feature}_high_risk (>{hard_mean:.1f}) - hard rows cluster here",
                            "implementation": f"df['{feature}_high_risk'] = (df['{feature}'] > {threshold:.2f}).astype(int)",
                            "threshold": float(threshold),
                            "rationale": f"Hard rows have {feature}={hard_mean:.1f} vs easy rows={easy_mean:.1f} (effect size={effect_size:.2f})"
                        })
                    elif easy_mean > hard_mean * 1.5:
                        threshold = hard_mean
                        suggestions.append({
                            "type": "numeric_binning",
                            "features": [feature],
                            "name": f"{feature}_low_risk",
                            "description": f"Binning: {feature}_low_risk (<{hard_mean:.1f}) - easy rows cluster here",
                            "implementation": f"df['{feature}_low_risk'] = (df['{feature}'] < {threshold:.2f}).astype(int)",
                            "threshold": float(threshold),
                            "rationale": f"Easy rows have {feature}={easy_mean:.1f} vs hard rows={hard_mean:.1f} (effect size={effect_size:.2f})"
                        })
                    
                    # Suggest ratios/interactions with other numeric features
                    if len(num_patterns) >= 2:
                        other_feature = num_patterns[1]['feature'] if num_patterns[0] == pattern else num_patterns[0]['feature']
                        suggestions.append({
                            "type": "numeric_ratio",
                            "features": [feature, other_feature],
                            "name": f"{feature}_div_{other_feature}",
                            "description": f"Ratio: {feature} / {other_feature}",
                            "implementation": f"df['{feature}_div_{other_feature}'] = df['{feature}'] / (df['{other_feature}'] + 1e-6)",
                            "rationale": f"Both {feature} and {other_feature} have large effect sizes"
                        })
        
        # Combine categorical and numeric for interaction features
        if cat_patterns and num_patterns:
            top_cat = cat_patterns[0]['feature']
            top_num = num_patterns[0]['feature']
            suggestions.append({
                "type": "conditional_numeric",
                "features": [top_num, top_cat],
                "name": f"{top_num}_by_{top_cat}",
                "description": f"Conditional: {top_num}_by_{top_cat} (group numeric by category)",
                "implementation": f"df['{top_num}_by_{top_cat}'] = df.groupby('{top_cat}')['{top_num}'].transform(lambda x: (x - x.mean()) / (x.std() + 1e-6))",
                "rationale": f"{top_cat} (categorical) and {top_num} (numeric) both distinguish hard rows"
            })
        
        # Age-specific patterns (credit-g domain knowledge)
        age_pattern = next((p for p in num_patterns if 'age' in p['feature'].lower()), None)
        duration_pattern = next((p for p in num_patterns if 'duration' in p['feature'].lower()), None)
        
        if age_pattern and age_pattern['hard_mean'] < age_pattern['easy_mean']:
            age_threshold = age_pattern['hard_mean']
            suggestions.append({
                "type": "domain_specific",
                "features": ["age"],
                "name": "younger_borrower",
                "description": f"Age group: younger_borrower (age < {age_threshold:.0f}) - higher risk segment",
                "implementation": f"df['younger_borrower'] = (df['age'] < {age_threshold:.0f}).astype(int)",
                "threshold": float(age_threshold),
                "rationale": f"Hard rows are younger (age={age_pattern['hard_mean']:.1f}) than easy rows (age={age_pattern['easy_mean']:.1f})"
            })
        
        if duration_pattern and age_pattern:
            suggestions.append({
                "type": "domain_specific",
                "features": ["duration", "age"],
                "name": "duration_age_risk_score",
                "description": "Risk score: (duration × age_factor) - combine temporal and demographic risk",
                "implementation": "df['duration_age_risk_score'] = df['duration'] * (1 + (40 - df['age']) / 40)",
                "rationale": "Younger borrowers with longer durations have higher risk"
            })
        
        # Store suggestions for JSON export
        if hasattr(self, '_feature_suggestions'):
            self._feature_suggestions = suggestions
        
        # Log suggestions if any were generated
        if suggestions:
            self.logger.info(self._prefix("   🔧 SUGGESTED FEATURE ENGINEERING:"))
            self.logger.info(self._prefix(""))
            for i, suggestion in enumerate(suggestions[:5], 1):  # Limit to top 5
                self.logger.info(self._prefix(f"   {i}. {suggestion['description']}"))
            self.logger.info(self._prefix(""))
        
        # Store suggestions for feature tracker
        self._last_generated_suggestions = suggestions
        
        return suggestions
    
    def _export_feature_suggestions_json(self, suggestions: list, cat_patterns: list, num_patterns: list):
        """Export feature engineering suggestions to JSON file."""
        import json
        from pathlib import Path
        from datetime import datetime
        
        # Try to save to qa.out directory
        output_dir = Path("qa.out")
        if not output_dir.exists():
            output_dir = Path(".")  # Fallback to current directory
        
        output_file = output_dir / "feature_engineering_suggestions.json"
        
        # Build comprehensive JSON structure
        export_data = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_suggestions": len(suggestions),
                "categorical_patterns_analyzed": len(cat_patterns),
                "numeric_patterns_analyzed": len(num_patterns)
            },
            "patterns": {
                "categorical": cat_patterns[:10],  # Top 10
                "numeric": num_patterns[:10]       # Top 10
            },
            "suggestions": suggestions,
            "usage": {
                "description": "Feature engineering suggestions based on hard row analysis",
                "how_to_use": [
                    "1. Review the 'suggestions' list",
                    "2. Copy the 'implementation' code for features you want to test",
                    "3. Add the code to your data preprocessing pipeline",
                    "4. Retrain and compare metrics",
                    "5. Keep features that improve validation performance"
                ],
                "example": "df['housing_x_credit_history'] = df['housing'].astype(str) + '_' + df['credit_history'].astype(str)"
            }
        }
        
        try:
            with open(output_file, 'w') as f:
                json.dump(export_data, f, indent=2)
            self.logger.info(self._prefix(f"   💾 Feature suggestions exported to: {output_file}"))
            self.logger.info(self._prefix(""))
        except Exception as e:
            self.logger.debug(self._prefix(f"   Could not export feature suggestions to JSON: {e}"))
    
    def log_threshold_section(self, optimal_threshold: float, default_threshold: float,
                             f1_optimal: float, f1_default: float,
                             acc_optimal: float, acc_default: float):
        """Log threshold optimization results."""
        self.logger.info(self._prefix(""))
        self.logger.info(self._prefix("🎯 THRESHOLD OPTIMIZATION:"))
        f1_gain = f1_optimal - f1_default
        acc_gain = acc_optimal - acc_default
        self.logger.info(self._prefix(f"   Selected: {optimal_threshold:.3f}  (vs default {default_threshold:.2f})"))
        self.logger.info(self._prefix(f"   Impact:   F1: {f1_optimal:.3f} (Δ={f1_gain:+.3f})  Acc: {acc_optimal*100:.1f}% (Δ={acc_gain*100:+.1f}%)"))
    
    def log_epoch_separator(self):
        """Log separator between epochs."""
        self.logger.info(self._prefix(""))
        self.logger.info(self._prefix("─" * 72))
        self.logger.info(self._prefix(""))

