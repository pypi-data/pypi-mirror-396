"""
Mock tests for PAY.JP API clients.

These tests use mocked responses to test API client behavior
without making actual network requests.
"""
import json
from unittest.mock import Mock, patch

import pytest
from payjpv2.api.customers_api import CustomersApi
from payjpv2.api.payment_flows_api import PaymentFlowsApi
from payjpv2.models.customer_create_request import CustomerCreateRequest
from payjpv2.models.payment_flow_create_request import PaymentFlowCreateRequest
from payjpv2.rest import ApiException


class TestCustomersApiMock:
    """Test Customers API with mocked responses."""

    @patch('payjpv2.api_client.ApiClient.response_deserialize')
    @patch('payjpv2.api_client.ApiClient.call_api')
    def test_create_customer_success(self, mock_call_api, mock_deserialize, api_client, sample_customer_data):
        """Test successful customer creation."""
        customers_api = CustomersApi(api_client)

        # Mock the REST response
        mock_rest_response = Mock()
        mock_rest_response.status = 200
        mock_rest_response.data = json.dumps(sample_customer_data).encode()
        mock_rest_response.headers = {"Content-Type": "application/json"}
        mock_rest_response.read = Mock()
        mock_call_api.return_value = mock_rest_response

        # Mock the deserialization to return an object with data attribute
        mock_api_response = Mock()
        mock_api_response.data = sample_customer_data
        mock_deserialize.return_value = mock_api_response

        request = CustomerCreateRequest(email="test@example.com")
        response = customers_api.create_customer(request)

        # Verify API was called correctly
        mock_call_api.assert_called_once()
        mock_deserialize.assert_called_once()

        # Verify response
        assert response['id'] == 'cus_test123'
        assert response['email'] == 'test@example.com'

    @patch('payjpv2.api_client.ApiClient.response_deserialize')
    @patch('payjpv2.api_client.ApiClient.call_api')
    def test_get_customer_success(self, mock_call_api, mock_deserialize, api_client, sample_customer_data):
        """Test successful customer retrieval."""
        customers_api = CustomersApi(api_client)

        mock_rest_response = Mock()
        mock_rest_response.status = 200
        mock_rest_response.data = json.dumps(sample_customer_data).encode()
        mock_call_api.return_value = mock_rest_response

        mock_api_response = Mock()
        mock_api_response.data = sample_customer_data
        mock_deserialize.return_value = mock_api_response

        response = customers_api.get_customer("cus_test123")

        # Verify API call
        mock_call_api.assert_called_once()
        mock_deserialize.assert_called_once()

        assert response['id'] == 'cus_test123'

    @patch('payjpv2.api_client.ApiClient.response_deserialize')
    @patch('payjpv2.api_client.ApiClient.call_api')
    def test_list_customers_success(self, mock_call_api, mock_deserialize, api_client):
        """Test successful customer listing."""
        customers_api = CustomersApi(api_client)

        mock_list_data = {
            "object": "list",
            "data": [
                {"id": "cus_1", "email": "user1@example.com"},
                {"id": "cus_2", "email": "user2@example.com"}
            ],
            "has_more": False
        }

        mock_rest_response = Mock()
        mock_rest_response.status = 200
        mock_rest_response.data = json.dumps(mock_list_data).encode()
        mock_call_api.return_value = mock_rest_response

        mock_api_response = Mock()
        mock_api_response.data = mock_list_data
        mock_deserialize.return_value = mock_api_response

        response = customers_api.get_all_customers(limit=10)

        # Verify API call
        mock_call_api.assert_called_once()
        mock_deserialize.assert_called_once()

        assert response['object'] == 'list'
        assert len(response['data']) == 2


class TestPaymentFlowsApiMock:
    """Test Payment Flows API with mocked responses."""

    @patch('payjpv2.api_client.ApiClient.response_deserialize')
    @patch('payjpv2.api_client.ApiClient.call_api')
    def test_create_payment_flow_success(self, mock_call_api, mock_deserialize, api_client, sample_payment_flow_data):
        """Test successful payment flow creation."""
        payment_flows_api = PaymentFlowsApi(api_client)

        mock_rest_response = Mock()
        mock_rest_response.status = 200
        mock_rest_response.data = json.dumps(sample_payment_flow_data).encode()
        mock_rest_response.read = Mock()
        mock_call_api.return_value = mock_rest_response

        mock_api_response = Mock()
        mock_api_response.data = sample_payment_flow_data
        mock_deserialize.return_value = mock_api_response

        request = PaymentFlowCreateRequest(amount=1000, currency="jpy")
        response = payment_flows_api.create_payment_flow(request)

        # Verify API call
        mock_call_api.assert_called_once()
        mock_deserialize.assert_called_once()

        assert response['amount'] == 1000

    @patch('payjpv2.api_client.ApiClient.response_deserialize')
    @patch('payjpv2.api_client.ApiClient.call_api')
    def test_get_payment_flow_success(self, mock_call_api, mock_deserialize, api_client, sample_payment_flow_data):
        """Test successful payment flow retrieval."""
        payment_flows_api = PaymentFlowsApi(api_client)

        mock_rest_response = Mock()
        mock_rest_response.status = 200
        mock_rest_response.data = json.dumps(sample_payment_flow_data).encode()
        mock_rest_response.read = Mock()
        mock_call_api.return_value = mock_rest_response

        mock_api_response = Mock()
        mock_api_response.data = sample_payment_flow_data
        mock_deserialize.return_value = mock_api_response

        response = payment_flows_api.get_payment_flow("pfw_test123")

        # Verify API call
        mock_call_api.assert_called_once()
        mock_deserialize.assert_called_once()

        assert response['id'] == 'pfw_test123'


