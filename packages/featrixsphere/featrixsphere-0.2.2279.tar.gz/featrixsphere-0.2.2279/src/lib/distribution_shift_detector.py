#!/usr/bin/env python3
"""
Distribution Shift Detection for Single Predictor Training

Detects when training data for a single predictor differs significantly from
the data used to train the base embedding space.

Checks for:
- Null rate differences (e.g., ES had 5% nulls, SP data has 95% nulls)
- Out-of-vocabulary values (values not seen during ES training)
- Type mismatches (ES saw floats, SP data has strings)
- Distribution shifts (KL divergence, Chi-square test)
- Extreme value differences (min/max changes)
"""
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from collections import Counter

logger = logging.getLogger(__name__)


class DistributionShiftReport:
    """Container for distribution shift analysis results."""
    
    def __init__(self, column_name: str):
        self.column_name = column_name
        self.issues = []
        self.warnings = []
        self.info = []
        self.metrics = {}
        
    def add_issue(self, message: str, severity: str = "error"):
        """Add a critical issue (will likely cause training problems)."""
        self.issues.append({'message': message, 'severity': severity})
    
    def add_warning(self, message: str):
        """Add a warning (may affect quality but won't break training)."""
        self.warnings.append(message)
    
    def add_info(self, message: str):
        """Add informational message."""
        self.info.append(message)
    
    def add_metric(self, name: str, value: float):
        """Add a numeric metric."""
        self.metrics[name] = value
    
    def has_critical_issues(self) -> bool:
        """Return True if there are critical issues."""
        return len([i for i in self.issues if i['severity'] == 'error']) > 0
    
    def has_warnings(self) -> bool:
        """Return True if there are warnings."""
        return len(self.warnings) > 0
    
    @property
    def severity(self) -> str:
        """Get overall severity level for this column."""
        if self.has_critical_issues():
            return 'CRITICAL'
        elif self.has_warnings():
            return 'WARNING'
        else:
            return 'OK'
    
    @property
    def kl_divergence(self) -> Optional[float]:
        """Get KL divergence metric if available."""
        return self.metrics.get('kl_divergence')
    
    def to_dict(self) -> dict:
        """Convert report to JSON-serializable dictionary."""
        return {
            'column_name': self.column_name,
            'has_critical_issues': self.has_critical_issues(),
            'has_warnings': self.has_warnings(),
            'issues': self.issues,
            'warnings': self.warnings,
            'info': self.info,
            'metrics': self.metrics,
        }
    
    def log_report(self, log_level: int = logging.INFO):
        """Log the full report."""
        logger.log(log_level, f"📊 DISTRIBUTION ANALYSIS: '{self.column_name}'")
        logger.log(log_level, "─" * 80)
        
        # Log critical issues
        if self.issues:
            for issue in self.issues:
                if issue['severity'] == 'error':
                    logger.error(f"   ❌ {issue['message']}")
                else:
                    logger.warning(f"   ⚠️  {issue['message']}")
        
        # Log warnings
        if self.warnings:
            for warning in self.warnings:
                logger.warning(f"   ⚠️  {warning}")
        
        # Log info
        if self.info:
            for info in self.info:
                logger.log(log_level, f"   ℹ️  {info}")
        
        # Log metrics
        if self.metrics:
            logger.log(log_level, f"   📈 Metrics:")
            for name, value in self.metrics.items():
                logger.log(log_level, f"      {name}: {value}")


