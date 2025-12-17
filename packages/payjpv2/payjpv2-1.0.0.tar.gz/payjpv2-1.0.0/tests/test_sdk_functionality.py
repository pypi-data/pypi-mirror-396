"""
Functional tests for PAY.JP Python SDK.

These tests verify the SDK functionality using the actual generated models
and API structure without making real API calls.
"""
from unittest.mock import Mock, patch

import payjpv2
import pytest
from payjpv2.api.customers_api import CustomersApi
from payjpv2.api.payment_flows_api import PaymentFlowsApi
from payjpv2.models.customer_create_request import CustomerCreateRequest
from payjpv2.models.payment_flow_create_request import PaymentFlowCreateRequest


class TestSDKBasicFunctionality:
    """Test basic SDK functionality."""

    def test_sdk_import(self):
        """Test that all main SDK components can be imported."""
        # Test that main modules are importable
        assert hasattr(payjpv2, 'Configuration')
        assert hasattr(payjpv2, 'ApiClient')
        assert hasattr(payjpv2, 'CustomersApi')
        assert hasattr(payjpv2, 'PaymentFlowsApi')

    def test_configuration_creation(self, api_key):
        """Test configuration creation with various parameters."""
        config = payjpv2.Configuration(
            host="https://api.pay.jp",
            api_key={'APIKeyHeader': api_key},
            api_key_prefix={'APIKeyHeader': 'Bearer'}
        )

        assert config.host == "https://api.pay.jp"
        assert config.api_key['APIKeyHeader'] == api_key
        assert config.api_key_prefix['APIKeyHeader'] == 'Bearer'

    def test_api_client_creation(self, configuration):
        """Test API client creation."""
        with payjpv2.ApiClient(configuration) as client:
            assert client.configuration == configuration

            # Test that API instances can be created
            customers_api = CustomersApi(client)
            payment_flows_api = PaymentFlowsApi(client)

            assert customers_api.api_client == client
            assert payment_flows_api.api_client == client


class TestCustomerOperations:
    """Test customer operations."""

    def test_customer_create_request_basic(self):
        """Test basic customer creation request."""
        request = CustomerCreateRequest(email="test@example.com")
        assert request.email == "test@example.com"

    def test_customer_create_request_with_description(self):
        """Test customer creation with description."""
        request = CustomerCreateRequest(
            email="test@example.com",
            description="Test customer for SDK testing"
        )
        assert request.email == "test@example.com"
        assert request.description == "Test customer for SDK testing"

    def test_customer_create_request_minimal_valid(self):
        """Test that minimal customer request is valid."""
        request = CustomerCreateRequest()
        # Should be able to create request without required fields
        # (validation happens server-side)
        assert request is not None

    def test_customer_api_instantiation(self, api_client):
        """Test customer API instantiation."""
        customers_api = CustomersApi(api_client)
        assert customers_api.api_client == api_client

        # Test that API methods exist
        assert hasattr(customers_api, 'create_customer')
        assert hasattr(customers_api, 'get_customer')
        assert hasattr(customers_api, 'get_all_customers')


class TestPaymentFlowOperations:
    """Test payment flow operations."""

    def test_payment_flow_create_request_basic(self):
        """Test basic payment flow creation request."""
        request = PaymentFlowCreateRequest(amount=1000, currency="jpy")
        assert request.amount == 1000

    def test_payment_flow_create_request_with_customer(self):
        """Test payment flow creation with customer."""
        request = PaymentFlowCreateRequest(
            amount=1000,
            currency="jpy",
            customer_id="cus_test123"
        )
        assert request.amount == 1000
        assert request.customer_id == "cus_test123"

    def test_payment_flow_create_request_with_description(self):
        """Test payment flow creation with description."""
        request = PaymentFlowCreateRequest(
            amount=1500,
            currency="jpy",
            description="Test payment for SDK"
        )
        assert request.amount == 1500
        assert request.description == "Test payment for SDK"

    def test_payment_flow_api_instantiation(self, api_client):
        """Test payment flow API instantiation."""
        payment_flows_api = PaymentFlowsApi(api_client)
        assert payment_flows_api.api_client == api_client

        # Test that API methods exist
        assert hasattr(payment_flows_api, 'create_payment_flow')
        assert hasattr(payment_flows_api, 'get_payment_flow')
        assert hasattr(payment_flows_api, 'get_all_payment_flows')


class TestModelSerialization:
    """Test model serialization capabilities."""

    def test_customer_request_serialization(self):
        """Test customer request serialization."""
        request = CustomerCreateRequest(
            email="test@example.com",
            description="Test customer"
        )

        # Test string representation
        str_repr = request.to_str()
        assert "test@example.com" in str_repr
        assert "Test customer" in str_repr

        # Test JSON serialization
        json_str = request.to_json()
        assert '"email": "test@example.com"' in json_str

    def test_payment_flow_request_serialization(self):
        """Test payment flow request serialization."""
        request = PaymentFlowCreateRequest(
            amount=1000,
            currency="jpy",
            description="Test payment"
        )

        str_repr = request.to_str()
        assert "1000" in str_repr
        assert "Test payment" in str_repr

        json_str = request.to_json()
        assert '"amount": 1000' in json_str

    def test_model_dict_conversion(self):
        """Test model to dict conversion."""
        request = CustomerCreateRequest(email="test@example.com")

        # Test dict conversion using model_dump
        if hasattr(request, 'model_dump'):
            data = request.model_dump()
            assert data["email"] == "test@example.com"


