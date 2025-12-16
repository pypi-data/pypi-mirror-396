from collections.abc import Callable
from dataclasses import dataclass
from functools import wraps
from inspect import signature
from typing import Any, TypedDict

from langchain_core.tools import Tool as LangchainTool
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field


class BindableToolSchema(TypedDict):
    name: str
    description: str
    parameters: dict[str, Any]
    strict: bool


class Tool(BaseModel):
    fn: Callable[..., Any] = Field(
        exclude=True,  # don't serialize this
        description="Function to call when the tool is invoked",
    )
    name: str = Field(description="Name of the tool")
    description: str = Field(description="Description of the tool")
    context_args: list[str] | None = Field(
        None, description="List of kwarg names that will be injected from context. "
    )

    def add_to_mcp(self, mcp: FastMCP) -> None:
        if self.context_args is not None:
            fn = wrap_context_args(self.fn, self.context_args)
            mcp.add_tool(fn, self.name, self.description, self.context_args)
        else:
            mcp.add_tool(self.fn, self.name, self.description)

    def to_langchain_tool(self) -> LangchainTool: ...

    def to_bindable_tool(self) -> BindableToolSchema: ...


def wrap_context_args(
    fn: Callable[..., Any],
    context_args: list[str],
    context_param_name: str = "ctx",
) -> Callable[..., Any]:
    """Wrap the function with the context arguments.

    Args:
        fn: The function to wrap.
        context_args: The arguments to inject from the context.
        context_param_name: The name of the context parameter.

    Returns:
        The wrapped function.

    Example:
        ```python
        def f(x: int, y: int) -> int:
            return x + y
        f_ = wrap_context_args(f, ["x"])
        ```

        `f_` is equivalent to:
        ```python
        def f_(y: int, ctx: Context) -> int:
            x = ctx.request_context.lifespan_context.x
            return x + y
        ```
    """
    sig = signature(fn)
    params = list(sig.parameters.keys())

    @wraps(fn)
    def wrapped(*args, **kwargs):
        # Get context from kwargs
        ctx = kwargs.pop(context_param_name, None)
        if ctx is None:
            raise ValueError(
                f"Missing required context parameter '{context_param_name}'"
            )

        # Extract values from context
        context_values = {}
        for arg_name in context_args:
            value = getattr(ctx.request_context.lifespan_context, arg_name)
            context_values[arg_name] = value

        # Remove context args from params list to get remaining params
        remaining_params = [p for p in params if p not in context_args]

        # Map positional args to remaining params
        args_dict = dict(zip(remaining_params, args, strict=False))

        # Combine all args
        all_kwargs = {**context_values, **args_dict, **kwargs}

        return fn(**all_kwargs)

    return wrapped


if __name__ == "__main__":

    @dataclass
    class MockLifespanContext:
        x: int = 10
        y: int = 20

    @dataclass
    class MockRequestContext:
        lifespan_context: MockLifespanContext

    @dataclass
    class MockContext:
        request_context: MockRequestContext

    def test_wrap_context_args():
        # Test basic functionality
        def add(x: int, y: int) -> int:
            return x + y

        wrapped = wrap_context_args(add, ["x"])
        ctx = MockContext(MockRequestContext(MockLifespanContext()))
        assert wrapped(y=5, ctx=ctx) == 15  # 10 + 5

        # Test multiple context args
        def multiply(x: int, y: int, z: int) -> int:
            return x * y * z

        wrapped = wrap_context_args(multiply, ["x", "y"])
        assert wrapped(z=2, ctx=ctx) == 400  # 10 * 20 * 2

        # Test error when context missing
        try:
            wrapped(z=2)
            raise AssertionError("Should have raised ValueError")
        except ValueError as e:
            assert str(e) == "Missing required context parameter 'ctx'"

        print("All tests passed!")

    test_wrap_context_args()
