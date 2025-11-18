"""
Centralized configuration management with enhanced security.

This module provides secure configuration management including:
- API key validation and format checking
- Multiple secret providers (environment, files, cloud)
- Configuration validation on startup
- Key rotation support
- Security warnings for insecure configurations
"""
import os
import re
import logging
import warnings
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Set up logging
logger = logging.getLogger(__name__)


class ConfigurationError(Exception):
    """Raised when configuration is invalid or insecure."""
    pass


class SecretProvider:
    """Base class for secret providers."""
    
    def get_secret(self, key: str) -> Optional[str]:
        """
        Retrieve a secret by key.
        
        Args:
            key: Secret key name
            
        Returns:
            Secret value or None if not found
        """
        raise NotImplementedError


class EnvironmentSecretProvider(SecretProvider):
    """Retrieve secrets from environment variables."""
    
    def get_secret(self, key: str) -> Optional[str]:
        """Get secret from environment variable."""
        return os.getenv(key)


class FileSecretProvider(SecretProvider):
    """Retrieve secrets from files (Docker/Kubernetes secrets)."""
    
    def __init__(self, secrets_dir: str = "/run/secrets"):
        """
        Initialize file-based secret provider.
        
        Args:
            secrets_dir: Directory containing secret files
        """
        self.secrets_dir = Path(secrets_dir)
    
    def get_secret(self, key: str) -> Optional[str]:
        """Get secret from file."""
        secret_file = self.secrets_dir / key
        if secret_file.exists() and secret_file.is_file():
            try:
                return secret_file.read_text().strip()
            except Exception as e:
                logger.warning(f"Failed to read secret file {key}: {e}")
                return None
        return None


class CloudSecretProvider(SecretProvider):
    """Retrieve secrets from cloud secret managers (AWS/GCP)."""
    
    def __init__(self, provider_type: str = "aws"):
        """
        Initialize cloud secret provider.
        
        Args:
            provider_type: Cloud provider type ('aws' or 'gcp')
        """
        self.provider_type = provider_type
        self._client = None
    
    def _get_aws_secret(self, key: str) -> Optional[str]:
        """Get secret from AWS Secrets Manager."""
        try:
            import boto3
            from botocore.exceptions import ClientError
            
            if self._client is None:
                self._client = boto3.client('secretsmanager')
            
            response = self._client.get_secret_value(SecretId=key)
            return response.get('SecretString')
        except ImportError:
            logger.warning("boto3 not installed, cannot use AWS Secrets Manager")
            return None
        except ClientError as e:
            logger.warning(f"Failed to retrieve AWS secret {key}: {e}")
            return None
        except Exception as e:
            logger.warning(f"Unexpected error retrieving AWS secret {key}: {e}")
            return None
    
    def _get_gcp_secret(self, key: str) -> Optional[str]:
        """Get secret from GCP Secret Manager."""
        try:
            from google.cloud import secretmanager
            from google.api_core import exceptions
            
            if self._client is None:
                self._client = secretmanager.SecretManagerServiceClient()
            
            # Format: projects/{project}/secrets/{secret}/versions/latest
            project_id = os.getenv('GCP_PROJECT_ID')
            if not project_id:
                logger.warning("GCP_PROJECT_ID not set, cannot use GCP Secret Manager")
                return None
            
            name = f"projects/{project_id}/secrets/{key}/versions/latest"
            response = self._client.access_secret_version(request={"name": name})
            return response.payload.data.decode('UTF-8')
        except ImportError:
            logger.warning("google-cloud-secret-manager not installed, cannot use GCP Secret Manager")
            return None
        except exceptions.NotFound:
            logger.warning(f"GCP secret {key} not found")
            return None
        except Exception as e:
            logger.warning(f"Unexpected error retrieving GCP secret {key}: {e}")
            return None
    
    def get_secret(self, key: str) -> Optional[str]:
        """Get secret from cloud provider."""
        if self.provider_type == "aws":
            return self._get_aws_secret(key)
        elif self.provider_type == "gcp":
            return self._get_gcp_secret(key)
        else:
            logger.warning(f"Unknown cloud provider type: {self.provider_type}")
            return None


