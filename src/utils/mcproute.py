from typing import Any, Callable, Dict, List, Optional, Tuple, TypeVar, Union
from fastmcp import FastMCP

T = TypeVar("T", bound=Callable[..., Any])

class MCPRouter:
    """A class for managing MCP components independently of the main FastMCP instance.

    This class allows you to define and categorize MCP tools, resources, and prompts separately 
    from the main FastMCP instance for better modularity, as APIRouter does in FastAPI.

    Attributes:
        _tools:              List of tool definitions to be registered.
        _resources:          List of resource definitions to be registered.
        _resource_templates: List of resource template definitions to be registered.
        _prompts:            List of prompt definitions to be registered.

    Usage:

    # in featureA.py -------------

    from utils.mcproute import MCPRoute
    router = MCPRouter()

    # simply, create and use @router, instead of @mcp
    @router.tool()
    def hello_world(str: name) -> str:
       return f'Hello, {name}!'

    # in app.py --------

    from fastmcp  import FastMCP
    from featureA import router
    from featureB import router as routerB

    mcp=FastMCP()
    router.register_to(mcp)
    routerB.register_to(mcp)

    if __name__ == '__main__':
        mcp.run()

    """

    def __init__(self) -> None:
        """
        Initialize the MCPRouter with isolated registries for each component type.
        """
        self._tools:              List[Tuple[T, Tuple[Any, ...], Dict[str, Any]]] = []
        self._resources:          List[Tuple[T, Tuple[Any, ...], Dict[str, Any]]] = []
        self._resource_templates: List[Tuple[T, Tuple[Any, ...], Dict[str, Any]]] = []
        self._prompts:            List[Tuple[T, Tuple[Any, ...], Dict[str, Any]]] = []


    def tool(self, name_or_fn: Union[str, T, None] = None, **kwargs: Any) -> Union[T,  Callable[[T], T]]:
        """Keep a tool definition, for later registration.

        Args:
            name_or_fn: The name of the tool or the function itself.
            **kwargs: Additional keyword arguments for tool configuration.

        Returns:
            The decorated function or a decorator function.
        """
        def decorator(func: T) -> T:
            # Store name as a positional argument if provided as a string
            args = (name_or_fn,) if isinstance(name_or_fn, str) else ()
            self._tools.append((func, args, kwargs))
            return func

        if callable(name_or_fn):
            return decorator(name_or_fn)
        return decorator


    def resource(self, uri_or_fn: Union[str, T, None] = None, **kwargs: Any) -> Union[T,  Callable[[T], T]]:
        """Keep a resource definition, for later registration.

        Args:
            uri_or_fn: The URI of the resource or the function itself.
            **kwargs: Additional keyword arguments for resource configuration.

        Returns:
            The decorated function or a decorator function.
        """
        def decorator(func: T) -> T:
            # Store URI as a positional argument if provided as a string
            args = (uri_or_fn,) if isinstance(uri_or_fn, str) else ()
            self._resources.append((func, args, kwargs))
            return func

        if callable(uri_or_fn):
            return decorator(uri_or_fn)
        return decorator


    def resource_template(self, uri_template_or_fn: Union[str, T, None] = None, **kwargs: Any) -> Union[T,  Callable[[T], T]]:
        """Keep a resource_template definition, for later registration.

        Args:
            uri_template_or_fn: The URI template or the function itself.
            **kwargs: Additional keyword arguments for template configuration.

        Returns:
            The decorated function or a decorator function.
        """
        def decorator(func: T) -> T:
            args = (uri_template_or_fn,) if isinstance(uri_template_or_fn, str) else ()
            self._resource_templates.append((func, args, kwargs))
            return func

        if callable(uri_template_or_fn):
            return decorator(uri_template_or_fn)
        return decorator


    def prompt(self, name_or_fn: Union[str, T, None] = None, **kwargs: Any) -> Union[T,  Callable[[T], T]]:
        """Keep a prompt definition, for later registration.

        Args:
            name_or_fn: The name of the prompt or the function itself.
            **kwargs: Additional keyword arguments for prompt configuration.

        Returns:
            The decorated function or a decorator function.
        """
        def decorator(func: T) -> T:
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

        # for resource templates
        for func, args, kwargs in self._resource_templates:
            mcp.resource_template(*args, **kwargs)(func)

        # for prompts
        for func, args, kwargs in self._prompts:
            mcp.prompt(*args, **kwargs)(func)
