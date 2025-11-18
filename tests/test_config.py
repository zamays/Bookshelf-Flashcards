"""
Unit tests for config.py module.
"""
import os
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from config import (
    Config,
    ConfigurationError,
    EnvironmentSecretProvider,
    FileSecretProvider,
    CloudSecretProvider,
    get_config,
    reset_config
)


class TestEnvironmentSecretProvider:
    """Tests for EnvironmentSecretProvider."""
    
    def test_get_secret_exists(self):
        """Test getting an existing environment variable."""
        with patch.dict(os.environ, {'TEST_KEY': 'test_value'}):
            provider = EnvironmentSecretProvider()
            assert provider.get_secret('TEST_KEY') == 'test_value'
    
    def test_get_secret_not_exists(self):
        """Test getting a non-existent environment variable."""
        provider = EnvironmentSecretProvider()
        assert provider.get_secret('NONEXISTENT_KEY') is None


class TestFileSecretProvider:
    """Tests for FileSecretProvider."""
    
    def test_get_secret_file_exists(self, tmp_path):
        """Test getting secret from existing file."""
        secret_file = tmp_path / "test_secret"
        secret_file.write_text("secret_value\n")
        
        provider = FileSecretProvider(secrets_dir=str(tmp_path))
        assert provider.get_secret('test_secret') == 'secret_value'
    
    def test_get_secret_file_not_exists(self, tmp_path):
        """Test getting secret from non-existent file."""
        provider = FileSecretProvider(secrets_dir=str(tmp_path))
        assert provider.get_secret('nonexistent') is None
    
    def test_get_secret_strips_whitespace(self, tmp_path):
        """Test that secret value is stripped of whitespace."""
        secret_file = tmp_path / "test_secret"
        secret_file.write_text("  secret_value  \n")
        
        provider = FileSecretProvider(secrets_dir=str(tmp_path))
        assert provider.get_secret('test_secret') == 'secret_value'
    
    def test_get_secret_read_error(self, tmp_path):
        """Test handling of file read errors."""
        # Create a directory instead of a file
        secret_dir = tmp_path / "test_secret"
        secret_dir.mkdir()
        
        provider = FileSecretProvider(secrets_dir=str(tmp_path))
        # Should return None and log warning
        assert provider.get_secret('test_secret') is None


class TestCloudSecretProvider:
    """Tests for CloudSecretProvider."""
    
    def test_aws_provider_success(self):
        """Test successful AWS secret retrieval."""
        # Mock boto3 at the import level
        mock_boto3 = MagicMock()
        mock_client = MagicMock()
        mock_client.get_secret_value.return_value = {
            'SecretString': 'aws_secret_value'
        }
        mock_boto3.client.return_value = mock_client
        
        with patch.dict('sys.modules', {'boto3': mock_boto3, 'botocore': MagicMock(), 'botocore.exceptions': MagicMock()}):
            provider = CloudSecretProvider(provider_type='aws')
            assert provider.get_secret('test_secret') == 'aws_secret_value'
    
    def test_aws_provider_not_found(self):
        """Test AWS secret not found."""
        # Create a custom exception class
        class ClientError(Exception):
            pass
        
        mock_boto3 = MagicMock()
        mock_client = MagicMock()
        mock_client.get_secret_value.side_effect = ClientError("Secret not found")
        mock_boto3.client.return_value = mock_client
        
        mock_botocore = MagicMock()
        mock_botocore.exceptions.ClientError = ClientError
        
        with patch.dict('sys.modules', {'boto3': mock_boto3, 'botocore': mock_botocore, 'botocore.exceptions': mock_botocore.exceptions}):
            provider = CloudSecretProvider(provider_type='aws')
            assert provider.get_secret('test_secret') is None
    
    def test_aws_provider_boto3_not_installed(self):
        """Test AWS provider when boto3 is not installed."""
        # Don't mock boto3 - it won't be in sys.modules
        provider = CloudSecretProvider(provider_type='aws')
        # Should handle ImportError gracefully
        assert provider.get_secret('test_secret') is None
    
    def test_gcp_provider_success(self):
        """Test successful GCP secret retrieval."""
        mock_sm = MagicMock()
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.payload.data = b'gcp_secret_value'
        mock_client.access_secret_version.return_value = mock_response
        mock_sm.SecretManagerServiceClient.return_value = mock_client
        
        mock_google_cloud = MagicMock()
        mock_google_cloud.secretmanager = mock_sm
        
        with patch.dict('sys.modules', {'google': MagicMock(), 'google.cloud': mock_google_cloud, 'google.cloud.secretmanager': mock_sm, 'google.api_core': MagicMock(), 'google.api_core.exceptions': MagicMock()}), \
             patch.dict(os.environ, {'GCP_PROJECT_ID': 'test-project'}):
            provider = CloudSecretProvider(provider_type='gcp')
            assert provider.get_secret('test_secret') == 'gcp_secret_value'
    
    def test_gcp_provider_no_project_id(self):
        """Test GCP provider without project ID."""
        mock_sm = MagicMock()
        mock_google_cloud = MagicMock()
        mock_google_cloud.secretmanager = mock_sm
        
        with patch.dict('sys.modules', {'google': MagicMock(), 'google.cloud': mock_google_cloud, 'google.cloud.secretmanager': mock_sm}), \
             patch.dict(os.environ, {}, clear=True):
            provider = CloudSecretProvider(provider_type='gcp')
            assert provider.get_secret('test_secret') is None
    
    def test_unknown_provider_type(self):
        """Test unknown cloud provider type."""
        provider = CloudSecretProvider(provider_type='unknown')
        assert provider.get_secret('test_secret') is None


