import functools
import inspect
import json
from inspect import Signature
from typing import (
    Any,
    Callable,
    Concatenate,
    Generic,
    ParamSpec,
    Tuple,
    Type,
    TypeVar,
    cast,
)

from django.http import HttpRequest, HttpResponse, QueryDict
from django.views import View
from htpy import Node, render_node
from icecream import ic

from hyperpony import ViewUtilsMixin

P = ParamSpec("P")
R = TypeVar("R")
T = TypeVar("T")


class ViewActionDescriptor(Generic[T, P, R]):
    """A descriptor that makes the decorated function a real method."""

    def __init__(self, func: Callable[Concatenate[T, P], R]):
        self.func = func
        self.is_view_action = True

        functools.update_wrapper(self, func)  # type: ignore

    def __get__(
        self, instance: T | None, owner: Type[T] | None = None
    ) -> "ViewActionDescriptor[T, P, R]":
        if instance is None:
            # Called on the class (e.g., MyView.action_toggle)
            return self
        # Called on the instance (e.g., my_view_instance.action_toggle)
        # Return a bound method with 'self' (the instance) already supplied.
        return functools.partial(self.func, instance)  # type: ignore


def view_action(func: Callable[Concatenate[T, P], R]) -> ViewActionDescriptor[T, P, R]:
    return ViewActionDescriptor(func)


def _check_view_action_and_return_with_signature(
    view_action_fn: Any,
) -> Tuple[Callable[..., Any], Signature]:
    fn = cast(Any, view_action_fn)
    if not getattr(fn, "is_view_action", False):
        raise Exception(
            f"The provided action function '{fn.__name__}' is not decorated with @view_action."
        )

    return fn, inspect.signature(fn)


class HtpyView(ViewUtilsMixin, View):
    # noinspection PyUnusedLocal
    def get(self, request, *args, **kwargs):
        return HttpResponse(render_node(self.render(request, *args, **kwargs)))

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def render(self, request: HttpRequest, *args, **kwargs) -> Node:
        raise NotImplementedError()

    def create_hx_get(self, **hx_vals_params) -> dict[str, Any]:
        return {"hx-get": self.path, **hx_vals(**hx_vals_params)}

    def create_hx_patch(self, **hx_vals_params) -> dict[str, Any]:
        return {"hx-patch": self.path, **hx_vals(**hx_vals_params)}

    def create_hx_post(self, **hx_vals_params) -> dict[str, Any]:
        return {"hx-post": self.path, **hx_vals(**hx_vals_params)}

    def create_hx_put(self, **hx_vals_params) -> dict[str, Any]:
        return {"hx-put": self.path, **hx_vals(**hx_vals_params)}

    def action_request(
        self, view_action_fn: ViewActionDescriptor[T, P, R], *args: P.args, **kwargs: P.kwargs
    ):
        ic(args, kwargs)

        fn, _ = _check_view_action_and_return_with_signature(view_action_fn)
        return self.create_hx_patch(__hp_action=fn.__name__)

    def patch(self, request: HttpRequest, *args, **kwargs):
        qd = QueryDict(request.body, encoding=request.encoding)
        if (action := qd.get("__hp_action")) is not None:
            action_fn = getattr(self, action, None)
            method, signature = _check_view_action_and_return_with_signature(action_fn)
            response = method() if len(signature.parameters) == 0 else method(request)
            if response is not None:
                return response
            return self.get(request, *args, **kwargs)

        # noinspection PyUnresolvedReferences
        return super().patch(request, *args, **kwargs)


def hx_vals(**kwargs) -> dict[str, Any]:
    return {"hx-vals": json.dumps({str(k): v for k, v in kwargs.items()})}
