"""Tests for MongoDB initialization and connection module."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from pymongo.errors import ServerSelectionTimeoutError, OperationFailure

from db import get_client, get_database, init_db, MONGO_URI, DB_NAME, COLLECTION_NAME


class TestGetClient:
    """Test get_client function."""
    
    @patch('db.MongoClient')
    def test_get_client_returns_client(self, mock_mongo_client):
        """Test that get_client returns a MongoClient instance."""
        mock_client_instance = Mock()
        mock_mongo_client.return_value = mock_client_instance
        
        client = get_client()
        
        assert client == mock_client_instance
        mock_mongo_client.assert_called_once_with(MONGO_URI, serverSelectionTimeoutMS=5000)


class TestGetDatabase:
    """Test get_database function."""
    
    @patch('db.get_client')
    def test_get_database_returns_database(self, mock_get_client):
        """Test that get_database returns a database instance."""
        mock_client = MagicMock()
        mock_db = Mock()
        mock_client.__getitem__.return_value = mock_db
        mock_get_client.return_value = mock_client
        
        db = get_database()
        
        assert db == mock_db
        mock_client.__getitem__.assert_called_once_with(DB_NAME)
    
    @patch('db.get_client')
    def test_get_database_uses_correct_db_name(self, mock_get_client):
        """Test that get_database accesses the correct database name."""
        mock_client = MagicMock()
        mock_db = Mock()
        mock_client.__getitem__.return_value = mock_db
        mock_get_client.return_value = mock_client
        
        get_database()
        
        mock_client.__getitem__.assert_called_with(DB_NAME)


class TestInitDb:
    """Test init_db function."""
    
    @patch('db.get_client')
    def test_init_db_successful(self, mock_get_client):
        """Test successful MongoDB initialization."""
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_collection = MagicMock()
        
        # Setup mocks
        mock_client.admin.command.return_value = {"ok": 1}
        mock_client.__getitem__.return_value = mock_db
        mock_db.list_collection_names.return_value = []
        mock_db.create_collection.return_value = mock_collection
        mock_db.__getitem__.return_value = mock_collection
        
        mock_get_client.return_value = mock_client
        
        result = init_db()
        
        assert result is True
        mock_client.admin.command.assert_called_once_with('ping')
        mock_db.create_collection.assert_called_once_with(COLLECTION_NAME)
        mock_collection.create_index.assert_any_call([("created_at", 1)])
        mock_collection.create_index.assert_any_call([("done", 1)])
    
    @patch('db.get_client')
    def test_init_db_collection_already_exists(self, mock_get_client):
        """Test initialization when collection already exists."""
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_collection = MagicMock()
        
        # Setup mocks - collection already exists
        mock_client.admin.command.return_value = {"ok": 1}
        mock_client.__getitem__.return_value = mock_db
        mock_db.list_collection_names.return_value = [COLLECTION_NAME]
        mock_db.__getitem__.return_value = mock_collection
        
        mock_get_client.return_value = mock_client
        
        result = init_db()
        
        assert result is True
        mock_db.create_collection.assert_not_called()
    
    @patch('db.get_client')
    def test_init_db_connection_timeout(self, mock_get_client):
        """Test init_db when MongoDB connection times out."""
        mock_client = Mock()
        mock_client.admin.command.side_effect = ServerSelectionTimeoutError(
            "Could not connect to MongoDB"
        )
        mock_get_client.return_value = mock_client
        
        result = init_db()
        
        assert result is False
    
    @patch('db.get_client')
    def test_init_db_operation_failure(self, mock_get_client):
        """Test init_db when MongoDB operation fails."""
        mock_client = MagicMock()
        mock_client.admin.command.return_value = {"ok": 1}
        mock_db = MagicMock()
        mock_client.__getitem__.return_value = mock_db
        mock_db.list_collection_names.side_effect = OperationFailure(
            "Operation failed"
        )
        
        mock_get_client.return_value = mock_client
        
        result = init_db()
        
        assert result is False
    
    @patch('db.get_client')
    def test_init_db_unexpected_error(self, mock_get_client):
        """Test init_db when an unexpected error occurs."""
        mock_client = Mock()
        mock_client.admin.command.side_effect = Exception("Unexpected error")
        mock_get_client.return_value = mock_client
        
        result = init_db()
        
        assert result is False
    
    @patch('db.get_client')
    def test_init_db_creates_correct_indexes(self, mock_get_client):
        """Test that init_db creates the correct indexes."""
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_collection = MagicMock()
        
        # Setup mocks
        mock_client.admin.command.return_value = {"ok": 1}
        mock_client.__getitem__.return_value = mock_db
        mock_db.list_collection_names.return_value = []
        mock_db.create_collection.return_value = mock_collection
        mock_db.__getitem__.return_value = mock_collection
        
        mock_get_client.return_value = mock_client
        
        init_db()
        
        # Verify indexes were created
        calls = mock_collection.create_index.call_args_list
        assert len(calls) == 2
        
        # Check created_at index
        assert mock_collection.create_index.call_count == 2
        created_at_indexed = any(call[0][0] == [("created_at", 1)] for call in calls)
        done_indexed = any(call[0][0] == [("done", 1)] for call in calls)
        
        assert created_at_indexed
        assert done_indexed


class TestMongoUriConfiguration:
    """Test MongoDB URI configuration."""
    
    def test_mongo_uri_is_configured(self):
        """Test that MONGO_URI is configured (either localhost or mongodb hostname)."""
        # MONGO_URI should contain the mongodb connection string
        assert MONGO_URI is not None
        assert "mongodb://" in MONGO_URI
        assert "27017" in MONGO_URI
        assert "notesdb" in MONGO_URI
    
    def test_db_name_constant(self):
        """Test that DB_NAME constant is set correctly."""
        assert DB_NAME == "notesdb"
    
    def test_collection_name_constant(self):
        """Test that COLLECTION_NAME constant is set correctly."""
        assert COLLECTION_NAME == "notes"


class TestIntegrationInitDb:
    """Integration tests for init_db (when mocks are fully setup)."""
    
    @patch('db.get_client')
    def test_init_db_idempotency(self, mock_get_client):
        """Test that init_db can be called multiple times safely."""
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_collection = MagicMock()
        
        # Setup mocks
        mock_client.admin.command.return_value = {"ok": 1}
        mock_client.__getitem__.return_value = mock_db
        mock_db.list_collection_names.return_value = []
        mock_db.create_collection.return_value = mock_collection
        mock_db.__getitem__.return_value = mock_collection
        
        mock_get_client.return_value = mock_client
        
        # Call init_db twice
        result1 = init_db()
        
        # On second call, collection exists
        mock_db.list_collection_names.return_value = [COLLECTION_NAME]
        result2 = init_db()
        
        assert result1 is True
        assert result2 is True