class TestConfigInit:
    """Tests for Config initialization."""
    
    def test_init_default(self):
        """Test default initialization."""
        with patch.dict(os.environ, {}, clear=True):
            config = Config()
            assert config.secret_providers
            assert config.is_production is False
    
    def test_init_with_env_file(self, tmp_path):
        """Test initialization with .env file."""
        env_file = tmp_path / ".env"
        env_file.write_text("TEST_KEY=test_value\n")
        
        config = Config(env_file=str(env_file))
        assert config.secret_providers
    
    def test_detect_production_environment_var(self):
        """Test production detection via ENVIRONMENT variable."""
        with patch.dict(os.environ, {'ENVIRONMENT': 'production'}):
            config = Config()
            assert config.is_production is True
    
    def test_detect_production_render(self):
        """Test production detection on Render.com."""
        with patch.dict(os.environ, {'RENDER': 'true'}):
            config = Config()
            assert config.is_production is True
    
    def test_detect_production_heroku(self):
        """Test production detection on Heroku."""
        with patch.dict(os.environ, {'HEROKU_APP_NAME': 'myapp'}):
            config = Config()
            assert config.is_production is True


class TestConfigGetSecret:
    """Tests for Config.get_secret method."""
    
    def test_get_secret_from_env(self):
        """Test getting secret from environment."""
        with patch.dict(os.environ, {'TEST_SECRET': 'env_value'}):
            config = Config()
            assert config.get_secret('TEST_SECRET') == 'env_value'
    
    def test_get_secret_with_default(self):
        """Test getting secret with default value."""
        with patch.dict(os.environ, {}, clear=True):
            config = Config()
            assert config.get_secret('NONEXISTENT', default='default_value') == 'default_value'
    
    def test_get_secret_required_not_found(self):
        """Test getting required secret that doesn't exist."""
        with patch.dict(os.environ, {}, clear=True):
            config = Config()
            with pytest.raises(ConfigurationError):
                config.get_secret('NONEXISTENT', required=True)
    
    def test_get_secret_multiple_providers(self, tmp_path):
        """Test secret resolution from multiple providers."""
        # Create file-based secret
        secret_file = tmp_path / "FILE_SECRET"
        secret_file.write_text("file_value")
        
        with patch.dict(os.environ, {'ENV_SECRET': 'env_value'}):
            config = Config()
            # Add file provider manually (after environment provider)
            config.secret_providers.append(FileSecretProvider(secrets_dir=str(tmp_path)))
            
            # Should get from environment (higher priority)
            assert config.get_secret('ENV_SECRET') == 'env_value'
            # Should get from file
            assert config.get_secret('FILE_SECRET') == 'file_value'


