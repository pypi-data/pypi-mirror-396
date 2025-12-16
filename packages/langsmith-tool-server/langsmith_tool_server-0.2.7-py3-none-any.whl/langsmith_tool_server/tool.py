"""Custom tool decorator and base class."""

import asyncio
import inspect
import os
from dataclasses import dataclass
from typing import Any, Callable, List, Optional, Union

import httpx
import structlog
from fastapi import HTTPException
from pydantic import create_model

from langsmith_tool_server.context import Context

logger = structlog.getLogger(__name__)


@dataclass
class AuthSuccess:
    """Authentication succeeded."""

    token: Optional[str] = None


@dataclass
class AuthRequired:
    """OAuth flow required."""

    auth_url: str
    auth_id: Optional[str] = None


class Tool:
    """Simple tool class."""

    def __init__(
        self,
        func: Callable,
        auth_provider: Optional[str] = None,
        scopes: Optional[List[str]] = None,
        default_interrupt: bool = False,
        inject_context: Optional[bool] = None,
        integration: Optional[str] = None,
    ):
        self.func = func
        self.name = func.__name__
        self.description = func.__doc__ or ""
        self.auth_provider = auth_provider
        self.scopes = scopes or []
        self.default_interrupt = default_interrupt
        self.integration = integration

        if inject_context is not None:
            self.should_inject_context = inject_context
        else:
            self.should_inject_context = auth_provider is not None

        # Generate JSON schemas using Pydantic (similar to LangChain Core)
        self.input_schema = self._generate_input_schema()
        self.output_schema = self._generate_output_schema()

    def _generate_input_schema(self) -> dict:
        """Generate input schema from function signature using Pydantic."""
        sig = inspect.signature(self.func)

        has_context_param = "context" in sig.parameters
        if self.should_inject_context and not has_context_param:
            raise ValueError(
                f"Tool '{self.func.__name__}' has inject_context=True but no 'context' parameter. "
                f"Add 'context: Context' as the first parameter."
            )

        fields = {}
        for name, param in sig.parameters.items():
            if name == "context":
                if not self.should_inject_context:
                    raise ValueError(
                        f"Tool '{self.func.__name__}' has a 'context' parameter but inject_context is False. "
                        f"Set inject_context=True or add auth_provider to inject context. "
                    )
                if self.auth_provider and (not self.scopes or len(self.scopes) == 0):
                    raise ValueError(
                        f"Tool '{self.func.__name__}' has a 'context' parameter and auth_provider but no scopes were provided. "
                        f"Tools with auth_provider must specify at least one scope."
                    )
                continue

            # Require type annotation for all parameters
            if param.annotation == inspect.Parameter.empty:
                raise ValueError(
                    f"Tool '{self.func.__name__}': Parameter '{name}' missing type annotation. "
                    f"All tool parameters must have type annotations."
                )
            annotation = param.annotation
            default_value = (
                param.default if param.default != inspect.Parameter.empty else ...
            )

            fields[name] = (annotation, default_value)

        # Create Pydantic model from filtered fields
        try:
            InputModel = create_model("InputModel", **fields)
            return InputModel.model_json_schema()
        except Exception as e:
            raise ValueError(
                f"Tool '{self.func.__name__}' schema generation failed. "
                f"Check parameter types and ensure auth_provider is set if using Context parameters. "
                f"Original error: {e}"
            ) from e

    def _generate_output_schema(self) -> dict:
        """Generate output schema from function return type using Pydantic."""
        try:
            sig = inspect.signature(self.func)
            return_annotation = sig.return_annotation

            if return_annotation == inspect.Signature.empty:
                return {"type": "string"}

            OutputModel = create_model("Output", result=(return_annotation, ...))
            return OutputModel.model_json_schema()["properties"]["result"]
        except Exception:
            return {"type": "string"}

    async def _check_auth_status(
        self, user_id: str = None, request=None
    ) -> Union[AuthSuccess, AuthRequired]:
        """Auth hook that runs before tool execution.

        Args:
            user_id: User ID for authentication
            request: FastAPI request object (for auth forwarding mode)

        Returns:
            AuthSuccess with token if authentication succeeded
            AuthRequired with auth_url if OAuth flow needed
        """
        # Check if we should forward auth instead of using langchain_auth client
        forward_auth = (
            os.getenv("LANGSMITH_HOST_FORWARD_AUTH", "false").lower() == "true"
        )

        try:
            if forward_auth:
                return await self._make_auth_request_with_forwarding(request, user_id)
            else:
                return await self._make_auth_request_with_langchain_client(user_id)

        except ImportError as e:
            raise HTTPException(
                status_code=500, detail="Authentication library not installed"
            ) from e
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e

            error_str = str(e)
            # If HTTP error, return the given status code and detail
            if error_str.startswith("HTTP "):
                try:
                    status_code = int(error_str.split(":")[0].replace("HTTP ", ""))
                    raise HTTPException(
                        status_code=status_code, detail=error_str
                    ) from e
                except (ValueError, IndexError):
                    pass

            # Default to 500
            raise HTTPException(
                status_code=500, detail=f"Authentication failed: {error_str}"
            ) from e

    # Customers using the langsmith-tool-server should not need this path. But this is useful for the instance deployed
    # in our cloud so it can forward either kind of auth (bearer token or api key) to host-backend
    async def _make_auth_request_with_forwarding(
        self, request, user_id: str = None
    ) -> Union[AuthSuccess, AuthRequired]:
        """Make auth request by forwarding headers to host backend."""
        if not request:
            raise HTTPException(
                status_code=401,
                detail=f"Tool '{self.name}' requires auth forwarding but no request context available",
            )

        forward_headers = {}
        for header_name, header_value in request.headers.items():
            if header_name.lower() == "authorization":
                forward_headers["Authorization"] = header_value
            elif header_name.lower() == "x-api-key":
                forward_headers["X-API-Key"] = header_value
            elif header_name.lower() == "x-tenant-id":
                forward_headers["X-Tenant-Id"] = header_value
            elif header_name.lower() == "x-user-id":
                forward_headers["X-User-Id"] = header_value
            elif header_name.lower() == "x-service-key":
                forward_headers["X-Service-Key"] = header_value

        host_api_url = os.getenv("LANGSMITH_HOST_API_URL")
        if not host_api_url:
            raise HTTPException(
                status_code=500,
                detail="LANGSMITH_HOST_API_URL not configured for auth forwarding",
            )

        payload = {
            "user_id": user_id,
            "provider": self.auth_provider,
            "scopes": self.scopes or [],
            "use_agent_builder_public_oauth": True,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{host_api_url}/v2/auth/authenticate",
                json=payload,
                headers=forward_headers,
            )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Authentication failed: {response.text}",
                )

            try:
                auth_data = response.json()
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail="Invalid response from auth service",
                ) from e

            if auth_data.get("status") == "completed":
                return AuthSuccess(token=auth_data["token"])
            else:
                return AuthRequired(
                    auth_url=auth_data.get("url"), auth_id=auth_data.get("auth_id")
                )

    async def _make_auth_request_with_langchain_client(
        self, user_id: str = None
    ) -> Union[AuthSuccess, AuthRequired]:
        """Original langchain_auth client authentication."""
        if not user_id:
            raise HTTPException(
                status_code=401,
                detail=f"Tool '{self.name}' requires authentication but no authenticated user provided. Configure server-level authentication to use OAuth-enabled tools.",
            )

        try:
            from langchain_auth import Client

            api_key = os.getenv("LANGSMITH_API_KEY")
            if not api_key:
                raise RuntimeError(
                    f"Tool '{self.name}' requires auth but LANGSMITH_API_KEY environment variable not set"
                )

            api_url = os.getenv("LANGSMITH_HOST_API_URL")
            client_kwargs = {"api_key": api_key}
            if api_url:
                client_kwargs["api_url"] = api_url
            client = Client(**client_kwargs)
            auth_result = await client.authenticate(
                provider=self.auth_provider, scopes=self.scopes, user_id=user_id
            )

            if auth_result.needs_auth:
                return AuthRequired(
                    auth_url=auth_result.auth_url, auth_id=auth_result.auth_id
                )
            else:
                return AuthSuccess(token=auth_result.token)

        except ImportError as e:
            raise HTTPException(
                status_code=500, detail="Authentication library not installed"
            ) from e
        except Exception as e:
            error_str = str(e)

            # If HTTP error, return the given status code and detail
            if error_str.startswith("HTTP "):
                try:
                    status_code = int(error_str.split(":")[0].replace("HTTP ", ""))
                    raise HTTPException(
                        status_code=status_code, detail=error_str
                    ) from e
                except (ValueError, IndexError):
                    pass

            raise HTTPException(
                status_code=500, detail=f"Authentication failed: {error_str}"
            ) from e

    async def __call__(self, *args, user_id: str = None, request=None, **kwargs) -> Any:
        """Call the tool function with timeout protection."""
        timeout_seconds = float(os.getenv("LANGSMITH_TOOL_TIMEOUT_SECONDS", "300"))
        token = None

        if self.auth_provider:
            auth_result = await self._check_auth_status(
                user_id=user_id, request=request
            )

            if isinstance(auth_result, AuthRequired):
                return {
                    "auth_required": True,
                    "auth_url": auth_result.auth_url,
                    "auth_id": auth_result.auth_id,
                }

            assert isinstance(auth_result, AuthSuccess), (
                "Auth result must be AuthSuccess"
            )
            token = auth_result.token

        if self.should_inject_context:
            context = Context(token=token, request=request)
            args = (context,) + args

        try:
            if asyncio.iscoroutinefunction(self.func):
                result = await asyncio.wait_for(
                    self.func(*args, **kwargs), timeout=timeout_seconds
                )
            else:
                loop = asyncio.get_event_loop()
                result = await asyncio.wait_for(
                    loop.run_in_executor(None, lambda: self.func(*args, **kwargs)),
                    timeout=timeout_seconds,
                )

            return result
        except asyncio.TimeoutError:
            logger.error(
                f"tool_timeout tool={self.name} timeout_seconds={timeout_seconds}"
            )
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Tool execution exceeded timeout of {timeout_seconds} seconds. The operation took too long to complete.",
                    }
                ],
                "isError": True,
            }