class TestErrorHandlingFunctionality:
    """Test error handling functionality."""

    def test_api_exception_creation(self):
        """Test API exception creation and properties."""
        from payjpv2.rest import ApiException

        exc = ApiException(
            status=400,
            reason="Bad Request",
            body='{"error": {"message": "Invalid email"}}'
        )

        assert exc.status == 400
        assert exc.reason == "Bad Request"
        assert "Invalid email" in exc.body

    def test_model_validation_flexibility(self):
        """Test that models are flexible with validation."""
        # These should not raise exceptions at model level
        request1 = CustomerCreateRequest(email="")
        assert request1.email == ""

        request2 = PaymentFlowCreateRequest(amount=50, currency="jpy")
        assert request2.amount == 50

        # Test with max valid value (PaymentFlowCreateRequest requires <= 9999999)
        request3 = PaymentFlowCreateRequest(amount=9999999, currency="jpy")
        assert request3.amount == 9999999


class TestAPIClientConfiguration:
    """Test API client configuration and headers."""

    def test_api_client_headers_configuration(self, api_client):
        """Test that API client has proper configuration."""
        # Verify client has configuration
        assert api_client.configuration is not None
        assert hasattr(api_client.configuration, 'api_key')
        assert hasattr(api_client.configuration, 'host')

    def test_multiple_api_instances(self, api_client):
        """Test that multiple API instances can be created."""
        customers_api = CustomersApi(api_client)
        payment_flows_api = PaymentFlowsApi(api_client)

        # Both should share the same client
        assert customers_api.api_client == payment_flows_api.api_client
        assert customers_api.api_client == api_client

    def test_api_client_context_manager_behavior(self, configuration):
        """Test API client context manager behavior."""
        # Test that context manager works properly
        with payjpv2.ApiClient(configuration) as client:
            assert client is not None
            customers_api = CustomersApi(client)
            assert customers_api.api_client == client


class TestWorkflowIntegration:
    """Test workflow integration without actual API calls."""

    def test_customer_workflow_simulation(self, api_client):
        """Test customer workflow simulation."""
        customers_api = CustomersApi(api_client)

        # Test creating request objects for workflow
        create_request = CustomerCreateRequest(
            email="workflow@example.com",
            description="Workflow test customer"
        )

        assert create_request.email == "workflow@example.com"
        assert create_request.description == "Workflow test customer"

        # Verify API object can handle the request structure
        assert hasattr(customers_api, 'create_customer')

    def test_payment_flow_workflow_simulation(self, api_client):
        """Test payment flow workflow simulation."""
        payment_flows_api = PaymentFlowsApi(api_client)

        # Test creating request objects for workflow
        create_request = PaymentFlowCreateRequest(
            amount=2500,
            currency="jpy",
            customer_id="cus_workflow_test",
            description="Workflow test payment"
        )

        assert create_request.amount == 2500
        assert create_request.customer_id == "cus_workflow_test"
        assert create_request.description == "Workflow test payment"

        # Verify API object can handle the request structure
        assert hasattr(payment_flows_api, 'create_payment_flow')
        assert hasattr(payment_flows_api, 'get_payment_flow')

    def test_multi_api_coordination(self, api_client):
        """Test coordination between multiple APIs."""
        customers_api = CustomersApi(api_client)
        payment_flows_api = PaymentFlowsApi(api_client)

        # Test that both APIs can work with the same client
        assert customers_api.api_client == payment_flows_api.api_client

        # Test creating related objects
        customer_request = CustomerCreateRequest(email="coordination@example.com")
        payment_request = PaymentFlowCreateRequest(
            amount=1500,
            currency="jpy",
            customer_id="cus_coordination_test"
        )

        assert customer_request.email == "coordination@example.com"
        assert payment_request.customer_id == "cus_coordination_test"


class TestSDKStructure:
    """Test SDK structure and organization."""

    def test_api_module_structure(self):
        """Test API module structure."""
        # Test that API classes are properly organized
        from payjpv2.api import customers_api, payment_flows_api

        assert hasattr(customers_api, 'CustomersApi')
        assert hasattr(payment_flows_api, 'PaymentFlowsApi')

    def test_model_module_structure(self):
        """Test model module structure."""
        # Test that model classes are properly organized
        from payjpv2.models import customer_create_request, payment_flow_create_request

        assert hasattr(customer_create_request, 'CustomerCreateRequest')
        assert hasattr(payment_flow_create_request, 'PaymentFlowCreateRequest')

    def test_configuration_accessibility(self):
        """Test configuration accessibility."""
        # Test that configuration is accessible from main module
        assert hasattr(payjpv2, 'Configuration')

        # Test configuration creation
        config = payjpv2.Configuration()
        assert config is not None

    def test_exception_accessibility(self):
        """Test exception accessibility."""
        # Test that exceptions are accessible
        from payjpv2 import exceptions
        from payjpv2.rest import ApiException

        assert ApiException is not None
        assert exceptions is not None