class TestConfigValidateApiKey:
    """Tests for Config.validate_api_key method."""
    
    def test_validate_api_key_valid(self):
        """Test validation of valid API key."""
        config = Config()
        assert config.validate_api_key('GOOGLE_AI_API_KEY', 'AIzaSyBcdefghijklmnopqrstuvwxyz1234567890') is True
    
    def test_validate_api_key_placeholder(self):
        """Test validation rejects placeholder values."""
        config = Config()
        assert config.validate_api_key('GOOGLE_AI_API_KEY', 'your_api_key_here') is False
    
    def test_validate_api_key_too_short(self):
        """Test validation rejects short keys."""
        config = Config()
        assert config.validate_api_key('GOOGLE_AI_API_KEY', 'short') is False
    
    def test_validate_api_key_none(self):
        """Test validation of None value."""
        config = Config()
        assert config.validate_api_key('GOOGLE_AI_API_KEY', None) is False
    
    def test_validate_api_key_invalid_format(self):
        """Test validation of invalid format."""
        config = Config()
        # Spaces not allowed in Google API keys
        assert config.validate_api_key('GOOGLE_AI_API_KEY', 'invalid key with spaces') is False


class TestConfigCheckSecurity:
    """Tests for Config.check_security method."""
    
    def test_check_security_dev_no_warnings(self):
        """Test no warnings in development."""
        with patch.dict(os.environ, {}, clear=True):
            config = Config()
            warnings = config.check_security()
            # Should have no critical warnings in dev
            assert not any(w.startswith('CRITICAL') for w in warnings)
    
    def test_check_security_prod_default_secret_key(self):
        """Test warning for default SECRET_KEY in production."""
        with patch.dict(os.environ, {
            'ENVIRONMENT': 'production',
            'SECRET_KEY': 'dev-secret-key-change-in-production'
        }):
            config = Config()
            warnings = config.check_security()
            assert any('CRITICAL' in w and 'SECRET_KEY' in w for w in warnings)
    
    def test_check_security_prod_short_secret_key(self):
        """Test warning for short SECRET_KEY in production."""
        with patch.dict(os.environ, {
            'ENVIRONMENT': 'production',
            'SECRET_KEY': 'short'
        }):
            config = Config()
            warnings = config.check_security()
            assert any('WARNING' in w and 'too short' in w for w in warnings)
    
    def test_check_security_prod_invalid_api_key(self):
        """Test warning for invalid API key in production."""
        with patch.dict(os.environ, {
            'ENVIRONMENT': 'production',
            'GOOGLE_AI_API_KEY': 'test_key'
        }):
            config = Config()
            warnings = config.check_security()
            assert any('WARNING' in w and 'GOOGLE_AI_API_KEY' in w for w in warnings)


class TestConfigValidate:
    """Tests for Config.validate method."""
    
    def test_validate_success_dev(self):
        """Test validation succeeds in development."""
        with patch.dict(os.environ, {}, clear=True):
            config = Config()
            # Should not raise
            config.validate()
    
    def test_validate_fails_prod_default_key(self):
        """Test validation fails in production with default key."""
        with patch.dict(os.environ, {
            'ENVIRONMENT': 'production',
            'SECRET_KEY': 'dev-secret-key-change-in-production'
        }):
            config = Config()
            with pytest.raises(ConfigurationError):
                config.validate()
    
    def test_validate_success_prod_good_key(self):
        """Test validation succeeds in production with good key."""
        with patch.dict(os.environ, {
            'ENVIRONMENT': 'production',
            'SECRET_KEY': 'a' * 32  # 32 character key
        }):
            config = Config()
            # Should not raise
            config.validate()


class TestConfigGetGoogleAiApiKey:
    """Tests for Config.get_google_ai_api_key method."""
    
    def test_get_google_ai_api_key_valid(self):
        """Test getting valid Google AI API key."""
        with patch.dict(os.environ, {
            'GOOGLE_AI_API_KEY': 'AIzaSyBcdefghijklmnopqrstuvwxyz1234567890'
        }):
            config = Config()
            assert config.get_google_ai_api_key() == 'AIzaSyBcdefghijklmnopqrstuvwxyz1234567890'
    
    def test_get_google_ai_api_key_placeholder(self):
        """Test getting placeholder API key returns None."""
        with patch.dict(os.environ, {'GOOGLE_AI_API_KEY': 'your_api_key_here'}):
            config = Config()
            assert config.get_google_ai_api_key() is None
    
    def test_get_google_ai_api_key_invalid_format_dev(self):
        """Test getting invalid format API key in development."""
        with patch.dict(os.environ, {'GOOGLE_AI_API_KEY': 'invalid'}):
            config = Config()
            # In dev, returns None with warning
            assert config.get_google_ai_api_key() is None
    
    def test_get_google_ai_api_key_invalid_format_prod(self):
        """Test getting invalid format API key in production."""
        with patch.dict(os.environ, {
            'ENVIRONMENT': 'production',
            'GOOGLE_AI_API_KEY': 'invalid'
        }):
            config = Config()
            # In prod, raises error
            with pytest.raises(ConfigurationError):
                config.get_google_ai_api_key()


