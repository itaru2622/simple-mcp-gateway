from typing import Any, Callable, overload
from mcp.types import AnyFunction

from fastmcp import FastMCP
from fastmcp.server.server import F

class MCPRouter:
    '''A class for managing MCP components independently of the main FastMCP instance.

    This class allows you to define and categorize MCP tools, resources, and prompts separately 
    from the main FastMCP instance for better modularity, as APIRouter does in FastAPI.

    Attributes:
        _tools:              List of tool definitions to be registered.
        _resources:          List of resource definitions to be registered.
        _prompts:            List of prompt definitions to be registered.

    Usage:

    # in featureA.py -------------
    # almost the same as official echo sample, except using @router instead of @mcp
    # cf. https://github.com/modelcontextprotocol/python-sdk/blob/main/examples/mcpserver/echo.py

    from utils.mcprouter import MCPRouter

    # simply, create and use @router, instead of @mcp
    router = MCPRouter()

    @router.tool
    def echo_tool(text: str) -> str:
        """Echo the input text"""
        return text

    @router.resource("echo://static")
    def echo_resource() -> str:
        return "Echo!"

    @router.resource("echo://{text}")
    def echo_template(text: str) -> str:
        """Echo the input text"""
        return f"Echo: {text}"

    @router.prompt("echo")
    def echo_prompt(text: str) -> str:
        return text

    # in app.py --------

    from fastmcp  import FastMCP
    from featureA import router
    from featureB import router as routerB

    mcp=FastMCP()
    router.register_to(mcp)
    routerB.register_to(mcp)

    if __name__ == '__main__':
        mcp.run()

    '''

    def __init__(self) -> None:
        """
        Initialize the MCPRouter with isolated registries for each component type.
        """
        self._tools:              list[tuple[F, tuple[Any, ...], dict[str, Any]]] = []
        self._resources:          list[tuple[F, tuple[Any, ...], dict[str, Any]]] = []
        self._prompts:            list[tuple[F, tuple[Any, ...], dict[str, Any]]] = []

    @overload
    def tool(self, name_or_fn: F, **kwargs: Any) -> F: ...

    @overload
    def tool(self, name_or_fn: str | None = None,**kwargs: Any) -> Callable[[F], F]: ...

    def tool(self, name_or_fn: str | F | None = None, **kwargs: Any) -> (F | Callable[[F], F]):
        """Keep a tool definition, for later registration.

        Args:
            name_or_fn: The name of the tool or the function itself.
            **kwargs: Additional keyword arguments for tool configuration.

        Returns:
            The decorated function or a decorator function.
        """
        def decorator(func: F) -> F:
            # Store name as a positional argument if provided as a string
            args = (name_or_fn,) if isinstance(name_or_fn, str) else ()
            self._tools.append((func, args, kwargs))
            return func

        if callable(name_or_fn):
            return decorator(name_or_fn)
        return decorator


    def resource(self, uri: str , **kwargs: Any) -> (F |  Callable[[F], F]):
        """Keep a resource definition, for later registration.

        Args:
            uri_or_fn: The URI of the resource or the function itself.
            **kwargs: Additional keyword arguments for resource configuration.

        Returns:
            The decorated function or a decorator function.
        """
        def decorator(func: F) -> F:
            args = (uri,)
            self._resources.append((func, args, kwargs))
            return func

        return decorator


    @overload
    def prompt(self, name_or_fn: F, **kwargs: Any) -> F: ...
    
    @overload
    def prompt(self, name_or_fn: str | None = None, **kwargs: Any) -> Callable[[F], F]: ...
    
    def prompt(self, name_or_fn: str | F | None = None, **kwargs: Any) -> (F | Callable[[F], F]) :
        """Keep a prompt definition, for later registration.

        Args:
            name_or_fn: The name of the prompt or the function itself.
            **kwargs: Additional keyword arguments for prompt configuration.

        Returns:
            The decorated function or a decorator function.
        """
        def decorator(func: F) -> F:
            args = (name_or_fn,) if isinstance(name_or_fn, str) else ()
            self._prompts.append((func, args, kwargs))
            return func

        if callable(name_or_fn):
            return decorator(name_or_fn)
        return decorator


    def register_to(self, mcp: FastMCP) -> None:
        """Register all collected components to the specified FastMCP instance.

        This method iterates through all stored definitions
        and applies them to the FastMCP instance with FastMCP built-in method simply.

        Args:
            mcp: The target FastMCP instance.
        """

        # for tools
        for func, args, kwargs in self._tools:
            mcp.tool(*args, **kwargs)(func)

        # for resources
        for func, args, kwargs in self._resources:
            mcp.resource(*args, **kwargs)(func)

        # for prompts
        for func, args, kwargs in self._prompts:
            mcp.prompt(*args, **kwargs)(func)
