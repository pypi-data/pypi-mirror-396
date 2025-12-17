"""
Integration tests for PAY.JP Python SDK.

These tests verify the integration between different components of the SDK
without making actual API calls.
"""
import json
from unittest.mock import MagicMock, Mock, patch

import payjpv2
import pytest
from payjpv2.api.customers_api import CustomersApi
from payjpv2.api.payment_flows_api import PaymentFlowsApi
from payjpv2.api.payment_methods_api import PaymentMethodsApi
from payjpv2.models.customer_create_request import CustomerCreateRequest
from payjpv2.rest import ApiException

# from payjpv2.models.payment_flow_create_request import PaymentFlowCreateRequest
# from payjpv2.models.payment_method_create_request import PaymentMethodCreateRequest


class TestSDKIntegration:
    """Test SDK integration scenarios."""

    def test_client_initialization_with_api_key(self, api_key):
        """Test that the client can be initialized with an API key."""
        config = payjpv2.Configuration(
            host="https://api.pay.jp",
            api_key={'APIKeyHeader': api_key},
            api_key_prefix={'APIKeyHeader': 'Bearer'}
        )

        with payjpv2.ApiClient(config) as client:
            assert client.configuration.api_key['APIKeyHeader'] == api_key
            assert client.configuration.host == "https://api.pay.jp"
            assert client.configuration.api_key_prefix['APIKeyHeader'] == 'Bearer'

    def test_customer_workflow(self, api_client, sample_customer_data):
        """Test customer creation workflow."""
        customers_api = CustomersApi(api_client)

        # Mock the API call
        with patch.object(customers_api, 'create_customer') as mock_create:
            mock_response = Mock()
            mock_response.data = sample_customer_data
            mock_create.return_value = mock_response

            # Create customer request
            request = CustomerCreateRequest(email="test@example.com")
            response = customers_api.create_customer(request)

            # Verify the call was made correctly
            mock_create.assert_called_once_with(request)
            assert response.data['email'] == "test@example.com"

    def test_payment_flow_workflow(self, api_client, sample_payment_flow_data):
        """Test payment flow creation and confirmation workflow."""
        payment_flows_api = PaymentFlowsApi(api_client)

        with patch.object(payment_flows_api, 'get_payment_flow') as mock_retrieve:
            # Mock payment flow retrieval
            mock_response = Mock()
            mock_response.data = sample_payment_flow_data
            mock_retrieve.return_value = mock_response

            # Retrieve payment flow
            retrieved_pf = payment_flows_api.get_payment_flow("pfw_test123")

            # Verify workflow
            assert retrieved_pf.data['amount'] == 1000
            assert retrieved_pf.data['id'] == 'pfw_test123'

    def test_error_handling_integration(self, api_client):
        """Test error handling across API calls."""
        customers_api = CustomersApi(api_client)

        # Mock API exception
        with patch.object(customers_api, 'create_customer') as mock_create:
            mock_create.side_effect = ApiException(
                status=400,
                reason="Bad Request",
                body='{"error": {"message": "Invalid email format"}}'
            )

            request = CustomerCreateRequest(email="invalid-email")

            with pytest.raises(ApiException) as exc_info:
                customers_api.create_customer(request)

            assert exc_info.value.status == 400
            assert "Bad Request" in str(exc_info.value)

    def test_multiple_api_clients(self, api_key):
        """Test that multiple API clients can work independently."""
        config1 = payjpv2.Configuration(
            host="https://api.pay.jp",
            api_key={'APIKeyHeader': api_key + "_1"},
            api_key_prefix={'APIKeyHeader': 'Bearer'}
        )

        config2 = payjpv2.Configuration(
            host="https://api.pay.jp",
            api_key={'APIKeyHeader': api_key + "_2"},
            api_key_prefix={'APIKeyHeader': 'Bearer'}
        )

        with payjpv2.ApiClient(config1) as client1, \
             payjpv2.ApiClient(config2) as client2:

            customers_api1 = CustomersApi(client1)
            customers_api2 = CustomersApi(client2)

            # Verify they have different configurations
            assert client1.configuration.api_key['APIKeyHeader'] != client2.configuration.api_key['APIKeyHeader']
            assert customers_api1.api_client != customers_api2.api_client

    def test_api_client_context_manager(self, configuration):
        """Test API client context manager behavior."""
        with payjpv2.ApiClient(configuration) as client:
            assert client is not None
            assert client.configuration == configuration

            # Test that we can create API instances
            customers_api = CustomersApi(client)
            assert customers_api.api_client == client

    def test_http_request_configuration(self, api_client):
        """Test HTTP request configuration."""
        customers_api = CustomersApi(api_client)

        request = CustomerCreateRequest(email="test@example.com")

        with patch.object(customers_api.api_client, 'call_api') as mock_call_api:
            # Mock a simple response
            mock_response = Mock()
            mock_response.status = 200
            mock_response.data = b'{"id": "test"}'
            mock_response.headers = {}
            mock_call_api.return_value = mock_response

            with patch.object(customers_api.api_client, 'response_deserialize') as mock_deserialize:
                mock_deserialize.return_value = Mock(data={"id": "test"})
                customers_api.create_customer(request)

                # Verify call_api was called
                mock_call_api.assert_called_once()
                mock_deserialize.assert_called_once()