class Config:
    """
    Centralized configuration with security enhancements.
    
    Supports multiple secret providers and validates configuration.
    """
    
    # Insecure default values that should trigger warnings
    INSECURE_DEFAULTS = {
        'SECRET_KEY': ['dev-secret-key-change-in-production', 'dev-secret-key'],
        'GOOGLE_AI_API_KEY': ['your_api_key_here', 'test_key', 'test_api_key'],
    }
    
    # API key format patterns for validation
    API_KEY_PATTERNS = {
        'GOOGLE_AI_API_KEY': re.compile(r'^[A-Za-z0-9_-]{20,}$'),  # At least 20 alphanumeric chars
    }
    
    def __init__(self, env_file: Optional[str] = None):
        """
        Initialize configuration.
        
        Args:
            env_file: Path to .env file (optional)
        """
        # Load environment variables from .env file if specified
        if env_file:
            load_dotenv(env_file)
        else:
            load_dotenv()
        
        # Initialize secret providers
        self.secret_providers = []
        self._init_secret_providers()
        
        # Configuration cache
        self._config_cache: Dict[str, Any] = {}
        
        # Check if running in production
        self.is_production = self._detect_production()
    
    def _init_secret_providers(self):
        """Initialize secret providers in priority order."""
        # 1. Environment variables (highest priority)
        self.secret_providers.append(EnvironmentSecretProvider())
        
        # 2. File-based secrets (Docker/Kubernetes)
        secrets_dir = os.getenv('SECRETS_DIR', '/run/secrets')
        if Path(secrets_dir).exists():
            self.secret_providers.append(FileSecretProvider(secrets_dir))
        
        # 3. Cloud secret managers (if configured)
        cloud_provider = os.getenv('CLOUD_SECRET_PROVIDER')
        if cloud_provider in ['aws', 'gcp']:
            self.secret_providers.append(CloudSecretProvider(cloud_provider))
    
    def _detect_production(self) -> bool:
        """Detect if running in production environment."""
        env = os.getenv('ENVIRONMENT', '').lower()
        flask_env = os.getenv('FLASK_ENV', '').lower()
        
        # Check common production indicators
        return (
            env in ['production', 'prod'] or
            flask_env == 'production' or
            os.getenv('RENDER') is not None or  # Render.com
            os.getenv('HEROKU_APP_NAME') is not None or  # Heroku
            os.getenv('AWS_EXECUTION_ENV') is not None or  # AWS
            os.getenv('K_SERVICE') is not None  # Google Cloud Run
        )
    
    def get_secret(self, key: str, default: Optional[str] = None, required: bool = False) -> Optional[str]:
        """
        Get secret from configured providers.
        
        Args:
            key: Secret key name
            default: Default value if not found
            required: If True, raise error if not found
            
        Returns:
            Secret value or default
            
        Raises:
            ConfigurationError: If required and not found
        """
        # Try each provider in order
        for provider in self.secret_providers:
            try:
                value = provider.get_secret(key)
                if value:
                    return value
            except Exception as e:
                logger.warning(f"Error getting secret {key} from {provider.__class__.__name__}: {e}")
        
        # Use default if provided
        if default is not None:
            return default
        
        # Raise error if required
        if required:
            # Don't log the key name in production to avoid leaking info
            if self.is_production:
                raise ConfigurationError("Required configuration value not found")
            else:
                raise ConfigurationError(f"Required configuration value not found: {key}")
        
        return None
    
    def validate_api_key(self, key_name: str, key_value: Optional[str]) -> bool:
        """
        Validate API key format.
        
        Args:
            key_name: Name of the API key
            key_value: API key value
            
        Returns:
            True if valid, False otherwise
        """
        if not key_value:
            return False
        
        # Check for placeholder values
        if key_name in self.INSECURE_DEFAULTS:
            if key_value in self.INSECURE_DEFAULTS[key_name]:
                return False
        
        # Check format if pattern is defined
        if key_name in self.API_KEY_PATTERNS:
            pattern = self.API_KEY_PATTERNS[key_name]
            if not pattern.match(key_value):
                return False
        
        # Basic checks
        if len(key_value) < 10:
            return False
        
        return True
    
    def check_security(self) -> list:
        """
        Check for security issues in configuration.
        
        Returns:
            List of security warnings
        """
        warnings_list = []
        
        if self.is_production:
            # Check SECRET_KEY
            secret_key = self.get_secret('SECRET_KEY')
            if secret_key in self.INSECURE_DEFAULTS.get('SECRET_KEY', []):
                warnings_list.append(
                    "CRITICAL: Using default SECRET_KEY in production! "
                    "Set SECRET_KEY environment variable to a strong random value."
                )
            elif secret_key and len(secret_key) < 32:
                warnings_list.append(
                    "WARNING: SECRET_KEY is too short. Use at least 32 characters."
                )
            
            # Check GOOGLE_AI_API_KEY
            api_key = self.get_secret('GOOGLE_AI_API_KEY')
            if api_key and not self.validate_api_key('GOOGLE_AI_API_KEY', api_key):
                warnings_list.append(
                    "WARNING: GOOGLE_AI_API_KEY appears to be invalid or a placeholder. "
                    "Set a valid API key."
                )
            
            # Check for HTTPS enforcement
            if not os.getenv('FORCE_HTTPS', '').lower() == 'true':
                warnings_list.append(
                    "INFO: Consider setting FORCE_HTTPS=true for production."
                )
        
        return warnings_list
    
    def validate(self):
        """
        Validate configuration and emit warnings.
        
        Raises:
            ConfigurationError: If critical configuration is invalid
        """
        security_warnings = self.check_security()
        
        for warning in security_warnings:
            if warning.startswith('CRITICAL:'):
                logger.error(warning)
                if self.is_production:
                    raise ConfigurationError(warning)
            elif warning.startswith('WARNING:'):
                logger.warning(warning)
                warnings.warn(warning, UserWarning)
            else:
                logger.info(warning)
    
    def get_google_ai_api_key(self) -> Optional[str]:
        """
        Get Google AI API key with validation.
        
        Returns:
            API key or None if not found/invalid
            
        Raises:
            ConfigurationError: If key is required but not found or invalid
        """
        key = self.get_secret('GOOGLE_AI_API_KEY')
        
        # Check for placeholder values
        if key in self.INSECURE_DEFAULTS.get('GOOGLE_AI_API_KEY', []):
            return None
        
        # Validate format
        if key and not self.validate_api_key('GOOGLE_AI_API_KEY', key):
            if self.is_production:
                raise ConfigurationError("Invalid API key format")
            logger.warning("GOOGLE_AI_API_KEY format validation failed")
            return None
        
        return key
    
    def get_secret_key(self) -> str:
        """
        Get Flask secret key.
        
        Returns:
            Secret key
        """
        key = self.get_secret('SECRET_KEY', default='dev-secret-key-change-in-production')
        return key
    
    def supports_key_rotation(self) -> bool:
        """
        Check if key rotation is supported.
        
        Returns:
            True if using a provider that supports rotation
        """
        # File and cloud providers support rotation
        return any(
            isinstance(p, (FileSecretProvider, CloudSecretProvider))
            for p in self.secret_providers
        )


# Global config instance
_config_instance: Optional[Config] = None


def get_config() -> Config:
    """
    Get global configuration instance.
    
    Returns:
        Config instance
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance


def reset_config():
    """Reset global configuration instance (for testing)."""
    global _config_instance
    _config_instance = None
