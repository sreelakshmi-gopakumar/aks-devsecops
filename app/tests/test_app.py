import sys, os

# This line tells Python where to find our app.py file
# Without it, the test file can't import the Flask app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import app
import pytest


@pytest.fixture
def client():
    """
    A "fixture" is test setup code that runs before each test.
    Here we create a test version of our Flask app.
    app.test_client() gives us a fake browser we can use in tests
    — we can send requests to our app without a real browser.
    """
    app.config['TESTING'] = True
    with app.test_client() as c:
        yield c


def test_health_endpoint(client):
    """Test that /health returns 200 and says healthy"""
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'


def test_status_endpoint(client):
    """Test that /status returns 200"""
    response = client.get('/status')
    assert response.status_code == 200
    data = response.get_json()
    assert data['version'] == '1.0.0'


def test_root_endpoint(client):
    """Test that / returns 200"""
    response = client.get('/')
    assert response.status_code == 200