def tool(
    func: Optional[Callable] = None,
    *,
    auth_provider: Optional[str] = None,
    scopes: Optional[List[str]] = None,
    default_interrupt: bool = False,
    inject_context: Optional[bool] = None,
    integration: Optional[str] = None,
) -> Any:
    """Decorator to create a tool from a function.

    Args:
        func: The function to wrap
        auth_provider: Name of the auth provider required
        scopes: List of OAuth scopes required
        default_interrupt: Whether interrupts are enabled by default
        inject_context: Whether to inject context
        integration: Integration identifier for grouping tools (e.g., "gmail", "slack")

    Usage:
        @tool
        def my_function():
            '''Description of my function'''
            return "result"

        @tool(auth_provider="google", scopes=["read", "write"], integration="gmail")
        def authenticated_function():
            '''Function requiring auth'''
            return "authenticated result"
    """

    def decorator(f: Callable) -> Tool:
        if auth_provider and (not scopes or len(scopes) == 0):
            raise ValueError(
                f"Tool '{f.__name__}': If auth_provider is specified, scopes must be provided with at least one scope"
            )

        if auth_provider and inject_context is True:
            raise ValueError(
                f"Tool '{f.__name__}': Cannot set both auth_provider and inject_context=True. "
                f"Tools with auth_provider automatically inject context."
            )

        # Validation: if auth_provider is given, first parameter must be 'context: Context'
        if auth_provider:
            import inspect
            from typing import get_type_hints

            sig = inspect.signature(f)
            params = list(sig.parameters.keys())

            # Check parameter name
            if not params or params[0] != "context":
                raise ValueError(
                    f"Tool '{f.__name__}': Tools with auth_provider must have 'context' as their first parameter"
                )

            # Check parameter type annotation
            try:
                type_hints = get_type_hints(f)
                if "context" in type_hints:
                    context_type = type_hints["context"]
                    if context_type != Context:
                        raise ValueError(
                            f"Tool '{f.__name__}': The 'context' parameter must be typed as 'Context', got '{context_type}'"
                        )
                else:
                    raise ValueError(
                        f"Tool '{f.__name__}': The 'context' parameter must have type annotation 'Context'"
                    )
            except Exception as e:
                raise ValueError(
                    f"Tool '{f.__name__}': Error validating context parameter type: {e}"
                ) from e

        return Tool(
            f,
            auth_provider=auth_provider,
            scopes=scopes,
            default_interrupt=default_interrupt,
            inject_context=inject_context,
            integration=integration,
        )

    # Handle both @tool and @tool() syntax
    if func is None:
        # Called as @tool(auth_provider="...", scopes=[...])
        return decorator
    else:
        # Called as @tool
        return decorator(func)
