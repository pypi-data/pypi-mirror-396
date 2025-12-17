"""
Tests for PAY.JP SDK configuration and client initialization.
"""
import os
import pytest
from unittest.mock import patch
import payjpv2
from payjpv2.configuration import Configuration
from payjpv2.api_client import ApiClient


class TestConfiguration:
    """Test SDK configuration."""

    def test_default_configuration(self):
        """Test default configuration values."""
        config = Configuration()
        
        # Test default values
        assert config.host is not None
        assert isinstance(config.api_key, dict)
        assert isinstance(config.api_key_prefix, dict)

    def test_configuration_with_api_key(self, api_key):
        """Test configuration with API key."""
        config = Configuration(
            host="https://api.pay.jp",
            api_key={'APIKeyHeader': api_key},
            api_key_prefix={'APIKeyHeader': 'Bearer'}
        )
        
        assert config.host == "https://api.pay.jp"
        assert config.api_key['APIKeyHeader'] == api_key
        assert config.api_key_prefix['APIKeyHeader'] == 'Bearer'

    def test_configuration_host_validation(self):
        """Test host validation."""
        # Valid hosts
        valid_hosts = [
            "https://api.pay.jp",
            "https://api.pay.jp/",
            "http://localhost:3000",
            "https://sandbox.api.pay.jp"
        ]
        
        for host in valid_hosts:
            config = Configuration(host=host)
            assert config.host is not None

    def test_api_key_configuration(self, api_key):
        """Test API key configuration options."""
        # Test with Bearer prefix
        config = Configuration(
            api_key={'APIKeyHeader': api_key},
            api_key_prefix={'APIKeyHeader': 'Bearer'}
        )
        assert config.api_key['APIKeyHeader'] == api_key
        assert config.api_key_prefix['APIKeyHeader'] == 'Bearer'
        
        # Test without prefix
        config_no_prefix = Configuration(
            api_key={'APIKeyHeader': api_key}
        )
        assert config_no_prefix.api_key['APIKeyHeader'] == api_key

    def test_configuration_from_environment(self):
        """Test configuration from environment variables."""
        with patch.dict(os.environ, {
            'PAYJP_API_KEY': 'sk_test_env_key',
            'PAYJP_HOST': 'https://api.pay.jp'
        }):
            # Test environment variable usage
            api_key = os.environ.get('PAYJP_API_KEY')
            host = os.environ.get('PAYJP_HOST')
            
            config = Configuration(
                host=host,
                api_key={'APIKeyHeader': api_key},
                api_key_prefix={'APIKeyHeader': 'Bearer'}
            )
            
            assert config.api_key['APIKeyHeader'] == 'sk_test_env_key'
            assert config.host == 'https://api.pay.jp'

    def test_configuration_validation(self):
        """Test configuration validation."""
        # Test empty API key
        config = Configuration(api_key={'APIKeyHeader': ''})
        assert config.api_key['APIKeyHeader'] == ''
        
        # Test None API key
        config = Configuration(api_key={'APIKeyHeader': None})
        assert config.api_key['APIKeyHeader'] is None

    def test_configuration_copy(self, configuration):
        """Test configuration copying."""
        # Create a copy
        config_copy = Configuration()
        config_copy.host = configuration.host
        config_copy.api_key = configuration.api_key.copy()
        config_copy.api_key_prefix = configuration.api_key_prefix.copy()
        
        # Verify copy is correct
        assert config_copy.host == configuration.host
        assert config_copy.api_key == configuration.api_key
        assert config_copy.api_key_prefix == configuration.api_key_prefix
        
        # Verify it's a deep copy
        config_copy.api_key['APIKeyHeader'] = 'different_key'
        assert config_copy.api_key['APIKeyHeader'] != configuration.api_key['APIKeyHeader']


class TestApiClient:
    """Test API client initialization and behavior."""

    def test_api_client_initialization(self, configuration):
        """Test API client initialization."""
        client = ApiClient(configuration)
        assert client.configuration == configuration
        assert client.configuration.host == configuration.host

    def test_api_client_context_manager(self, configuration):
        """Test API client as context manager."""
        with ApiClient(configuration) as client:
            assert client is not None
            assert client.configuration == configuration

    def test_api_client_with_custom_config(self, api_key):
        """Test API client with custom configuration."""
        custom_config = Configuration(
            host="https://custom.api.endpoint",
            api_key={'APIKeyHeader': api_key},
            api_key_prefix={'APIKeyHeader': 'Bearer'}
        )
        
        with ApiClient(custom_config) as client:
            assert client.configuration.host == "https://custom.api.endpoint"
            assert client.configuration.api_key['APIKeyHeader'] == api_key

    def test_multiple_clients_independence(self, api_key):
        """Test that multiple clients are independent."""
        config1 = Configuration(
            host="https://api1.pay.jp",
            api_key={'APIKeyHeader': api_key + "_1"}
        )
        config2 = Configuration(
            host="https://api2.pay.jp",
            api_key={'APIKeyHeader': api_key + "_2"}
        )
        
        client1 = ApiClient(config1)
        client2 = ApiClient(config2)
        
        assert client1.configuration.host != client2.configuration.host
        assert client1.configuration.api_key['APIKeyHeader'] != client2.configuration.api_key['APIKeyHeader']

    def test_api_client_default_headers(self, api_client):
        """Test API client default headers."""
        # Verify client has proper configuration
        assert api_client.configuration is not None
        
        # Test that User-Agent and other headers would be set
        # (This depends on the actual implementation)
        assert hasattr(api_client, 'configuration')

    def test_api_client_timeout_configuration(self):
        """Test API client timeout configuration."""
        config = Configuration()
        
        # Test default timeout (if applicable)
        with ApiClient(config) as client:
            assert client.configuration is not None
            # Add specific timeout tests based on actual implementation

    def test_configuration_thread_safety(self, configuration):
        """Test configuration thread safety."""
        import threading
        import time
        
        results = []
        
        def create_client():
            with ApiClient(configuration) as client:
                results.append(client.configuration.api_key['APIKeyHeader'])
                time.sleep(0.01)  # Small delay to test concurrency
        
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=create_client)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # All results should be the same
        assert len(set(results)) == 1
        assert results[0] == configuration.api_key['APIKeyHeader']