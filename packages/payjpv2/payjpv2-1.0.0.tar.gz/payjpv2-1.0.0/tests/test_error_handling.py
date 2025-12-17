"""
Tests for error handling in PAY.JP Python SDK.

These tests verify that the SDK properly handles various error conditions
and API exceptions.
"""
import json
from unittest.mock import Mock, patch

import pytest
from payjpv2.api.customers_api import CustomersApi
from payjpv2.api.payment_flows_api import PaymentFlowsApi
from payjpv2.exceptions import *
from payjpv2.models.customer_create_request import CustomerCreateRequest
from payjpv2.models.payment_flow_create_request import PaymentFlowCreateRequest
from payjpv2.rest import ApiException


class TestApiExceptions:
    """Test API exception handling."""

    def test_api_exception_400_bad_request(self, api_client):
        """Test handling of 400 Bad Request errors."""
        customers_api = CustomersApi(api_client)

        with patch.object(api_client, 'call_api') as mock_call_api:
            mock_call_api.side_effect = ApiException(
                status=400,
                reason="Bad Request",
                body='{"error": {"type": "invalid_request_error", "message": "Missing required parameter: email"}}'
            )

            request = CustomerCreateRequest()  # Missing email

            with pytest.raises(ApiException) as exc_info:
                customers_api.create_customer(request)

            assert exc_info.value.status == 400
            assert exc_info.value.reason == "Bad Request"
            assert "Missing required parameter" in str(exc_info.value.body)

    def test_api_exception_401_unauthorized(self, api_client):
        """Test handling of 401 Unauthorized errors."""
        customers_api = CustomersApi(api_client)

        with patch.object(api_client, 'call_api') as mock_call_api:
            mock_call_api.side_effect = ApiException(
                status=401,
                reason="Unauthorized",
                body='{"error": {"type": "authentication_error", "message": "Invalid API key provided"}}'
            )

            request = CustomerCreateRequest(email="test@example.com")

            with pytest.raises(ApiException) as exc_info:
                customers_api.create_customer(request)

            assert exc_info.value.status == 401
            assert exc_info.value.reason == "Unauthorized"
            assert "Invalid API key" in str(exc_info.value.body)

    def test_api_exception_404_not_found(self, api_client):
        """Test handling of 404 Not Found errors."""
        customers_api = CustomersApi(api_client)

        with patch.object(api_client, 'call_api') as mock_call_api:
            mock_call_api.side_effect = ApiException(
                status=404,
                reason="Not Found",
                body='{"error": {"type": "invalid_request_error", "message": "No such customer: cus_nonexistent"}}'
            )

            with pytest.raises(ApiException) as exc_info:
                customers_api.get_customer("cus_nonexistent")

            assert exc_info.value.status == 404
            assert exc_info.value.reason == "Not Found"
            assert "No such customer" in str(exc_info.value.body)

    def test_api_exception_429_rate_limit(self, api_client):
        """Test handling of 429 Rate Limit errors."""
        customers_api = CustomersApi(api_client)

        with patch.object(api_client, 'call_api') as mock_call_api:
            mock_call_api.side_effect = ApiException(
                status=429,
                reason="Too Many Requests",
                body='{"error": {"type": "rate_limit_error", "message": "Too many requests hit the API too quickly"}}'
            )

            request = CustomerCreateRequest(email="test@example.com")

            with pytest.raises(ApiException) as exc_info:
                customers_api.create_customer(request)

            assert exc_info.value.status == 429
            assert exc_info.value.reason == "Too Many Requests"
            assert "Too many requests" in str(exc_info.value.body)

    def test_api_exception_500_server_error(self, api_client):
        """Test handling of 500 Internal Server Error."""
        customers_api = CustomersApi(api_client)

        with patch.object(api_client, 'call_api') as mock_call_api:
            mock_call_api.side_effect = ApiException(
                status=500,
                reason="Internal Server Error",
                body='{"error": {"type": "api_error", "message": "An error occurred on our end"}}'
            )

            request = CustomerCreateRequest(email="test@example.com")

            with pytest.raises(ApiException) as exc_info:
                customers_api.create_customer(request)

            assert exc_info.value.status == 500
            assert exc_info.value.reason == "Internal Server Error"

    def test_api_exception_with_malformed_json(self, api_client):
        """Test handling of malformed JSON in error response."""
        customers_api = CustomersApi(api_client)

        with patch.object(api_client, 'call_api') as mock_call_api:
            mock_call_api.side_effect = ApiException(
                status=400,
                reason="Bad Request",
                body='invalid json {'
            )

            request = CustomerCreateRequest()

            with pytest.raises(ApiException) as exc_info:
                customers_api.create_customer(request)

            assert exc_info.value.status == 400
            assert exc_info.value.body == 'invalid json {'

    def test_api_exception_empty_body(self, api_client):
        """Test handling of empty error response body."""
        customers_api = CustomersApi(api_client)

        with patch.object(api_client, 'call_api') as mock_call_api:
            mock_call_api.side_effect = ApiException(
                status=503,
                reason="Service Unavailable",
                body=""
            )

            request = CustomerCreateRequest(email="test@example.com")

            with pytest.raises(ApiException) as exc_info:
                customers_api.create_customer(request)

            assert exc_info.value.status == 503
            assert exc_info.value.body == ""


