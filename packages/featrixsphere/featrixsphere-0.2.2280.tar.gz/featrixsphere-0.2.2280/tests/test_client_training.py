#!/usr/bin/env python3
"""
Test Suite 2: Client Training Operations

Tests training APIs including ES training, SP training, and foundation models.
"""
import os
import sys
import pytest
import pandas as pd
from pathlib import Path

# Add parent directory and src/lib to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src" / "lib"))

from featrixsphere import FeatrixSphereClient


@pytest.fixture(scope="module")
def client():
    """Create FeatrixSphere client."""
    sphere_url = os.getenv("SPHERE_URL", "http://localhost:8000")
    client = FeatrixSphereClient(base_url=sphere_url)
    
    try:
        client._get_json("/health")
        return client
    except Exception as e:
        pytest.skip(f"Cannot connect to Sphere API at {sphere_url}: {e}")


@pytest.fixture
def training_dataframe():
    """Create larger DataFrame suitable for training."""
    import numpy as np
    np.random.seed(42)
    
    n_samples = 100
    return pd.DataFrame({
        'feature1': np.random.choice(['A', 'B', 'C', 'D'], n_samples),
        'feature2': np.random.randint(1, 100, n_samples),
        'feature3': np.random.uniform(0, 1, n_samples),
        'feature4': np.random.choice(['cat', 'dog', 'bird'], n_samples),
        'target': np.random.choice(['positive', 'negative'], n_samples)
    })


class TestEmbeddingSpaceTraining:
    """Test embedding space training operations."""
    
    def test_basic_session_training(self, client, training_dataframe):
        """Test standard session creation triggers ES training."""
        session_info = client.upload_df_and_create_session(
            df=training_dataframe,
            filename="test_es_training.csv",
            name="pytest_es_training"
        )
        
        assert session_info is not None
        
        # Get session status - should show train_es job
        status = client.get_session_status(session_info.session_id)
        assert status.jobs is not None
        
        # Cleanup
        try:
            client.mark_for_deletion(session_info.session_id)
        except:
            pass


class TestSinglePredictorTraining:
    """Test single predictor training operations."""
    
    def test_train_single_predictor(self, client, training_dataframe):
        """Test training a single predictor."""
        # Create session
        session_info = client.upload_df_and_create_session(
            df=training_dataframe,
            filename="test_sp.csv",
            name="pytest_sp_training"
        )
        
        # Wait for ES to complete
        try:
            completed = client.wait_for_session_completion(
                session_info.session_id,
                max_wait_time=300,
                check_interval=5
            )
            
            if completed.status != "completed":
                pytest.skip(f"ES training did not complete: {completed.status}")
            
            # Train single predictor
            sp_result = client.train_single_predictor(
                session_info.session_id,
                target_column='target',
                target_column_type='set'
            )
            
            assert sp_result is not None
            
        finally:
            try:
                client.mark_for_deletion(session_info.session_id)
            except:
                pass


class TestFoundationModelOperations:
    """Test foundation model training operations."""
    
    @pytest.mark.slow
    def test_train_on_foundational_model(self, client, training_dataframe):
        """Test training a predictor on a foundation model."""
        # This requires an existing foundation model
        # We'll skip if no foundation models available
        pytest.skip("Requires pre-existing foundation model")


class TestTrainingMetrics:
    """Test getting training metrics and status."""
    
    def test_get_training_metrics(self, client, training_dataframe):
        """Test getting training metrics during/after training."""
        session_info = client.upload_df_and_create_session(
            df=training_dataframe,
            filename="test_metrics.csv"
        )
        
        # Try to get metrics (may be empty if training just started)
        metrics = client.get_training_metrics(session_info.session_id)
        
        assert metrics is not None
        assert isinstance(metrics, dict)
        
        # Cleanup
        try:
            client.mark_for_deletion(session_info.session_id)
        except:
            pass


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