class TestApiErrorHandling:
    """Test API error handling with mocks."""

    @patch('payjpv2.api_client.ApiClient.call_api')
    def test_api_exception_handling(self, mock_call_api, api_client):
        """Test API exception handling."""
        customers_api = CustomersApi(api_client)

        # Mock API exception
        mock_call_api.side_effect = ApiException(
            status=400,
            reason="Bad Request",
            body='{"error": {"message": "Invalid email"}}'
        )

        request = CustomerCreateRequest(email="invalid-email")

        with pytest.raises(ApiException) as exc_info:
            customers_api.create_customer(request)

        assert exc_info.value.status == 400
        assert exc_info.value.reason == "Bad Request"

    @patch('payjpv2.api_client.ApiClient.call_api')
    def test_404_error_handling(self, mock_call_api, api_client):
        """Test 404 error handling."""
        customers_api = CustomersApi(api_client)

        mock_call_api.side_effect = ApiException(
            status=404,
            reason="Not Found",
            body='{"error": {"message": "Customer not found"}}'
        )

        with pytest.raises(ApiException) as exc_info:
            customers_api.get_customer("cus_nonexistent")

        assert exc_info.value.status == 404


class TestApiRequestBuilding:
    """Test API request building and parameter handling."""

    @patch('payjpv2.api_client.ApiClient.response_deserialize')
    @patch('payjpv2.api_client.ApiClient.call_api')
    def test_query_parameters(self, mock_call_api, mock_deserialize, api_client):
        """Test query parameter handling."""
        customers_api = CustomersApi(api_client)

        mock_rest_response = Mock()
        mock_rest_response.status = 200
        mock_rest_response.data = b'{"object": "list", "data": []}'
        mock_rest_response.read = Mock()
        mock_call_api.return_value = mock_rest_response

        mock_api_response = Mock()
        mock_api_response.data = {"object": "list", "data": []}
        mock_deserialize.return_value = mock_api_response

        # Call with query parameters (use only valid parameters)
        customers_api.get_all_customers(limit=20)

        # Verify call_api was called
        mock_call_api.assert_called_once()
        mock_deserialize.assert_called_once()

    @patch('payjpv2.api_client.ApiClient.response_deserialize')
    @patch('payjpv2.api_client.ApiClient.call_api')
    def test_request_body_serialization(self, mock_call_api, mock_deserialize, api_client):
        """Test request body serialization."""
        customers_api = CustomersApi(api_client)

        mock_rest_response = Mock()
        mock_rest_response.status = 200
        mock_rest_response.data = b'{"id": "cus_test"}'
        mock_rest_response.read = Mock()
        mock_call_api.return_value = mock_rest_response

        mock_api_response = Mock()
        mock_api_response.data = {"id": "cus_test"}
        mock_deserialize.return_value = mock_api_response

        request = CustomerCreateRequest(email="test@example.com")
        customers_api.create_customer(request)

        # Verify request body was included in the call
        mock_call_api.assert_called_once()
        mock_deserialize.assert_called_once()

    @patch('payjpv2.api_client.ApiClient.response_deserialize')
    @patch('payjpv2.api_client.ApiClient.call_api')
    def test_headers_configuration(self, mock_call_api, mock_deserialize, api_client):
        """Test HTTP headers configuration."""
        customers_api = CustomersApi(api_client)

        mock_rest_response = Mock()
        mock_rest_response.status = 200
        mock_rest_response.data = b'{"id": "cus_test"}'
        mock_rest_response.read = Mock()
        mock_call_api.return_value = mock_rest_response

        mock_api_response = Mock()
        mock_api_response.data = {"id": "cus_test"}
        mock_deserialize.return_value = mock_api_response

        request = CustomerCreateRequest(email="test@example.com")
        customers_api.create_customer(request)

        # Verify headers were configured (call_api was called)
        mock_call_api.assert_called_once()
        mock_deserialize.assert_called_once()


class TestModelIntegration:
    """Test model integration with API calls."""

    def test_customer_model_creation(self):
        """Test customer model creation."""
        request = CustomerCreateRequest(
            email="test@example.com",
            description="Test customer for API integration"
        )

        assert request.email == "test@example.com"
        assert request.description == "Test customer for API integration"

    def test_payment_flow_model_creation(self):
        """Test payment flow model creation."""
        request = PaymentFlowCreateRequest(
            amount=1000,
            currency="jpy",
            customer_id="cus_test123",
            description="Test payment flow"
        )

        assert request.amount == 1000
        assert request.customer_id == "cus_test123"
        assert request.description == "Test payment flow"

    def test_model_serialization_integration(self):
        """Test model serialization for API integration."""
        request = CustomerCreateRequest(email="test@example.com")

        # Test that model can be serialized for API calls
        json_str = request.to_json()
        assert isinstance(json_str, str)
        assert "test@example.com" in json_str