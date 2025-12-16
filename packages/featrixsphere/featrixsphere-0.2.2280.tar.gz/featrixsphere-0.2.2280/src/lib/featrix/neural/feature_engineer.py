"""
Feature Engineering from Suggestions

Applies feature engineering transformations based on hard row analysis.
Can be serialized and applied consistently to training and prediction data.
"""
import json
import logging
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Optional
import pickle

logger = logging.getLogger(__name__)


class FeatureEngineer:
    """
    Apply feature engineering transformations from suggestions JSON.
    
    Usage:
        # Training time
        engineer = FeatureEngineer.from_json("qa.out/feature_engineering_suggestions.json")
        df_enhanced = engineer.fit_transform(df)
        
        # Save with model
        engineer.save("model_dir/feature_engineer.pkl")
        
        # Prediction time
        engineer = FeatureEngineer.load("model_dir/feature_engineer.pkl")
        new_df_enhanced = engineer.transform(new_df)
    """
    
    def __init__(self, suggestions: Optional[List[Dict[str, Any]]] = None):
        """
        Initialize feature engineer.
        
        Args:
            suggestions: List of feature engineering suggestions (from JSON)
        """
        self.suggestions = suggestions or []
        self.applied_features = []  # Track which features were successfully applied
        self.fit_params = {}  # Store parameters learned during fit (e.g., thresholds)
        self.is_fitted = False
    
    @classmethod
    def from_json(cls, json_path: str, max_features: Optional[int] = None) -> 'FeatureEngineer':
        """
        Load feature suggestions from JSON file.
        
        Args:
            json_path: Path to feature_engineering_suggestions.json
            max_features: Maximum number of features to apply (default: all)
        
        Returns:
            FeatureEngineer instance
        """
        json_path = Path(json_path)
        
        if not json_path.exists():
            logger.warning(f"Feature suggestions file not found: {json_path}")
            return cls(suggestions=[])
        
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
            
            suggestions = data.get('suggestions', [])
            
            if max_features is not None:
                suggestions = suggestions[:max_features]
            
            logger.info(f"✅ Loaded {len(suggestions)} feature suggestions from {json_path}")
            
            return cls(suggestions=suggestions)
            
        except Exception as e:
            logger.error(f"Failed to load feature suggestions from {json_path}: {e}")
            return cls(suggestions=[])
    
    def fit_transform(self, df: pd.DataFrame, verbose: bool = True) -> pd.DataFrame:
        """
        Fit to training data and apply transformations.
        
        Args:
            df: Input DataFrame
            verbose: Log which features are being added
        
        Returns:
            Enhanced DataFrame with new features
        """
        self.is_fitted = True
        return self._apply_transformations(df, is_fit=True, verbose=verbose)
    
    def transform(self, df: pd.DataFrame, verbose: bool = False) -> pd.DataFrame:
        """
        Apply transformations to new data (e.g., during prediction).
        
        Args:
            df: Input DataFrame
            verbose: Log which features are being added
        
        Returns:
            Enhanced DataFrame with new features
        """
        if not self.is_fitted:
            raise RuntimeError("FeatureEngineer must be fit before transform. Use fit_transform() first.")
        
        return self._apply_transformations(df, is_fit=False, verbose=verbose)
    
    def _apply_transformations(self, df: pd.DataFrame, is_fit: bool, verbose: bool) -> pd.DataFrame:
        """
        Apply feature transformations to DataFrame.
        
        Args:
            df: Input DataFrame
            is_fit: Whether this is fit (training) or transform (prediction)
            verbose: Log progress
        
        Returns:
            Enhanced DataFrame
        """
        df_enhanced = df.copy()
        
        if verbose and self.suggestions:
            logger.info("")
            logger.info("=" * 80)
            logger.info(f"🔧 APPLYING FEATURE ENGINEERING ({len(self.suggestions)} suggestions)")
            logger.info("=" * 80)
        
        success_count = 0
        
        for i, suggestion in enumerate(self.suggestions, 1):
            try:
                feature_name = suggestion.get('name')
                feature_type = suggestion.get('type')
                features = suggestion.get('features', [])
                
                # Check if required source features exist
                missing_features = [f for f in features if f not in df_enhanced.columns]
                if missing_features:
                    if verbose:
                        logger.warning(f"   ⚠️  Skipping {feature_name}: missing features {missing_features}")
                    continue
                
                # Apply transformation based on type
                if feature_type == 'categorical_interaction':
                    df_enhanced = self._apply_categorical_interaction(df_enhanced, suggestion)
                
                elif feature_type == 'numeric_binning':
                    df_enhanced = self._apply_numeric_binning(df_enhanced, suggestion, is_fit)
                
                elif feature_type == 'numeric_ratio':
                    df_enhanced = self._apply_numeric_ratio(df_enhanced, suggestion)
                
                elif feature_type == 'conditional_numeric':
                    df_enhanced = self._apply_conditional_numeric(df_enhanced, suggestion, is_fit)
                
                elif feature_type == 'domain_specific':
                    df_enhanced = self._apply_domain_specific(df_enhanced, suggestion)
                
                else:
                    if verbose:
                        logger.warning(f"   ⚠️  Unknown feature type: {feature_type}")
                    continue
                
                # Track successful application
                if is_fit:
                    self.applied_features.append(feature_name)
                
                success_count += 1
                
                if verbose:
                    logger.info(f"   ✅ [{i}/{len(self.suggestions)}] Added: {feature_name} ({feature_type})")
            
            except Exception as e:
                if verbose:
                    logger.error(f"   ❌ Failed to add {feature_name}: {e}")
                continue
        
        if verbose:
            logger.info("")
            logger.info(f"   Total: {success_count}/{len(self.suggestions)} features added successfully")
            logger.info(f"   Original columns: {len(df.columns)}, Enhanced columns: {len(df_enhanced.columns)}")
            logger.info("=" * 80)
            logger.info("")
        
        return df_enhanced
    
    def _apply_categorical_interaction(self, df: pd.DataFrame, suggestion: Dict) -> pd.DataFrame:
        """Create interaction between categorical features."""
        feature_name = suggestion['name']
        features = suggestion['features']
        
        # Combine categorical values with underscore
        df[feature_name] = df[features[0]].astype(str) + '_' + df[features[1]].astype(str)
        
        return df
    
    def _apply_numeric_binning(self, df: pd.DataFrame, suggestion: Dict, is_fit: bool) -> pd.DataFrame:
        """Create binary feature from numeric threshold."""
        feature_name = suggestion['name']
        source_feature = suggestion['features'][0]
        threshold = suggestion.get('threshold')
        
        if threshold is None:
            logger.warning(f"No threshold provided for {feature_name}")
            return df
        
        # Create binary indicator
        if 'high_risk' in feature_name:
            df[feature_name] = (df[source_feature] > threshold).astype(int)
        else:  # low_risk
            df[feature_name] = (df[source_feature] < threshold).astype(int)
        
        return df
    
    def _apply_numeric_ratio(self, df: pd.DataFrame, suggestion: Dict) -> pd.DataFrame:
        """Create ratio between two numeric features."""
        feature_name = suggestion['name']
        features = suggestion['features']
        
        # Compute ratio with small epsilon to avoid division by zero
        df[feature_name] = df[features[0]] / (df[features[1]] + 1e-6)
        
        return df
    
    def _apply_conditional_numeric(self, df: pd.DataFrame, suggestion: Dict, is_fit: bool) -> pd.DataFrame:
        """Create grouped/standardized numeric feature by category."""
        feature_name = suggestion['name']
        numeric_feature = suggestion['features'][0]
        categorical_feature = suggestion['features'][1]
        
        # Group by category and standardize within each group
        df[feature_name] = df.groupby(categorical_feature)[numeric_feature].transform(
            lambda x: (x - x.mean()) / (x.std() + 1e-6)
        )
        
        return df
    
    def _apply_domain_specific(self, df: pd.DataFrame, suggestion: Dict) -> pd.DataFrame:
        """Apply domain-specific transformations."""
        feature_name = suggestion['name']
        features = suggestion['features']
        implementation = suggestion.get('implementation', '')
        
        # Use the implementation code directly
        # This is safe because we generated it ourselves
        try:
            # Execute the implementation in a controlled namespace
            namespace = {'df': df, 'pd': pd, 'np': np}
            exec(implementation, namespace)
            df = namespace['df']
        except Exception as e:
            logger.warning(f"Failed to apply domain-specific feature {feature_name}: {e}")
        
        return df
    
    def save(self, path: str):
        """
        Save FeatureEngineer to disk.
        
        Args:
            path: Output path for pickle file
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'wb') as f:
            pickle.dump(self, f)
        
        logger.info(f"💾 Saved FeatureEngineer to {path}")
    
    @classmethod
    def load(cls, path: str) -> 'FeatureEngineer':
        """
        Load FeatureEngineer from disk.
        
        Args:
            path: Path to pickle file
        
        Returns:
            FeatureEngineer instance
        """
        path = Path(path)
        
        if not path.exists():
            logger.warning(f"FeatureEngineer file not found: {path}, returning empty engineer")
            return cls()
        
        with open(path, 'rb') as f:
            engineer = pickle.load(f)
        
        logger.info(f"✅ Loaded FeatureEngineer from {path} ({len(engineer.applied_features)} features)")
        
        return engineer
    
    def get_feature_names(self) -> List[str]:
        """Get list of feature names that were successfully applied."""
        return self.applied_features.copy()
    
    def __repr__(self):
        status = "fitted" if self.is_fitted else "not fitted"
        return f"FeatureEngineer({len(self.suggestions)} suggestions, {len(self.applied_features)} applied, {status})"