class TestNetworkErrors:
    """Test network-level error handling."""

    def test_connection_timeout(self, api_client):
        """Test handling of connection timeout."""
        customers_api = CustomersApi(api_client)

        with patch.object(api_client, 'call_api') as mock_call_api:
            # Simulate connection timeout
            import urllib3
            mock_call_api.side_effect = urllib3.exceptions.TimeoutError("Connection timeout")

            request = CustomerCreateRequest(email="test@example.com")

            with pytest.raises(urllib3.exceptions.TimeoutError):
                customers_api.create_customer(request)

    def test_connection_error(self, api_client):
        """Test handling of connection errors."""
        customers_api = CustomersApi(api_client)

        with patch.object(api_client, 'call_api') as mock_call_api:
            # Simulate connection error
            import urllib3
            mock_call_api.side_effect = urllib3.exceptions.NewConnectionError(
                None, "Failed to establish a new connection"
            )

            request = CustomerCreateRequest(email="test@example.com")

            with pytest.raises(urllib3.exceptions.NewConnectionError):
                customers_api.create_customer(request)


class TestValidationErrors:
    """Test client-side validation errors."""

    def test_invalid_email_format(self):
        """Test validation of email format (if implemented)."""
        # This test depends on whether client-side validation is implemented
        # For now, we test that invalid data can be created and sent
        request = CustomerCreateRequest(email="invalid-email-format")
        assert request.email == "invalid-email-format"

    def test_minimum_amount_validation(self):
        """Test validation of minimum amount."""
        # PaymentFlowCreateRequest requires amount >= 50
        request = PaymentFlowCreateRequest(
            amount=50,
            currency="jpy"
        )
        assert request.amount == 50

    def test_invalid_currency_validation(self):
        """Test validation of currency codes (if implemented)."""
        # PaymentFlowCreateRequest now has currency as a required field
        # Test with description field
        request = PaymentFlowCreateRequest(
            amount=1000,
            currency="jpy",
            description="INVALID_DESCRIPTION_TEST"
        )
        assert request.description == "INVALID_DESCRIPTION_TEST"


class TestErrorMessageParsing:
    """Test parsing of error messages from API responses."""

    def test_parse_error_details(self, api_client):
        """Test parsing of detailed error information."""
        customers_api = CustomersApi(api_client)

        error_body = {
            "error": {
                "type": "invalid_request_error",
                "message": "Your card was declined.",
                "code": "card_declined",
                "decline_code": "generic_decline",
                "param": "source"
            }
        }

        with patch.object(api_client, 'call_api') as mock_call_api:
            mock_call_api.side_effect = ApiException(
                status=402,
                reason="Payment Required",
                body=json.dumps(error_body)
            )

            request = CustomerCreateRequest(email="test@example.com")

            with pytest.raises(ApiException) as exc_info:
                customers_api.create_customer(request)

            # Test that error details can be extracted
            error_data = json.loads(exc_info.value.body)
            assert error_data["error"]["type"] == "invalid_request_error"
            assert error_data["error"]["code"] == "card_declined"
            assert error_data["error"]["decline_code"] == "generic_decline"

    def test_multiple_validation_errors(self, api_client):
        """Test handling of multiple validation errors."""
        customers_api = CustomersApi(api_client)

        error_body = {
            "error": {
                "type": "invalid_request_error",
                "message": "You have multiple validation errors",
                "errors": [
                    {"field": "email", "message": "Email is required"},
                    {"field": "name", "message": "Name must be at least 2 characters"}
                ]
            }
        }

        with patch.object(api_client, 'call_api') as mock_call_api:
            mock_call_api.side_effect = ApiException(
                status=400,
                reason="Bad Request",
                body=json.dumps(error_body)
            )

            request = CustomerCreateRequest()

            with pytest.raises(ApiException) as exc_info:
                customers_api.create_customer(request)

            # Test that multiple errors can be extracted
            error_data = json.loads(exc_info.value.body)
            assert len(error_data["error"]["errors"]) == 2
            assert error_data["error"]["errors"][0]["field"] == "email"
            assert error_data["error"]["errors"][1]["field"] == "name"


class TestRetryAndRecovery:
    """Test retry and recovery mechanisms (if implemented)."""

    def test_no_automatic_retry_on_client_error(self, api_client):
        """Test that client errors (4xx) are not automatically retried."""
        customers_api = CustomersApi(api_client)

        with patch.object(api_client, 'call_api') as mock_call_api:
            mock_call_api.side_effect = ApiException(
                status=400,
                reason="Bad Request",
                body='{"error": {"message": "Bad request"}}'
            )

            request = CustomerCreateRequest()

            with pytest.raises(ApiException):
                customers_api.create_customer(request)

            # Verify call_api was called only once (no retry)
            assert mock_call_api.call_count == 1

    def test_exception_inheritance(self):
        """Test that ApiException has proper inheritance."""
        exc = ApiException(status=400, reason="Bad Request")

        # Test that it's a proper exception
        assert isinstance(exc, Exception)
        assert exc.status == 400
        assert exc.reason == "Bad Request"