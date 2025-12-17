import inspect
from functools import wraps
from typing import Optional, get_type_hints

from orchestral.tools.base.tool import BaseTool
from orchestral.tools.base.field_utils import RuntimeField


def define_tool(*dargs, **dkwargs):
    """
    Usage:

    @define_tool
    def multiply(a: float, b: float = 1.0):
        return a * b
    """

    # Support bare decorator and decorator with kwargs
    if dargs and callable(dargs[0]) and not dkwargs:
        return _define_tool_impl()(dargs[0])
    return _define_tool_impl(**dkwargs)


def _define_tool_impl(
    *,
    name: str | None = None,
    param_descriptions: dict[str, str] | None = None,
    base: type = BaseTool,
):
    param_descriptions = param_descriptions or {}

    def decorator(func):
        sig = inspect.signature(func)
        # Resolve forward refs using the function's globals
        try:
            hints = get_type_hints(func, globalns=getattr(func, "__globals__", None))
        except Exception:
            # Fallback if type resolution fails
            hints = {k: p.annotation for k, p in sig.parameters.items()}

        # Build __annotations__ and class attributes with RuntimeField
        class_annotations = {}
        class_dict = {"__doc__": func.__doc__ or ""}

        for name_, param in sig.parameters.items():
            if param.kind not in (param.POSITIONAL_ONLY,
                                  param.POSITIONAL_OR_KEYWORD,
                                  param.KEYWORD_ONLY):
                raise TypeError(f"Unsupported parameter kind for {name_}: {param.kind}")

            # Optional[annotation] to mirror "float | None" style
            ann = hints.get(name_, inspect._empty)
            opt_ann = Optional[ann] if ann is not inspect._empty else Optional[object]
            class_annotations[name_] = opt_ann

            desc = param_descriptions.get(name_, f"{name_}")
            default = param.default

            # Map to RuntimeField with or without default
            if default is inspect._empty:
                class_dict[name_] = RuntimeField(description=desc)
            else:
                class_dict[name_] = RuntimeField(description=desc, default=default)

        class_dict["__annotations__"] = class_annotations

        # _run implementation that pulls attributes from self and calls func
        def _run(self):
            kwargs = {p: getattr(self, p) for p in sig.parameters}
            return func(**kwargs)

        class_dict["_run"] = _run
        class_dict["__wrapped__"] = func  # helps introspection and debugging

        cls_name = name or f"{func.__name__}Tool"
        NewTool = type(cls_name, (base,), class_dict)

        # Return a thin wrapper that behaves like the original function factory
        # If your framework expects the class itself, you can just return NewTool
        return NewTool()
        # @wraps(func)
        # def factory(*args, **kwargs):
        #     # Convenience: allow direct call to run without manual instantiation
        #     inst = NewTool()
        #     for k, v in kwargs.items():
        #         setattr(inst, k, v)
        #     # For positional args, map in order
        #     for k, v in zip(sig.parameters, args):
        #         setattr(inst, k, v)
        #     return inst._run()

        # # Expose the generated class in case the caller wants it
        # factory.__define_tool_class__ = NewTool
        # return factory

    return decorator
