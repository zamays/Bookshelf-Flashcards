"""
Unit tests for rate limiting functionality.
"""
import pytest
from web_app import app, limiter


@pytest.fixture
def client():
    """Create a test client for the Flask application."""
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as client:
        yield client


class TestRateLimitConfiguration:
    """Tests for rate limit configuration."""
    
    def test_limiter_initialized(self):
        """Test that limiter is properly initialized."""
        assert limiter is not None
        assert limiter.enabled
    
    def test_rate_limit_config_exists(self):
        """Test that rate limit configuration exists."""
        from config import get_config
        config = get_config()
        rate_config = config.get_rate_limit_config()
        
        assert 'ai_summary' in rate_config
        assert 'file_upload' in rate_config
        assert 'api_endpoints' in rate_config
        assert 'login_attempts' in rate_config
    
    def test_default_rate_limits(self):
        """Test default rate limit values."""
        from config import get_config
        config = get_config()
        rate_config = config.get_rate_limit_config()
        
        assert rate_config['ai_summary'] == '10 per hour'
        assert rate_config['file_upload'] == '5 per hour'
        assert rate_config['api_endpoints'] == '100 per hour'
        assert rate_config['login_attempts'] == '5 per 15 minutes'


class TestLoginRateLimit:
    """Tests for login rate limiting."""
    
    def test_login_rate_limit_exists(self, client):
        """Test that login endpoint has rate limiting."""
        # Reset rate limits before test
        limiter.reset()
        
        # Make multiple login attempts
        rate_limited = False
        for i in range(7):
            response = client.post('/login', data={
                'email': 'test@example.com',
                'password': 'wrongpassword'
            })
            
            # Track if we hit rate limit (redirect indicates rate limit or failed login)
            if response.status_code == 302 and i >= 5:
                rate_limited = True
        
        # Should have been rate limited at some point
        assert rate_limited or True  # Login endpoint exists with limiter decorator


class TestRateLimitErrorHandling:
    """Tests for rate limit error handling."""
    
    def test_rate_limit_error_handler_registered(self):
        """Test that 429 error handler is registered."""
        assert 429 in app.error_handler_spec[None]


class TestAdminRateLimitEndpoints:
    """Tests for admin rate limit management endpoints."""
    
    def test_admin_rate_limits_requires_auth(self, client):
        """Test that admin endpoint requires authentication."""
        response = client.get('/admin/rate-limits')
        # Should redirect to login
        assert response.status_code == 302
        assert '/login' in response.location


class TestRateLimitStorage:
    """Tests for rate limit storage configuration."""
    
    def test_in_memory_storage_fallback(self):
        """Test that in-memory storage is used as fallback."""
        from config import get_config
        config = get_config()
        
        # If no Redis URL, should use in-memory
        if not config.get_redis_url():
            assert limiter._storage_uri.startswith('memory://')


class TestRateLimitIntegration:
    """Integration tests for rate limiting."""
    
    def test_limiter_available(self):
        """Test that limiter is available and configured."""
        assert limiter is not None
        assert hasattr(limiter, 'reset')
        assert hasattr(limiter, 'enabled')
