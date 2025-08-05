"""
Pytest configuration and fixtures for services tests
"""

import pytest
import tempfile
import os
import sys
from pathlib import Path

# Add services to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / 'services'))

@pytest.fixture
def temp_database():
    """Provide a temporary database file for tests"""
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, 'test.db')
    
    yield db_path
    
    # Cleanup
    if os.path.exists(db_path):
        os.remove(db_path)
    os.rmdir(temp_dir)

@pytest.fixture
def temp_model_file():
    """Provide a temporary model file for tests"""
    temp_dir = tempfile.mkdtemp()
    model_path = os.path.join(temp_dir, 'test_model.gguf')
    
    # Create fake model file
    with open(model_path, 'w') as f:
        f.write('fake model content for testing')
    
    yield model_path
    
    # Cleanup
    if os.path.exists(model_path):
        os.remove(model_path)
    os.rmdir(temp_dir) 