class DistributionShiftDetector:
    """
    Detect distribution shifts between ES training data and SP training data.
    """
    
    def __init__(self, embedding_space):
        """
        Initialize detector with base embedding space.
        
        Args:
            embedding_space: The EmbeddingSpace object that was trained
        """
        self.es = embedding_space
        self.es_stats = self._extract_es_stats()
    
    @staticmethod
    def _normalize_value_for_comparison(val) -> str:
        """
        Normalize a value for comparison with ES vocabulary.
        
        This handles the issue where floats like 1.0 are converted to '1.0' 
        instead of '1', causing false OOV errors.
        
        Args:
            val: Any value (float, int, str, etc.)
            
        Returns:
            Normalized string representation
        """
        if pd.isna(val) or val in ['nan', 'NaN', 'None', '', ' ']:
            return str(val)
        
        try:
            # Try to convert to float, then back to int if it's a whole number
            # This converts: 1.0 -> '1', 0.0 -> '0', but keeps 1.5 -> '1.5'
            float_val = float(val)
            if float_val.is_integer():
                return str(int(float_val))
            return str(float_val)
        except (ValueError, TypeError):
            # Not numeric, return as-is
            return str(val)
    
    def _extract_es_stats(self) -> Dict:
        """
        Extract statistics from the embedding space's codec metadata.
        
        Note: train_input_data is intentionally excluded from ES pickle files to keep them small.
        Instead, we extract stats from col_codecs which ARE pickled and contain all the
        information we need (vocabulary, min/max, null handling, etc).
        
        Returns:
            dict mapping column_name → stats dict
        """
        stats = {}
        
        # Use codec metadata instead of train_input_data (which is excluded from pickle)
        if not hasattr(self.es, 'col_codecs') or not self.es.col_codecs:
            logger.warning("⚠️  Cannot extract ES stats - col_codecs not available")
            return stats
        
        logger.info(f"📊 Extracting ES distribution stats from {len(self.es.col_codecs)} codecs...")
        
        for col_name, codec in self.es.col_codecs.items():
            col_stats = {}
            col_stats['codec_type'] = type(codec).__name__
            
            # Get vocabulary for categorical codecs (SetCodec, StringCodec, etc.)
            if hasattr(codec, 'members') and codec.members is not None:
                col_stats['vocabulary'] = set(codec.members)
                col_stats['vocab_size'] = len(codec.members)
                logger.debug(f"   '{col_name}': {col_stats['codec_type']} with {col_stats['vocab_size']} unique values")
            
            # Get min/max for numeric codecs (ScalarCodec, IntCodec, FloatCodec)
            if hasattr(codec, 'min') and hasattr(codec, 'max'):
                col_stats['min'] = float(codec.min) if codec.min is not None else None
                col_stats['max'] = float(codec.max) if codec.max is not None else None
                if col_stats['min'] is not None and col_stats['max'] is not None:
                    logger.debug(f"   '{col_name}': {col_stats['codec_type']} range [{col_stats['min']:.2f}, {col_stats['max']:.2f}]")
            
            # Get null handling info if available
            if hasattr(codec, 'handle_nans'):
                col_stats['handles_nulls'] = codec.handle_nans
            
            # Determine if this is a numeric or categorical column based on codec type
            numeric_codec_types = ['ScalarCodec', 'IntCodec', 'FloatCodec', 'NumericCodec']
            categorical_codec_types = ['SetCodec', 'StringCodec', 'CategoricalCodec', 'DomainCodec', 'UrlCodec']
            
            codec_type_name = type(codec).__name__
            if codec_type_name in numeric_codec_types:
                col_stats['is_numeric'] = True
                col_stats['is_categorical'] = False
            elif codec_type_name in categorical_codec_types:
                col_stats['is_numeric'] = False
                col_stats['is_categorical'] = True
            else:
                # Unknown codec type - try to infer from available attributes
                col_stats['is_numeric'] = hasattr(codec, 'min') and hasattr(codec, 'max')
                col_stats['is_categorical'] = hasattr(codec, 'members')
            
            stats[col_name] = col_stats
        
        logger.info(f"✅ Extracted stats for {len(stats)} columns from ES codecs")
        return stats
    
    def analyze_column(self, col_name: str, sp_data: pd.Series) -> DistributionShiftReport:
        """
        Analyze a single column for distribution shift.
        
        Args:
            col_name: Column name
            sp_data: Series containing SP training data for this column
            
        Returns:
            DistributionShiftReport with findings
        """
        report = DistributionShiftReport(col_name)
        
        # Check if column existed in ES
        if col_name not in self.es_stats:
            report.add_issue(f"Column '{col_name}' NOT in base ES training data (new column)")
            return report
        
        es_col_stats = self.es_stats[col_name]
        
        # 1. NULL RATE CHECK (ES codec metadata doesn't include historical null rates)
        sp_null_count = sp_data.isnull().sum()
        sp_null_rate = sp_null_count / len(sp_data)
        
        report.add_metric('sp_null_rate', sp_null_rate)
        
        # Warn about extremely high null rates
        if sp_null_rate > 0.9:
            report.add_issue(f"SP data is {sp_null_rate*100:.1f}% NULL - almost all nulls!", severity='error')
        elif sp_null_rate > 0.5:
            report.add_warning(f"SP data is {sp_null_rate*100:.1f}% NULL - high null rate")
        elif sp_null_rate > 0.1:
            report.add_info(f"Null rate: {sp_null_rate*100:.1f}%")
        
        # 2. OUT-OF-VOCABULARY CHECK (for categorical columns)
        if 'vocabulary' in es_col_stats:
            es_vocab = set(es_col_stats['vocabulary'])
            
            # Get raw SP values (before normalization) for logging
            sp_values_raw = set(sp_data.dropna().unique())
            
            # CRITICAL: Normalize SP values before comparison to handle float->string conversion
            # E.g., 1.0 should become '1' not '1.0' to match ES vocab
            sp_data_normalized = sp_data.dropna().apply(self._normalize_value_for_comparison)
            sp_values_normalized = set(sp_data_normalized.unique())
            
            oov_values = sp_values_normalized - es_vocab
            missing_values = es_vocab - sp_values_normalized
            
            # Count OOV based on normalized values
            oov_count = sum(sp_data_normalized.isin(oov_values))
            oov_rate = oov_count / len(sp_data)
            
            report.add_metric('oov_count', len(oov_values))
            report.add_metric('oov_rate', oov_rate)
            report.add_metric('es_vocab_size', len(es_vocab))
            report.add_metric('sp_unique_values', len(sp_values_normalized))
            
            # For low-cardinality, show full vocab comparison
            max_card = 20
            show_full = len(es_vocab) <= max_card or len(sp_values_normalized) <= max_card
            
            # Determine if raw and normalized are different
            raw_vs_normalized_differ = sp_values_raw != sp_values_normalized
            
            if oov_rate > 0.5:
                msg = f"{oov_rate*100:.1f}% OUT-OF-VOCABULARY (not in ES). "
                if show_full:
                    msg += f"\n       ES vocab ({len(es_vocab)}): {sorted(es_vocab)}"
                    if raw_vs_normalized_differ:
                        msg += f"\n       SP vocab RAW ({len(sp_values_raw)}): {sorted(sp_values_raw)}"
                        msg += f"\n       SP vocab NORMALIZED ({len(sp_values_normalized)}): {sorted(sp_values_normalized)}"
                    else:
                        msg += f"\n       SP vocab ({len(sp_values_normalized)}): {sorted(sp_values_normalized)}"
                    msg += f"\n       NEW in SP: {sorted(oov_values)}" if oov_values else "\n       NEW in SP: (none)"
                    msg += f"\n       MISSING from SP: {sorted(missing_values)}" if missing_values else "\n       MISSING from SP: (none)"
                else:
                    msg += f"{len(oov_values)} new in SP (ES had {len(es_vocab)}). NEW in SP: {list(oov_values)[:5]}"
                report.add_issue(msg, severity='error')
            elif oov_rate > 0.1:
                msg = f"{oov_rate*100:.1f}% of values are out-of-vocabulary. "
                msg += f"{len(oov_values)} new in SP. NEW values (examples): {list(oov_values)[:5]}"
                if raw_vs_normalized_differ and show_full:
                    msg += f"\n       SP vocab RAW: {sorted(sp_values_raw)}"
                    msg += f"\n       SP vocab NORMALIZED: {sorted(sp_values_normalized)}"
                report.add_warning(msg)
            elif len(oov_values) > 0:
                report.add_info(f"{len(oov_values)} new values ({oov_rate*100:.2f}% of data)")
            else:
                msg = f"✅ All values in ES vocabulary ({len(sp_values_normalized)} unique values, ES had {len(es_vocab)})"
                if raw_vs_normalized_differ:
                    msg += f"\n       SP vocab RAW: {sorted(sp_values_raw)} → NORMALIZED: {sorted(sp_values_normalized)}"
                report.add_info(msg)
        
        # 3. TYPE COMPATIBILITY CHECK (use codec type instead of dtype)
        sp_is_numeric = pd.api.types.is_numeric_dtype(sp_data)
        sp_is_categorical = pd.api.types.is_object_dtype(sp_data) or pd.api.types.is_categorical_dtype(sp_data)
        
        es_is_numeric = es_col_stats.get('is_numeric', False)
        es_is_categorical = es_col_stats.get('is_categorical', False)
        
        # SMART TYPE COMPATIBILITY: If SP is numeric but ES is categorical, check if after
        # normalization ALL SP values match ES vocab (e.g., binary flags: 0.0/1.0 -> '0'/'1')
        type_mismatch = sp_is_numeric != es_is_numeric
        compatible_after_normalization = False
        
        if type_mismatch and sp_is_numeric and es_is_categorical and 'vocabulary' in es_col_stats:
            # Check if ALL normalized SP values are in ES vocab (allowing for nulls)
            sp_normalized = sp_data.dropna().apply(self._normalize_value_for_comparison)
            sp_normalized_values = set(sp_normalized.unique())
            es_vocab = set(es_col_stats['vocabulary'])
            
            if sp_normalized_values.issubset(es_vocab):
                # All values match after normalization - this is actually compatible!
                compatible_after_normalization = True
                report.add_info(
                    f"✅ Type compatible after normalization: SP has numeric dtype but values "
                    f"{sorted(sp_normalized_values)} match ES categorical vocab. "
                    f"ES codec={es_col_stats.get('codec_type', 'unknown')}"
                )
        
        if type_mismatch and not compatible_after_normalization:
            sp_dtype = str(sp_data.dtype)
            es_codec_type = es_col_stats.get('codec_type', 'unknown')
            report.add_issue(
                f"TYPE MISMATCH: SP has {sp_dtype} (numeric={sp_is_numeric}), "
                f"ES had {es_codec_type} codec (numeric={es_is_numeric}). "
                f"Numeric vs categorical mismatch!",
                severity='error'
            )
        elif not type_mismatch:
            # Compatible types
            codec_type = es_col_stats.get('codec_type', 'unknown')
            report.add_info(f"✅ Type compatible: ES codec={codec_type}, SP dtype={sp_data.dtype}")
        
        # 4. NUMERIC DISTRIBUTION SHIFT (for numeric columns)
        if sp_is_numeric and es_is_numeric:
            sp_clean = sp_data.dropna()
            if len(sp_clean) > 0:
                sp_mean = float(sp_clean.mean())
                sp_std = float(sp_clean.std())
                sp_min = float(sp_clean.min())
                sp_max = float(sp_clean.max())
                
                es_min = es_col_stats.get('min')
                es_max = es_col_stats.get('max')
                
                report.add_metric('sp_mean', sp_mean)
                report.add_metric('sp_min', sp_min)
                report.add_metric('sp_max', sp_max)
                
                if es_min is not None:
                    report.add_metric('es_min', es_min)
                if es_max is not None:
                    report.add_metric('es_max', es_max)
                
                # Check for out-of-range values
                if es_min is not None and es_max is not None:
                    values_below_min = (sp_clean < es_min).sum()
                    values_above_max = (sp_clean > es_max).sum()
                    out_of_range_count = values_below_min + values_above_max
                    out_of_range_rate = out_of_range_count / len(sp_clean)
                    
                    if out_of_range_rate > 0.1:
                        report.add_warning(
                            f"{out_of_range_rate*100:.1f}% of values ({out_of_range_count:,} rows) outside ES range "
                            f"[{es_min:.4g}, {es_max:.4g}]. SP range: [{sp_min:.4g}, {sp_max:.4g}]"
                        )
                    elif out_of_range_count > 0:
                        report.add_info(
                            f"{out_of_range_count:,} values ({out_of_range_rate*100:.2f}%) outside ES range. "
                            f"ES: [{es_min:.4g}, {es_max:.4g}], SP: [{sp_min:.4g}, {sp_max:.4g}]"
                        )
                    else:
                        report.add_info(f"✅ All values within ES range [{es_min:.4g}, {es_max:.4g}]")
                    
                    # Calculate KL divergence for numeric columns
                    try:
                        # Compute histogram-based KL divergence
                        sp_clean_vals = sp_clean.values
                        
                        # Use 50 bins for histogram
                        if es_min is not None and es_max is not None:
                            # Use ES range for bins
                            range_min = min(es_min, sp_min)
                            range_max = max(es_max, sp_max)
                        else:
                            range_min = sp_min
                            range_max = sp_max
                        
                        # Create histogram bins
                        bins = np.linspace(range_min, range_max, 51)  # 50 bins
                        
                        # Compute SP histogram
                        sp_hist, _ = np.histogram(sp_clean_vals, bins=bins, density=True)
                        sp_hist = sp_hist + 1e-10  # Avoid zero probabilities
                        sp_hist = sp_hist / sp_hist.sum()  # Normalize
                        
                        # For ES, we don't have the raw data, so assume uniform distribution within range
                        # This is a rough approximation - ideally we'd have ES histogram in metadata
                        es_hist = np.ones_like(sp_hist) / len(sp_hist)
                        
                        # Compute KL divergence: KL(SP || ES)
                        kl_div = np.sum(sp_hist * np.log(sp_hist / es_hist))
                        report.add_metric('kl_divergence', float(kl_div))
                        
                        if kl_div > 1.0:
                            report.add_warning(f"HIGH distribution shift: KL divergence = {kl_div:.4f}")
                        elif kl_div > 0.5:
                            report.add_info(f"Moderate distribution shift: KL divergence = {kl_div:.4f}")
                        else:
                            report.add_info(f"✅ Low distribution shift: KL divergence = {kl_div:.4f}")
                    
                    except Exception as kl_error:
                        logger.debug(f"Could not compute KL divergence for {col_name}: {kl_error}")
        
        # 5. CATEGORICAL DISTRIBUTION SHIFT (for categorical columns)
        if 'vocabulary' in es_col_stats and not sp_is_numeric:
            try:
                # Compute KL divergence based on value frequencies
                es_vocab = es_col_stats['vocabulary']
                sp_clean = sp_data.dropna()
                
                if len(sp_clean) > 0:
                    # Get SP value frequencies
                    sp_counts = sp_clean.value_counts()
                    sp_probs = sp_counts / len(sp_clean)
                    
                    # For ES, assume uniform distribution over vocabulary (we don't have frequencies)
                    # This is a rough approximation
                    es_prob = 1.0 / len(es_vocab) if len(es_vocab) > 0 else 0
                    
                    # Compute KL divergence: KL(SP || ES)
                    # Only for values in ES vocabulary (OOV handled separately)
                    kl_div = 0.0
                    for value, sp_prob in sp_probs.items():
                        if value in es_vocab:
                            # KL contribution: p * log(p/q)
                            kl_div += sp_prob * np.log(sp_prob / es_prob)
                    
                    report.add_metric('kl_divergence', float(kl_div))
                    
                    if kl_div > 1.0:
                        report.add_warning(f"HIGH categorical shift: KL divergence = {kl_div:.4f}")
                    elif kl_div > 0.5:
                        report.add_info(f"Moderate categorical shift: KL divergence = {kl_div:.4f}")
                    else:
                        report.add_info(f"✅ Low categorical shift: KL divergence = {kl_div:.4f}")
            
            except Exception as kl_error:
                logger.debug(f"Could not compute categorical KL divergence for {col_name}: {kl_error}")
        
        return report
    
    def analyze_dataframe(self, sp_df: pd.DataFrame, target_column: str = None) -> Dict[str, DistributionShiftReport]:
        """
        Analyze entire dataframe for distribution shifts.
        
        Args:
            sp_df: Single predictor training dataframe
            target_column: Optional target column to exclude from analysis
            
        Returns:
            Dict mapping column_name → DistributionShiftReport
        """
        reports = {}
        
        for col in sp_df.columns:
            if col == target_column:
                continue  # Skip target column (it may not have been in ES)
            
            if col.startswith('__featrix'):
                continue  # Skip internal columns
            
            report = self.analyze_column(col, sp_df[col])
            reports[col] = report
        
        # IMPORTANT: Check for ES columns missing from SP data
        sp_columns = set(sp_df.columns)
        for es_col in self.es_stats.keys():
            if es_col == target_column:
                continue  # Skip target
            if es_col not in sp_columns:
                # This ES column is missing from SP data - create a report
                missing_report = DistributionShiftReport(es_col)
                missing_report.add_warning(f"Column was in ES training data but MISSING from SP data - will use defaults/nulls")
                reports[es_col] = missing_report
        
        return reports
    
    def log_summary(self, reports: Dict[str, DistributionShiftReport]):
        """
        Log a summary of all distribution shift findings.
        
        Args:
            reports: Dict of column reports from analyze_dataframe()
        """
        logger.info("=" * 80)
        logger.info("📊 DISTRIBUTION SHIFT DETECTION SUMMARY")
        logger.info("=" * 80)
        
        # Count issues by severity
        critical_columns = []
        warning_columns = []
        ok_columns = []
        new_in_sp_columns = []  # In SP but not in ES
        missing_from_sp_columns = []  # In ES but not in SP
        
        for col_name, report in reports.items():
            if col_name not in self.es_stats:
                new_in_sp_columns.append(col_name)
            elif report.has_critical_issues():
                critical_columns.append(col_name)
            elif report.has_warnings():
                # Check if this is a "missing from SP" warning
                if any("MISSING from SP data" in w for w in report.warnings):
                    missing_from_sp_columns.append(col_name)
                else:
                    warning_columns.append(col_name)
            else:
                ok_columns.append(col_name)
        
        logger.info(f"📈 Total columns analyzed: {len(reports)}")
        logger.info(f"   ✅ OK: {len(ok_columns)} columns")
        logger.info(f"   ⚠️  Warnings: {len(warning_columns)} columns")
        logger.info(f"   ❌ Critical: {len(critical_columns)} columns")
        logger.info(f"   ➕ New in SP (not in ES): {len(new_in_sp_columns)} columns")
        if len(missing_from_sp_columns) > 0:
            logger.warning(f"   ➖ Missing from SP (were in ES): {len(missing_from_sp_columns)} columns")
        logger.info("")
        
        # Log critical columns
        if critical_columns:
            logger.error("❌ CRITICAL ISSUES DETECTED:")
            for col in critical_columns:
                report = reports[col]
                logger.error(f"   '{col}':")
                for issue in report.issues:
                    if issue['severity'] == 'error':
                        logger.error(f"      • {issue['message']}")
            logger.error("")
        
        # Log warning columns
        if warning_columns:
            logger.warning("⚠️  WARNINGS:")
            for col in warning_columns[:10]:  # Show first 10
                report = reports[col]
                logger.warning(f"   '{col}':")
                for warning in report.warnings[:2]:  # Show first 2 warnings per column
                    logger.warning(f"      • {warning}")
            if len(warning_columns) > 10:
                logger.warning(f"   ... and {len(warning_columns) - 10} more columns with warnings")
            logger.warning("")
        
        # Log ES columns missing from SP data
        if missing_from_sp_columns:
            logger.warning("⚠️  ES COLUMNS MISSING FROM SP DATA:")
            logger.warning("   These columns were used to train the embedding space but are absent from predictor training data.")
            logger.warning("   The encoder will use default/null values for these columns, which may reduce prediction quality.")
            for col in missing_from_sp_columns[:20]:
                logger.warning(f"   • '{col}'")
            if len(missing_from_sp_columns) > 20:
                logger.warning(f"   ... and {len(missing_from_sp_columns) - 20} more missing columns")
            logger.warning("")
        
        # Log new columns
        if new_in_sp_columns:
            logger.info("➕ NEW COLUMNS (not in ES training data):")
            for col in new_in_sp_columns[:20]:
                logger.info(f"   • '{col}'")
            if len(new_in_sp_columns) > 20:
                logger.info(f"   ... and {len(new_in_sp_columns) - 20} more new columns")
            logger.info("")
        
        logger.info("=" * 80)
        
        # Return summary stats
        return {
            'total_columns': len(reports),
            'ok_columns': len(ok_columns),
            'warning_columns': len(warning_columns),
            'critical_columns': len(critical_columns),
            'new_columns': len(new_in_sp_columns),
            'missing_from_sp': len(missing_from_sp_columns),
            'has_critical_issues': len(critical_columns) > 0,
        }


