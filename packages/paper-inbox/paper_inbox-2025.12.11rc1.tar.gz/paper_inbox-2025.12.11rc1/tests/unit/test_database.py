# tests/test_database.py
"""Tests for database module"""
import os
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import pytest

from paper_inbox.modules.database.sqlwrapper import SQLiteWrapper
from paper_inbox.modules.database.utils import (
    does_database_exist,
    does_email_exist,
    get_database_handle,
    get_email_from_db_by_id,
    get_unprinted_emails,
    set_all_emails_as_printed,
    set_email_as_printed,
    update_email_attachments,
)


class TestDatabaseUtils:
    """Test database utility functions"""
    
    @pytest.fixture
    def temp_db(self):
        """Create a temporary database for testing"""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.sqlite3') as f:
            db_path = f.name
        
        # Patch at both the import location in utils AND where it's called
        with patch('paper_inbox.modules.database.utils.get_database_filepath') as mock_path:
            mock_path.return_value = Path(db_path)
            db = get_database_handle(delete_existing=True)
            yield db
        
        # Cleanup
        if os.path.exists(db_path):
            os.unlink(db_path)
    
    def test_does_database_exist_returns_false_when_no_db(self):
        """Test database existence check when no database exists"""
        # Create a truly nonexistent path
        nonexistent_path = Path(f'/tmp/nonexistent_{os.getpid()}_test.db')
        
        # Make absolutely sure it doesn't exist
        if nonexistent_path.exists():
            nonexistent_path.unlink()
        
        # Patch where the function is imported and used
        with patch('paper_inbox.modules.database.utils.get_database_filepath') as mock_path:
            mock_path.return_value = nonexistent_path
            result = does_database_exist()
            assert result is False
    
    def test_does_database_exist_returns_true_when_db_exists(self):
        """Test database existence check when database exists"""
        # Create a real temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.sqlite3') as f:
            temp_path = Path(f.name)
        
        try:
            with patch('paper_inbox.modules.database.utils.get_database_filepath') as mock_path:
                mock_path.return_value = temp_path
                result = does_database_exist()
                assert result is True
        finally:
            if temp_path.exists():
                temp_path.unlink()
    
    def test_get_database_handle_creates_database(self, temp_db):
        """Test that get_database_handle creates a database"""
        assert temp_db is not None
        assert temp_db.table_exists('emails')
    
    def test_does_email_exist_returns_false_for_nonexistent_email(self, temp_db):
        """Test email existence check for non-existent email"""
        result = does_email_exist('nonexistent-uid')
        assert result is False
    
    def test_does_email_exist_returns_true_for_existing_email(self, temp_db):
        """Test email existence check for existing email"""
        # Create an email
        email_data = {
            'email_uid': 'test-uid-123',
            'sent_date': datetime.now(),
            'subject': 'Test Subject',
            'body': 'Test Body',
        }
        temp_db.create('Email', email_data)
        
        result = does_email_exist('test-uid-123')
        assert result is True
    
    def test_get_email_from_db_by_id(self, temp_db):
        """Test retrieving email by ID"""
        email_data = {
            'email_uid': 'test-uid-456',
            'sent_date': datetime.now(),
            'subject': 'Test Subject 2',
            'body': 'Test Body 2',
        }
        email_id = temp_db.create('Email', email_data)
        
        result = get_email_from_db_by_id(email_id)
        assert result is not None
        assert result['subject'] == 'Test Subject 2'
    
    def test_get_unprinted_emails(self, temp_db):
        """Test getting unprinted emails"""
        # Create printed and unprinted emails
        temp_db.create('Email', {
            'email_uid': 'printed-1',
            'sent_date': datetime.now(),
            'subject': 'Printed Email',
            'body': 'Body',
            'printed': True
        })
        
        temp_db.create('Email', {
            'email_uid': 'unprinted-1',
            'sent_date': datetime.now(),
            'subject': 'Unprinted Email',
            'body': 'Body',
            'printed': False
        })
        
        result = get_unprinted_emails()
        assert len(result) == 1
        assert result[0]['subject'] == 'Unprinted Email'
    
    def test_set_email_as_printed(self, temp_db):
        """Test marking email as printed"""
        email_id = temp_db.create('Email', {
            'email_uid': 'test-uid-789',
            'sent_date': datetime.now(),
            'subject': 'Test',
            'body': 'Body',
            'printed': False
        })
        
        # set_email_as_printed doesn't return a value, it just performs the update
        set_email_as_printed(email_id)
        
        result = get_email_from_db_by_id(email_id)
        # Use truthiness check or == comparison (SQLite stores booleans as 0/1)
        assert result['printed']  # Truthy check (works for True or 1)
        assert result['printed_at'] is not None

    def test_update_email_attachments(self, temp_db):
        """Test updating email attachments"""
        email_id = temp_db.create('Email', {
            'email_uid': 'test-uid-101',
            'sent_date': datetime.now(),
            'subject': 'Test',
            'body': 'Body',
        })
        
        attachments = ['file1.pdf', 'file2.pdf']
        update_email_attachments(email_id, attachments)
        
        result = get_email_from_db_by_id(email_id)
        assert result['attachments'] == 'file1.pdf,file2.pdf'
    
    def test_set_all_emails_as_printed(self, temp_db):
        """Test marking all emails as printed"""
        # Create multiple unprinted emails
        for i in range(3):
            temp_db.create('Email', {
                'email_uid': f'uid-{i}',
                'sent_date': datetime.now(),
                'subject': f'Subject {i}',
                'body': 'Body',
                'printed': False
            })
        
        set_all_emails_as_printed()
        
        result = get_unprinted_emails()
        assert len(result) == 0