class TestConfigGetSecretKey:
    """Tests for Config.get_secret_key method."""
    
    def test_get_secret_key_from_env(self):
        """Test getting SECRET_KEY from environment."""
        with patch.dict(os.environ, {'SECRET_KEY': 'my_secret_key'}):
            config = Config()
            assert config.get_secret_key() == 'my_secret_key'
    
    def test_get_secret_key_default(self):
        """Test getting default SECRET_KEY."""
        with patch.dict(os.environ, {}, clear=True):
            config = Config()
            assert config.get_secret_key() == 'dev-secret-key-change-in-production'


class TestConfigSupportsKeyRotation:
    """Tests for Config.supports_key_rotation method."""
    
    def test_supports_key_rotation_env_only(self):
        """Test key rotation support with only environment provider."""
        with patch.dict(os.environ, {}, clear=True):
            config = Config()
            # Only environment provider, no rotation support
            assert config.supports_key_rotation() is False
    
    def test_supports_key_rotation_with_file_provider(self, tmp_path):
        """Test key rotation support with file provider."""
        with patch('config.Path') as mock_path:
            mock_path.return_value.exists.return_value = True
            
            config = Config()
            config.secret_providers.append(FileSecretProvider(secrets_dir=str(tmp_path)))
            # Has file provider, supports rotation
            assert config.supports_key_rotation() is True


class TestGlobalConfig:
    """Tests for global config functions."""
    
    def test_get_config_singleton(self):
        """Test that get_config returns singleton."""
        reset_config()
        config1 = get_config()
        config2 = get_config()
        assert config1 is config2
    
    def test_reset_config(self):
        """Test that reset_config clears singleton."""
        config1 = get_config()
        reset_config()
        config2 = get_config()
        assert config1 is not config2


class TestConfigEdgeCases:
    """Tests for edge cases in Config."""
    
    def test_empty_secret_value(self):
        """Test handling of empty secret value."""
        with patch.dict(os.environ, {'EMPTY_SECRET': ''}):
            config = Config()
            # Empty string is falsy, should not be returned
            assert config.get_secret('EMPTY_SECRET', default='default') == 'default'
    
    def test_provider_exception_handling(self):
        """Test handling of provider exceptions."""
        config = Config()
        
        # Add a provider that raises an exception
        class BadProvider:
            def get_secret(self, key):
                raise Exception("Provider error")
        
        config.secret_providers.insert(0, BadProvider())
        
        # Should fall back to next provider
        with patch.dict(os.environ, {'TEST_KEY': 'fallback_value'}):
            assert config.get_secret('TEST_KEY') == 'fallback_value'
    
    def test_api_key_with_special_characters(self):
        """Test API key validation with special characters."""
        config = Config()
        # Underscores and hyphens are allowed
        assert config.validate_api_key('GOOGLE_AI_API_KEY', 'AIzaSy_test-key_123456789') is True
    
    def test_secret_key_validation_boundary(self):
        """Test SECRET_KEY validation at length boundary."""
        with patch.dict(os.environ, {'ENVIRONMENT': 'production', 'SECRET_KEY': 'a' * 31}):
            config = Config()
            warnings = config.check_security()
            # 31 chars should trigger warning
            assert any('too short' in w for w in warnings)
        
        with patch.dict(os.environ, {'ENVIRONMENT': 'production', 'SECRET_KEY': 'a' * 32}):
            config = Config()
            warnings = config.check_security()
            # 32 chars should be okay
            assert not any('too short' in w for w in warnings)