def detect_distribution_shift(embedding_space, sp_train_df: pd.DataFrame, target_column: str = None) -> Dict:
    """
    Convenience function to detect and log distribution shifts.
    
    Args:
        embedding_space: Base EmbeddingSpace object
        sp_train_df: Single predictor training dataframe
        target_column: Target column to exclude from analysis
        
    Returns:
        Dict with 'summary' and 'column_reports' keys containing analysis results
    """
    detector = DistributionShiftDetector(embedding_space)
    reports = detector.analyze_dataframe(sp_train_df, target_column=target_column)
    summary = detector.log_summary(reports)
    
    # Log detailed reports for columns with issues
    logger.info("=" * 80)
    logger.info("📋 DETAILED COLUMN ANALYSIS")
    logger.info("=" * 80)
    
    for col_name, report in reports.items():
        if report.has_critical_issues() or report.has_warnings():
            report.log_report(log_level=logging.INFO)
    
    logger.info("=" * 80)
    
    # Convert reports to JSON-serializable format
    column_reports = {}
    for col_name, report in reports.items():
        column_reports[col_name] = report.to_dict()
    
    # Return both summary and detailed column reports
    return {
        'summary': summary,
        'column_reports': column_reports,
        'metadata': {
            'target_column': target_column,
            'sp_total_rows': len(sp_train_df),
            'sp_total_columns': len(sp_train_df.columns),
            'es_total_columns': len(detector.es_stats),
        }
    }


