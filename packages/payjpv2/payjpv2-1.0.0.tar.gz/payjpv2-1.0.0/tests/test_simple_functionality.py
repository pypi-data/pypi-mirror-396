"""
Simple functionality tests for PAY.JP Python SDK.

These tests focus on testing components that don't require complex mocking.
"""
import os
from unittest.mock import patch

import payjpv2
import pytest
from payjpv2.models.customer_create_request import CustomerCreateRequest
from payjpv2.models.payment_flow_create_request import PaymentFlowCreateRequest


class TestSDKImports:
    """Test SDK imports and basic functionality."""

    def test_main_imports(self):
        """Test that main SDK components can be imported."""
        assert hasattr(payjpv2, 'Configuration')
        assert hasattr(payjpv2, 'ApiClient')
        assert hasattr(payjpv2, 'CustomersApi')
        assert hasattr(payjpv2, 'PaymentFlowsApi')

    def test_model_imports(self):
        """Test that model classes can be imported."""
        from payjpv2.models import customer_create_request, payment_flow_create_request

        assert hasattr(customer_create_request, 'CustomerCreateRequest')
        assert hasattr(payment_flow_create_request, 'PaymentFlowCreateRequest')

    def test_api_imports(self):
        """Test that API classes can be imported."""
        from payjpv2.api import customers_api, payment_flows_api

        assert hasattr(customers_api, 'CustomersApi')
        assert hasattr(payment_flows_api, 'PaymentFlowsApi')


class TestConfiguration:
    """Test configuration functionality."""

    def test_configuration_creation(self):
        """Test configuration creation."""
        config = payjpv2.Configuration()
        assert config is not None
        assert hasattr(config, 'host')
        assert hasattr(config, 'api_key')

    def test_configuration_with_parameters(self):
        """Test configuration with parameters."""
        config = payjpv2.Configuration(
            host="https://api.pay.jp",
            api_key={'APIKeyHeader': 'test_key'},
            api_key_prefix={'APIKeyHeader': 'Bearer'}
        )

        assert config.host == "https://api.pay.jp"
        assert config.api_key['APIKeyHeader'] == 'test_key'
        assert config.api_key_prefix['APIKeyHeader'] == 'Bearer'

    def test_configuration_from_environment(self):
        """Test configuration using environment variables."""
        with patch.dict(os.environ, {'PAYJP_API_KEY': 'env_test_key'}):
            api_key = os.environ.get('PAYJP_API_KEY')
            config = payjpv2.Configuration(
                api_key={'APIKeyHeader': api_key}
            )
            assert config.api_key['APIKeyHeader'] == 'env_test_key'


class TestApiClient:
    """Test API client functionality."""

    def test_api_client_creation(self):
        """Test API client creation."""
        config = payjpv2.Configuration()
        client = payjpv2.ApiClient(config)
        assert client is not None
        assert client.configuration == config

    def test_api_client_context_manager(self):
        """Test API client as context manager."""
        config = payjpv2.Configuration()
        with payjpv2.ApiClient(config) as client:
            assert client is not None
            assert client.configuration == config

    def test_api_client_with_custom_host(self):
        """Test API client with custom host."""
        config = payjpv2.Configuration(host="https://custom.api.com")
        with payjpv2.ApiClient(config) as client:
            assert client.configuration.host == "https://custom.api.com"


class TestModelCreation:
    """Test model creation and validation."""

    def test_customer_create_request_basic(self):
        """Test basic customer creation request."""
        request = CustomerCreateRequest()
        assert request is not None

    def test_customer_create_request_with_email(self):
        """Test customer creation request with email."""
        request = CustomerCreateRequest(email="test@example.com")
        assert request.email == "test@example.com"

    def test_customer_create_request_with_description(self):
        """Test customer creation request with description."""
        request = CustomerCreateRequest(
            email="test@example.com",
            description="Test customer"
        )
        assert request.email == "test@example.com"
        assert request.description == "Test customer"

    def test_payment_flow_create_request_basic(self):
        """Test basic payment flow creation request."""
        request = PaymentFlowCreateRequest(amount=1000, currency="jpy")
        assert request.amount == 1000

    def test_payment_flow_create_request_with_customer(self):
        """Test payment flow creation request with customer."""
        request = PaymentFlowCreateRequest(
            amount=1000,
            currency="jpy",
            customer_id="cus_test123"
        )
        assert request.amount == 1000
        assert request.customer_id == "cus_test123"

    def test_payment_flow_create_request_with_options(self):
        """Test payment flow creation request with various options."""
        request = PaymentFlowCreateRequest(
            amount=1500,
            currency="jpy",
            customer_id="cus_test123",
            description="Test payment for SDK",
            confirm=True
        )
        assert request.amount == 1500
        assert request.customer_id == "cus_test123"
        assert request.description == "Test payment for SDK"
        assert request.confirm is True


