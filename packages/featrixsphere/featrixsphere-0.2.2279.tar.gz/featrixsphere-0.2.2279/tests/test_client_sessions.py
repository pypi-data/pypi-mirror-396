#!/usr/bin/env python3
"""
Test Suite 1: Client Session Lifecycle

Tests session creation, metadata management, and lifecycle operations.
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
    """Create FeatrixSphere client - use local if SPHERE_URL set, else skip tests."""
    sphere_url = os.getenv("SPHERE_URL", "http://localhost:8000")
    client = FeatrixSphereClient(base_url=sphere_url)
    
    # Test connection
    try:
        # Simple health check - try to get sessions (will fail gracefully if server down)
        client._get_json("/health")
        return client
    except Exception as e:
        pytest.skip(f"Cannot connect to Sphere API at {sphere_url}: {e}")


@pytest.fixture
def sample_csv_file():
    """Create temporary CSV file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write("col1,col2,target\n")
        f.write("a,1,yes\n")
        f.write("b,2,no\n")
        f.write("c,3,yes\n")
        f.write("a,4,no\n")
        f.write("b,5,yes\n")
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    try:
        os.unlink(temp_path)
    except:
        pass


@pytest.fixture
def sample_dataframe():
    """Create sample DataFrame for testing."""
    return pd.DataFrame({
        'feature1': ['apple', 'banana', 'cherry', 'date', 'elderberry'],
        'feature2': [10, 20, 30, 40, 50],
        'feature3': [1.1, 2.2, 3.3, 4.4, 5.5],
        'target': ['good', 'bad', 'good', 'bad', 'good']
    })


class TestSessionCreation:
    """Test session creation from different sources."""
    
    def test_create_session_from_file(self, client, sample_csv_file):
        """Test creating session by uploading CSV file."""
        session_info = client.upload_file_and_create_session(
            file_path=Path(sample_csv_file),
            name="test_file_upload"
        )
        
        assert session_info is not None
        assert session_info.session_id is not None
        assert session_info.status in ["pending", "training", "completed"]
        
        # Cleanup
        try:
            client.mark_for_deletion(session_info.session_id)
        except:
            pass
    
    def test_create_session_from_dataframe(self, client, sample_dataframe):
        """Test creating session from pandas DataFrame."""
        session_info = client.upload_df_and_create_session(
            df=sample_dataframe,
            filename="test_df.csv",
            name="test_df_upload"
        )
        
        assert session_info is not None
        assert session_info.session_id is not None
        
        # Cleanup
        try:
            client.mark_for_deletion(session_info.session_id)
        except:
            pass
    
    def test_create_session_with_metadata(self, client, sample_dataframe):
        """Test creating session with custom metadata."""
        metadata = {
            "test_name": "pytest_session_creation",
            "test_number": 42,
            "test_bool": True
        }
        
        session_info = client.upload_df_and_create_session(
            df=sample_dataframe,
            filename="test_metadata.csv",
            name="test_with_metadata",
            metadata=metadata
        )
        
        assert session_info is not None
        
        # Verify metadata was stored
        status = client.get_session_status(session_info.session_id)
        assert status.user_metadata is not None
        assert status.user_metadata.get("test_name") == "pytest_session_creation"
        assert status.user_metadata.get("test_number") == 42
        
        # Cleanup
        try:
            client.mark_for_deletion(session_info.session_id)
        except:
            pass


class TestSessionMetadata:
    """Test metadata management operations."""
    
    def test_update_metadata_merge(self, client, sample_dataframe):
        """Test updating metadata in merge mode."""
        # Create session with initial metadata
        initial_metadata = {"key1": "value1", "key2": "value2"}
        session_info = client.upload_df_and_create_session(
            df=sample_dataframe,
            filename="test_merge.csv",
            metadata=initial_metadata
        )
        
        # Update with merge (should add new key, preserve existing)
        update_metadata = {"key3": "value3"}
        result = client.update_user_metadata(
            session_info.session_id,
            update_metadata,
            write_mode="merge"
        )
        
        # Verify all keys present
        status = client.get_session_status(session_info.session_id)
        assert status.user_metadata.get("key1") == "value1"
        assert status.user_metadata.get("key2") == "value2"
        assert status.user_metadata.get("key3") == "value3"
        
        # Cleanup
        try:
            client.mark_for_deletion(session_info.session_id)
        except:
            pass
    
    def test_update_metadata_replace(self, client, sample_dataframe):
        """Test updating metadata in replace mode."""
        # Create session with initial metadata
        initial_metadata = {"key1": "value1", "key2": "value2"}
        session_info = client.upload_df_and_create_session(
            df=sample_dataframe,
            filename="test_replace.csv",
            metadata=initial_metadata
        )
        
        # Update with replace (should replace all)
        update_metadata = {"key3": "value3"}
        result = client.update_user_metadata(
            session_info.session_id,
            update_metadata,
            write_mode="replace"
        )
        
        # Verify only new key present
        status = client.get_session_status(session_info.session_id)
        assert status.user_metadata.get("key1") is None
        assert status.user_metadata.get("key2") is None
        assert status.user_metadata.get("key3") == "value3"
        
        # Cleanup
        try:
            client.mark_for_deletion(session_info.session_id)
        except:
            pass


class TestSessionStatus:
    """Test session status and monitoring."""
    
    def test_get_session_status(self, client, sample_dataframe):
        """Test getting session status."""
        session_info = client.upload_df_and_create_session(
            df=sample_dataframe,
            filename="test_status.csv"
        )
        
        status = client.get_session_status(session_info.session_id)
        
        assert status is not None
        assert status.session_id == session_info.session_id
        assert hasattr(status, 'status')
        assert hasattr(status, 'jobs')
        
        # Cleanup
        try:
            client.mark_for_deletion(session_info.session_id)
        except:
            pass
    
    def test_get_session_models(self, client, sample_dataframe):
        """Test getting session models/predictors."""
        session_info = client.upload_df_and_create_session(
            df=sample_dataframe,
            filename="test_models.csv"
        )
        
        # Wait a bit for training to start
        import time
        time.sleep(2)
        
        models = client.get_session_models(session_info.session_id)
        
        assert models is not None
        assert isinstance(models, dict)
        
        # Cleanup
        try:
            client.mark_for_deletion(session_info.session_id)
        except:
            pass


class TestSessionLifecycle:
    """Test session lifecycle operations."""
    
    def test_session_deletion(self, client, sample_dataframe):
        """Test marking session for deletion."""
        session_info = client.upload_df_and_create_session(
            df=sample_dataframe,
            filename="test_delete.csv"
        )
        
        # Mark for deletion
        result = client.mark_for_deletion(session_info.session_id)
        
        assert result is not None
        # Session should still exist but marked for deletion
        status = client.get_session_status(session_info.session_id)
        assert status is not None


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "-s"])