if __name__ == '__main__':
    # Test the detector
    logging.basicConfig(level=logging.INFO)
    
    print("\n" + "=" * 80)
    print("DISTRIBUTION SHIFT DETECTOR TEST")
    print("=" * 80 + "\n")
    
    # Create mock ES with some stats
    class MockES:
        def __init__(self):
            self.train_input_data = None
            self.col_codecs = {}
    
    # Create mock ES data
    import pandas as pd
    es_df = pd.DataFrame({
        'feature1': [1, 2, 3, 4, 5] * 100,
        'feature2': ['A', 'B', 'C'] * 166 + ['A', 'B'],
        'feature3': [10.0, 20.0, 30.0] * 166 + [10.0, 20.0],
    })
    
    # Create SP data with shifts
    sp_df = pd.DataFrame({
        'feature1': [100, 200, 300] * 50,  # Out of range
        'feature2': ['D', 'E', 'F'] * 50,  # Out of vocabulary
        'feature3': [None] * 150,  # Lots of nulls
    })
    
    class MockInputData:
        def __init__(self, df):
            self.df = df
    
    es = MockES()
    es.train_input_data = MockInputData(es_df)
    
    # Run detection
    summary = detect_distribution_shift(es, sp_df, target_column='target')
    
    print("\n✅ Test complete!\n")

