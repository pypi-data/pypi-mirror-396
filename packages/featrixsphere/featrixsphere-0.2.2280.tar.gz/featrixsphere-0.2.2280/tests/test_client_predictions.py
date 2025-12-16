#!/usr/bin/env python3
"""
Test Suite 3: Client Prediction Operations

Tests all prediction methods and exercises guardrails, calibration, and prediction code paths.
"""
import os
import sys
import tempfile
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


@pytest.fixture(scope="module")
def trained_session(client):
    """Create and train a session for prediction tests."""
    # Create training data
    df = pd.DataFrame({
        'age': [25, 35, 45, 55, 30, 40, 50, 60, 28, 38],
        'income': [30000, 50000, 70000, 90000, 40000, 60000, 80000, 100000, 35000, 55000],
        'city': ['NYC', 'LA', 'SF', 'NYC', 'LA', 'SF', 'NYC', 'LA', 'SF', 'NYC'],
        'target': ['no', 'no', 'yes', 'yes', 'no', 'yes', 'yes', 'yes', 'no', 'yes']
    })
    
    # Upload and create session
    session_info = client.upload_df_and_create_session(
        df=df,
        filename="test_predictions.csv",
        name="pytest_prediction_tests"
    )
    
    # Wait for training to complete (with timeout)
    try:
        completed = client.wait_for_session_completion(
            session_info.session_id,
            max_wait_time=600,  # 10 minutes max
            check_interval=5
        )
        
        if completed.status != "completed":
            pytest.skip(f"Training did not complete in time: {completed.status}")
        
        yield session_info.session_id
    except Exception as e:
        pytest.skip(f"Training failed: {e}")
    finally:
        # Cleanup after all tests
        try:
            client.mark_for_deletion(session_info.session_id)
        except:
            pass


class TestSinglePredictions:
    """Test single record predictions."""
    
    def test_predict_single_record(self, client, trained_session):
        """Test predicting a single record."""
        record = {
            'age': 42,
            'income': 65000,
            'city': 'SF'
        }
        
        result = client.predict(trained_session, record, target_column='target')
        
        assert result is not None
        assert 'prediction' in result or 'results' in result
    
    def test_predict_with_extended_result(self, client, trained_session):
        """Test prediction with extended_result flag (exercises guardrails)."""
        record = {
            'age': 42,
            'income': 65000,
            'city': 'SF'
        }
        
        result = client.predict(
            trained_session, 
            record, 
            target_column='target',
            extended_result=True
        )
        
        assert result is not None
        # Extended result should include additional data (guardrails, etc)
        assert 'prediction' in result or 'results' in result


class TestBatchPredictions:
    """Test batch prediction methods."""
    
    def test_predict_records(self, client, trained_session):
        """Test predicting multiple records."""
        records = [
            {'age': 30, 'income': 45000, 'city': 'NYC'},
            {'age': 50, 'income': 75000, 'city': 'LA'},
            {'age': 40, 'income': 60000, 'city': 'SF'},
        ]
        
        results = client.predict_records(
            trained_session,
            records,
            target_column='target'
        )
        
        assert results is not None
        assert isinstance(results, list)
        assert len(results) == len(records)
    
    def test_predict_df(self, client, trained_session):
        """Test predicting entire DataFrame."""
        test_df = pd.DataFrame({
            'age': [28, 38, 48],
            'income': [35000, 55000, 75000],
            'city': ['NYC', 'LA', 'SF']
        })
        
        result = client.predict_df(
            trained_session,
            test_df,
            target_column='target',
            show_progress_bar=False  # Disable for test
        )
        
        assert result is not None
        # Should return a dict with results
        assert 'results' in result or 'predictions' in result
    
    def test_predict_table(self, client, trained_session):
        """Test table-style predictions (column-oriented)."""
        table_data = {
            'age': [25, 35, 45],
            'income': [30000, 50000, 70000],
            'city': ['NYC', 'LA', 'SF']
        }
        
        result = client.predict_table(
            trained_session,
            table_data,
            target_column='target'
        )
        
        assert result is not None


class TestPredictionFormats:
    """Test different prediction input/output formats."""
    
    def test_predict_csv_file(self, client, trained_session):
        """Test predicting from CSV file."""
        # Create test CSV
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("age,income,city\n")
            f.write("32,48000,NYC\n")
            f.write("45,72000,LA\n")
            test_file = f.name
        
        try:
            # Create output file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
                output_file = f.name
            
            result = client.predict_csv_file(
                trained_session,
                input_file=test_file,
                output_file=output_file,
                target_column='target'
            )
            
            assert result is not None
            
            # Verify output file created
            assert Path(output_file).exists()
            
        finally:
            # Cleanup
            try:
                os.unlink(test_file)
                os.unlink(output_file)
            except:
                pass


class TestPredictorSelection:
    """Test predictor selection and management."""
    
    def test_list_predictors(self, client, trained_session):
        """Test listing available predictors."""
        predictors = client.list_predictors(
            trained_session,
            verbose=False
        )
        
        assert predictors is not None
        assert isinstance(predictors, dict)
    
    def test_get_available_predictors(self, client, trained_session):
        """Test getting available predictors."""
        predictors = client.get_available_predictors(trained_session)
        
        assert predictors is not None
        assert isinstance(predictors, dict)
    
    def test_predict_with_target_column_selection(self, client, trained_session):
        """Test prediction with explicit target column."""
        record = {'age': 35, 'income': 55000, 'city': 'LA'}
        
        result = client.predict(
            trained_session,
            record,
            target_column='target'
        )
        
        assert result is not None


class TestPredictionCache:
    """Test prediction caching and batching behavior."""
    
    def test_predictor_cache_creation(self, client, trained_session):
        """Test that PredictorCache is created."""
        cache = client.get_predictor(trained_session, target_column='target')
        
        assert cache is not None
        assert hasattr(cache, 'predict')
    
    def test_cached_prediction_stats(self, client, trained_session):
        """Test getting prediction statistics from cache."""
        cache = client.get_predictor(trained_session, target_column='target')
        
        # Make some predictions
        cache.predict({'age': 30, 'income': 45000, 'city': 'NYC'})
        cache.predict({'age': 40, 'income': 60000, 'city': 'LA'})
        
        stats = cache.get_stats()
        
        assert stats is not None
        # Should track prediction count, cache hits, etc


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "-s"])