class TestSQLiteWrapper:
    """Test SQLiteWrapper class"""
    
    @pytest.fixture
    def db(self):
        """Create a temporary SQLite database"""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.sqlite3') as f:
            db_path = Path(f.name)
        
        db = SQLiteWrapper(db_path, debug=False)
        yield db
        
        # Cleanup
        if db_path.exists():
            db_path.unlink()
    
    def test_create_entity_type(self, db):
        """Test creating a new entity type"""
        db.create_entity_type('TestEntity', {
            'name': 'TEXT',
            'value': 'INTEGER'
        })
        
        # Entity type 'TestEntity' becomes table name 'test_entities' (plural snake_case)
        assert db.table_exists('test_entities')
    
    def test_create_and_find_entity(self, db):
        """Test creating and finding an entity"""
        db.create_entity_type('Person', {
            'name': 'TEXT',
            'age': 'INTEGER'
        })
        
        entity_id = db.create('Person', {'name': 'John', 'age': 30})
        result = db.find_one('Person', [['id', 'is', entity_id]])
        
        assert result is not None
        assert result['name'] == 'John'
        assert result['age'] == 30
    
    def test_update_entity(self, db):
        """Test updating an entity"""
        db.create_entity_type('Person', {
            'name': 'TEXT',
            'age': 'INTEGER'
        })
        
        entity_id = db.create('Person', {'name': 'Jane', 'age': 25})
        db.update('Person', entity_id, {'age': 26})
        
        result = db.find_one('Person', [['id', 'is', entity_id]])
        assert result['age'] == 26
    
    def test_delete_entity(self, db):
        """Test deleting an entity"""
        db.create_entity_type('Person', {
            'name': 'TEXT'
        })
        
        entity_id = db.create('Person', {'name': 'Bob'})
        db.delete('Person', entity_id, force=True)
        
        result = db.find_one('Person', [['id', 'is', entity_id]])
        assert result is None
    
    def test_find_with_filters(self, db):
        """Test finding entities with filters"""
        db.create_entity_type('Person', {
            'name': 'TEXT',
            'age': 'INTEGER'
        })
        
        db.create('Person', {'name': 'Alice', 'age': 30})
        db.create('Person', {'name': 'Bob', 'age': 25})
        db.create('Person', {'name': 'Charlie', 'age': 30})
        
        results = db.find('Person', [['age', 'is', 30]])
        assert len(results) == 2
    
    def test_find_with_limit(self, db):
        """Test finding entities with limit"""
        db.create_entity_type('Person', {
            'name': 'TEXT'
        })
        
        for i in range(5):
            db.create('Person', {'name': f'Person {i}'})
        
        results = db.find('Person', limit=3)
        assert len(results) == 3