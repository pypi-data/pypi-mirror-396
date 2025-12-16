"""Unit tests for Context injection behavior."""

from unittest.mock import MagicMock

import pytest

from langsmith_tool_server import Context, tool
from langsmith_tool_server.tool import AuthRequired, AuthSuccess


class TestContextInjection:
    """Test Context parameter injection behavior."""

    @pytest.mark.asyncio
    async def test_context_has_fresh_token_on_each_call(self):
        """Test that Context receives fresh token from auth hook on each call."""

        @tool(auth_provider="test_provider", scopes=["test_scope"])
        def test_tool(context: Context, message: str) -> str:
            """Test tool that uses context."""
            return f"token={context.token}, message={message}"

        # Mock the auth hook to return different tokens
        call_count = [0]

        async def mock_check_auth_status(user_id=None, request=None):
            call_count[0] += 1
            return AuthSuccess(token=f"token_{call_count[0]}")

        test_tool._check_auth_status = mock_check_auth_status

        # First call
        result1 = await test_tool(message="first", user_id="user1", request=MagicMock())
        assert result1 == "token=token_1, message=first"

        # Second call should get fresh token
        result2 = await test_tool(
            message="second", user_id="user1", request=MagicMock()
        )
        assert result2 == "token=token_2, message=second"

        # Third call should get fresh token
        result3 = await test_tool(message="third", user_id="user1", request=MagicMock())
        assert result3 == "token=token_3, message=third"

    @pytest.mark.asyncio
    async def test_context_has_fresh_request_on_each_call(self):
        """Test that Context receives fresh request object on each call."""

        @tool(auth_provider="test_provider", scopes=["test_scope"])
        def test_tool(context: Context, message: str) -> str:
            """Test tool that uses context request."""
            return f"method={context.request.method}, message={message}"

        # Mock auth hook
        async def mock_check_auth_status(user_id=None, request=None):
            return AuthSuccess(token="test_token")

        test_tool._check_auth_status = mock_check_auth_status

        # Create different request objects
        request1 = MagicMock()
        request1.method = "GET"

        request2 = MagicMock()
        request2.method = "POST"

        request3 = MagicMock()
        request3.method = "PUT"

        # Each call should get the request that was passed
        result1 = await test_tool(message="first", user_id="user1", request=request1)
        assert result1 == "method=GET, message=first"

        result2 = await test_tool(message="second", user_id="user1", request=request2)
        assert result2 == "method=POST, message=second"

        result3 = await test_tool(message="third", user_id="user1", request=request3)
        assert result3 == "method=PUT, message=third"

    @pytest.mark.asyncio
    async def test_context_injection_without_auth_provider(self):
        """Test Context injection with inject_context=True but no auth_provider."""

        @tool(inject_context=True)
        def test_tool(context: Context, message: str) -> str:
            """Test tool with inject_context but no auth."""
            has_token = context.token is not None
            has_request = context.request is not None
            return (
                f"has_token={has_token}, has_request={has_request}, message={message}"
            )

        # Call without auth - should still get context
        request = MagicMock()
        result = await test_tool(message="test", request=request)

        assert result == "has_token=False, has_request=True, message=test"

    @pytest.mark.asyncio
    async def test_check_auth_status_returns_auth_required(self):
        """Test that auth_required response is properly returned."""

        @tool(auth_provider="test_provider", scopes=["test_scope"])
        def test_tool(context: Context, message: str) -> str:
            """Test tool that requires auth."""
            return message

        # Mock auth hook to return auth required
        async def mock_check_auth_status(user_id=None, request=None):
            return AuthRequired(auth_url="https://auth.example.com", auth_id="auth123")

        test_tool._check_auth_status = mock_check_auth_status

        # Call should return auth_required response
        result = await test_tool(message="test", user_id="user1", request=MagicMock())

        assert isinstance(result, dict)
        assert result["auth_required"] is True
        assert result["auth_url"] == "https://auth.example.com"
        assert result["auth_id"] == "auth123"

    @pytest.mark.asyncio
    async def test_context_token_is_none_when_auth_returns_none(self):
        """Test that Context.token is None when auth hook returns None token."""

        @tool(auth_provider="test_provider", scopes=["test_scope"])
        def test_tool(context: Context) -> str:
            """Test tool."""
            return f"token_is_none={context.token is None}"

        # Mock auth hook to return AuthSuccess with None token
        async def mock_check_auth_status(user_id=None, request=None):
            return AuthSuccess(token=None)

        test_tool._check_auth_status = mock_check_auth_status

        result = await test_tool(user_id="user1", request=MagicMock())
        assert result == "token_is_none=True"
