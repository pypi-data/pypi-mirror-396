#!/usr/bin/env python3
"""
Test Suite 5: Client Data Operations

Tests data management, encoding, and vector DB operations.
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


@pytest.fixture(scope="module")
def data_session(client):
    """Create a completed session for data operations."""
    df = pd.DataFrame({
        'name': ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve'],
        'age': [25, 30, 35, 40, 45],
        'score': [85, 90, 75, 95, 80],
        'category': ['A', 'B', 'A', 'C', 'B']
    })
    
    session_info = client.upload_df_and_create_session(
        df=df,
        filename="test_data_ops.csv",
        name="pytest_data_operations"
    )
    
    # Wait for completion
    try:
        completed = client.wait_for_session_completion(
            session_info.session_id,
            max_wait_time=300,
            check_interval=5
        )
        
        if completed.status != "completed":
            pytest.skip(f"Training did not complete: {completed.status}")
        
        yield session_info.session_id
    finally:
        try:
            client.mark_for_deletion(session_info.session_id)
        except:
            pass


class TestEncodingOperations:
    """Test encoding and embedding operations."""
    
    def test_encode_records(self, client, data_session):
        """Test encoding records to embeddings."""
        records = [
            {'name': 'Frank', 'age': 28, 'score': 88, 'category': 'A'},
            {'name': 'Grace', 'age': 32, 'score': 92, 'category': 'B'},
        ]
        
        embeddings = client.encode_records(data_session, records)
        
        assert embeddings is not None
        assert isinstance(embeddings, list)
        assert len(embeddings) == len(records)
    
    def test_get_embedding_space_columns(self, client, data_session):
        """Test getting column information from embedding space."""
        columns = client.get_embedding_space_columns(data_session)
        
        assert columns is not None
        assert isinstance(columns, (list, dict))


class TestVectorDatabase:
    """Test vector database operations."""
    
    def test_add_records(self, client, data_session):
        """Test adding new records to vector database."""
        new_records = [
            {'name': 'Henry', 'age': 27, 'score': 87, 'category': 'A'},
            {'name': 'Iris', 'age': 33, 'score': 93, 'category': 'C'},
        ]
        
        result = client.add_records(data_session, new_records)
        
        assert result is not None
    
    def test_vectordb_size(self, client, data_session):
        """Test getting vector database size."""
        size_info = client.vectordb_size(data_session)
        
        assert size_info is not None
        assert isinstance(size_info, dict)
    
    def test_similarity_search(self, client, data_session):
        """Test similarity search in vector database."""
        query_record = {'name': 'Test', 'age': 30, 'score': 85, 'category': 'A'}
        
        results = client.similarity_search(
            data_session,
            query_record,
            top_k=3
        )
        
        assert results is not None


class TestDataExport:
    """Test data export operations."""
    
    def test_export_data_csv(self, client, data_session):
        """Test exporting data as CSV."""
        result = client.export_data(data_session, format='csv')
        
        assert result is not None
    
    def test_export_data_json(self, client, data_session):
        """Test exporting data as JSON."""
        result = client.export_data(data_session, format='json')
        
        assert result is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