class TestModelSerialization:
    """Test model serialization functionality."""

    def test_customer_request_to_string(self):
        """Test customer request string representation."""
        request = CustomerCreateRequest(email="test@example.com")
        str_repr = request.to_str()
        assert isinstance(str_repr, str)
        assert "test@example.com" in str_repr

    def test_customer_request_to_json(self):
        """Test customer request JSON serialization."""
        request = CustomerCreateRequest(email="test@example.com")
        json_str = request.to_json()
        assert isinstance(json_str, str)
        assert "test@example.com" in json_str

    def test_payment_flow_request_to_string(self):
        """Test payment flow request string representation."""
        request = PaymentFlowCreateRequest(amount=1000, currency="jpy")
        str_repr = request.to_str()
        assert isinstance(str_repr, str)
        assert "1000" in str_repr

    def test_payment_flow_request_to_json(self):
        """Test payment flow request JSON serialization."""
        request = PaymentFlowCreateRequest(amount=1000, currency="jpy")
        json_str = request.to_json()
        assert isinstance(json_str, str)
        assert "1000" in json_str

    def test_model_dump_functionality(self):
        """Test model dump functionality."""
        request = CustomerCreateRequest(email="test@example.com")
        if hasattr(request, 'model_dump'):
            data = request.model_dump()
            assert isinstance(data, dict)
            assert data.get('email') == "test@example.com"


class TestAPIInstantiation:
    """Test API class instantiation."""

    def test_customers_api_creation(self):
        """Test customers API instantiation."""
        config = payjpv2.Configuration()
        with payjpv2.ApiClient(config) as client:
            customers_api = payjpv2.CustomersApi(client)
            assert customers_api is not None
            assert customers_api.api_client == client

    def test_payment_flows_api_creation(self):
        """Test payment flows API instantiation."""
        config = payjpv2.Configuration()
        with payjpv2.ApiClient(config) as client:
            payment_flows_api = payjpv2.PaymentFlowsApi(client)
            assert payment_flows_api is not None
            assert payment_flows_api.api_client == client

    def test_multiple_api_instances(self):
        """Test creating multiple API instances."""
        config = payjpv2.Configuration()
        with payjpv2.ApiClient(config) as client:
            customers_api = payjpv2.CustomersApi(client)
            payment_flows_api = payjpv2.PaymentFlowsApi(client)
            payment_methods_api = payjpv2.PaymentMethodsApi(client)

            # All should use the same client
            assert customers_api.api_client == client
            assert payment_flows_api.api_client == client
            assert payment_methods_api.api_client == client


class TestErrorClasses:
    """Test error and exception classes."""

    def test_api_exception_import(self):
        """Test that ApiException can be imported."""
        from payjpv2.rest import ApiException
        assert ApiException is not None

    def test_api_exception_creation(self):
        """Test ApiException creation."""
        from payjpv2.rest import ApiException

        exc = ApiException(status=400, reason="Bad Request")
        assert exc.status == 400
        assert exc.reason == "Bad Request"

    def test_api_exception_with_body(self):
        """Test ApiException with body."""
        from payjpv2.rest import ApiException

        exc = ApiException(
            status=400,
            reason="Bad Request",
            body='{"error": {"message": "Invalid request"}}'
        )
        assert exc.status == 400
        assert exc.reason == "Bad Request"
        assert exc.body == '{"error": {"message": "Invalid request"}}'


class TestPackageStructure:
    """Test package structure and organization."""

    def test_package_version(self):
        """Test package version availability."""
        # Test if version is available
        if hasattr(payjpv2, '__version__'):
            assert isinstance(payjpv2.__version__, str)

    def test_package_documentation(self):
        """Test package documentation."""
        # Test if main classes have docstrings
        assert payjpv2.Configuration.__doc__ is not None
        assert payjpv2.ApiClient.__doc__ is not None

    def test_model_properties(self):
        """Test model properties and attributes."""
        request = CustomerCreateRequest()

        # Test that model has expected properties
        assert hasattr(request, 'email')
        assert hasattr(request, 'description')
        assert hasattr(request, 'to_str')
        assert hasattr(request, 'to_json')