import pytest
import sqlite3
import os
import tempfile
from run_tracker import RunTracker, init_database, register_flow

@pytest.fixture
def temp_db():
    """Create a temporary database for testing"""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    init_database(path)
    yield path
    if os.path.exists(path):
        os.remove(path)


def test_init_database(temp_db):
    """Test database initialization"""
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()

    # Check if tables exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {row[0] for row in cursor.fetchall()}

    assert 'flows' in tables
    assert 'runs' in tables
    conn.close()


def test_register_flow(temp_db):
    """Test flow registration"""
    register_flow(
        temp_db,
        flow_name='Test Flow',
        flow_path='/path/to/test.py',
        description='Test description'
    )

    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("SELECT flow_name, flow_path FROM flows WHERE flow_name='Test Flow'")
    row = cursor.fetchone()

    assert row is not None
    assert row[0] == 'Test Flow'
    assert row[1] == '/path/to/test.py'
    conn.close()


def test_run_tracker_success(temp_db):
    """Test successful run tracking"""
    # Register a flow first
    register_flow(temp_db, 'Test Flow', __file__)

    # Use RunTracker
    with RunTracker(temp_db, project_name='test_flow') as tracker:
        tracker.log("Test message")

    # Verify run was recorded
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("SELECT status FROM runs ORDER BY run_id DESC LIMIT 1")
    row = cursor.fetchone()

    assert row is not None
    assert row[0] == 'success'
    conn.close()
