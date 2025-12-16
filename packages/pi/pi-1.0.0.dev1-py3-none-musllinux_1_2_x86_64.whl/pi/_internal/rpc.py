from __future__ import annotations
from typing import TYPE_CHECKING, Any, Protocol, overload

import collections
import dataclasses
import inspect
import itertools
import functools
import sys
import types
import typing

from dataclasses import dataclass

from . import bus as _bus
from . import dataclass_extras as _dataclass_extras

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable


type _ParamSignature = dict[str, tuple[Any, Any]]


@dataclass(frozen=True, kw_only=True)
class RpcMethod:
    interface: str
    method: str
    params: _ParamSignature
    module: str
    result: str | None
    source: str | None


class RpcRegistry:
    def __init__(self) -> None:
        self._interfaces: collections.defaultdict[
            str, dict[str, RpcMethod]
        ] = collections.defaultdict(dict)

    def register(self, mm: RpcMethod) -> None:
        methods = self._interfaces[mm.interface]
        if mm.method in methods:
            raise ValueError(
                f"RPC method {mm.interface}:{mm.method} already registered"
            )
        methods[mm.method] = mm

    @property
    def methods(self) -> Iterable[RpcMethod]:
        return itertools.chain.from_iterable(
            iface.values() for iface in self._interfaces.values()
        )

    def get_interface(self, iface: str) -> dict[str, RpcMethod] | None:
        if iface in self._interfaces:
            return self._interfaces[iface]
        else:
            return None


_REGISTRY = RpcRegistry()


@overload
def export[T](func_or_proto: type[T], /) -> type[T]: ...


@overload
def export[**P, R](func_or_proto: Callable[P, R], /) -> Callable[P, R]: ...


def export[**P, R, T](
    func_or_proto: Callable[P, R] | type[T],
    /,
) -> Callable[P, R] | type[T]:
    """Mark function or Protocol class as an RPC method.

    If a regular callable is passed, it registers the function as before.
    If a Protocol class is passed, each of its methods is registered as
    an individual RPC method using the method name and signature.
    """
    if isinstance(func_or_proto, type) and typing.is_protocol(func_or_proto):
        _export_protocol(func_or_proto)
    elif inspect.iscoroutinefunction(func_or_proto):
        _export_func(func_or_proto)
    else:
        raise TypeError(
            f"{func_or_proto} is expected to be either "
            f"a typing.Protocol subclass or an async function"
        )

    return func_or_proto  # type: ignore [return-value]


def _export_protocol[T](proto: type[T]) -> None:
    _check_protocol_declaration(proto)

    modfile = sys.modules[proto.__module__].__file__

    for attrname in typing.get_protocol_members(proto):
        attr = getattr(proto, attrname)
        if not inspect.iscoroutinefunction(attr):
            raise TypeError(
                f"{attrname} is supposed to be an async function on {proto}"
            )

        params, return_type = _inspect_func(attr)
        _REGISTRY.register(
            RpcMethod(
                interface=proto.__name__,
                method=attrname,
                params=params,
                result=return_type,
                source=modfile,
                module=proto.__module__,
            )
        )


def _export_func[**P, R](func: Callable[P, R]) -> None:
    params, return_type = _inspect_func(func)
    mod = sys.modules[func.__module__]
    _REGISTRY.register(
        RpcMethod(
            interface=mod.__name__,
            method=func.__name__,
            params=params,
            result=return_type,
            source=mod.__file__,
            module=mod.__module__,
        )
    )


def _inspect_func[**P, R](func: Callable[P, R]) -> tuple[_ParamSignature, Any]:
    sig = inspect.signature(func)
    hints = typing.get_type_hints(func)
    params: dict[str, tuple[Any, Any]] = {}

    for pname, param in sig.parameters.items():
        if param.kind in (
            inspect.Parameter.VAR_POSITIONAL,
            inspect.Parameter.VAR_KEYWORD,
        ):
            raise TypeError(
                f"{func.__name__}: *args/**kwargs are not supported"
            )
        if pname == "self":
            continue

        if pname not in hints:
            raise TypeError(
                f"{func.__name__}: missing type annotation for "
                f"parameter {pname!r}"
            )

        ptype = hints[pname]

        default_val: Any
        if param.default is inspect.Parameter.empty:
            default_val = ...
        else:
            default_val = param.default

        params[pname] = (ptype, default_val)

    return_type = hints.get("return")

    return (params, return_type)


def get_exports() -> Iterable[RpcMethod]:
    return _REGISTRY.methods


def _check_protocol_declaration(proto: type[Any]) -> None:
    assert typing.is_protocol(proto)

    for meth_name in typing.get_protocol_members(proto):
        # Check that RPC methods only expose keyword-only parameters.
        # Besides this leading to more readable code, it's also
        # easier for us to separate this way low-level system args
        # from user-specified API-level ones.
        meth_proto = getattr(proto, meth_name)
        for i, param in enumerate(
            inspect.signature(meth_proto).parameters.values()
        ):
            if param.name == "self" and i == 0:
                continue
            if param.kind != inspect.Parameter.KEYWORD_ONLY:
                raise TypeError(
                    f"{proto.__name__}.{meth_name}() has "
                    f"a non-keyword-only parameter: {param.name!r}"
                )


class RpcInterfaceProxy:  # noqa: B903
    def __init__(self, _bus: _bus.Bus, receiver: str | None) -> None:
        self._bus = _bus
        self._receiver = receiver or "broadcast"


class ResponseMsg(Protocol):
    result: Any


class RpcInterfaceProxyMeta[T](type):
    def __new__(
        cls,
        name: str,
        bases: tuple[type[Any], ...],
        namespace: dict[str, Any],
        *,
        proto: type[T],
    ) -> RpcInterfaceProxyMeta[T]:
        iface = _REGISTRY.get_interface(proto.__name__)
        if iface is None:
            raise RuntimeError(f"unknown bus interface: {proto.__name__}")

        for mname, meth in iface.items():
            msg = f"{proto.__name__}:{mname}"
            proto_method = getattr(proto, mname)

            response_dataclass: type[ResponseMsg] = dataclasses.make_dataclass(
                f"{mname}_response",
                [("result", meth.result)],
                module=meth.module,
            )

            async def call(
                self: RpcInterfaceProxy,
                __timeout__: float = 1.0,
                __msg__: str = msg,
                __response_dataclass__: type[ResponseMsg] = response_dataclass,
                /,
                **kwargs: Any,
            ) -> Any:
                resp = await self._bus.call(
                    receiver=self._receiver,
                    message_name=__msg__,
                    payload=kwargs,
                    timeout=__timeout__,
                )

                if not resp:
                    raise RuntimeError(f"RPC call failed: {msg}")

                payload = resp.get("payload")
                return _dataclass_extras.coerce_to_dataclass(
                    __response_dataclass__, payload
                ).result

            functools.update_wrapper(call, proto_method)
            namespace[mname] = call

        return super().__new__(cls, name, bases, namespace)


_PROXIES: dict[type[Any], type[Any]] = {}


def get_interface_proxy_class[T](cls: type[T]) -> type[T]:
    if (proxy := _PROXIES.get(cls)) is not None:
        return proxy

    proxy = types.new_class(
        cls.__name__,
        (RpcInterfaceProxy,),
        dict(metaclass=RpcInterfaceProxyMeta, proto=cls),
    )

    _PROXIES[cls] = proxy

    return proxy


def get_interface[T](
    proto: type[T], _bus: _bus.Bus, receiver: str | None = None
) -> T:
    proxy = get_interface_proxy_class(proto)
    return proxy(_bus, receiver)  # type: ignore [call-arg]


def implement[T](proto: type[T], _bus: _bus.Bus, impl: T) -> None:
    iface = _REGISTRY.get_interface(proto.__name__)
    assert iface is not None

    for meth_name in iface:
        msg_name = f"{proto.__name__}:{meth_name}"

        meth = getattr(impl, meth_name)
        assert inspect.ismethod(meth) and inspect.iscoroutinefunction(meth)

        _bus.implement(msg_name, meth)


def listen(proto: type[Any], _bus: _bus.Bus, impl: Any) -> None:
    _check_protocol_declaration(proto)

    iface = _REGISTRY.get_interface(proto.__name__)
    assert iface is not None

    for meth_name, meth in iface.items():
        msg_name = f"{proto.__name__}:{meth_name}"

        meth_impl = getattr(impl, meth_name, None)
        if not inspect.ismethod(meth_impl):
            continue
        assert inspect.iscoroutinefunction(meth_impl)

        req_dataclass: type = dataclasses.make_dataclass(
            f"{meth_name}_request",
            [(n, t[0]) for n, t in meth.params.items()],
            module=meth.module,
        )

        async def call(
            __req_dataclass__: type = req_dataclass,
            __meth_impl__: Callable[..., Any] = meth_impl,  # type: ignore [assignment]
            /,
            **payload: Any,
        ) -> Any:
            kwargs: object = _dataclass_extras.coerce_to_dataclass(
                __req_dataclass__, payload
            )

            return await __meth_impl__(**kwargs.__dict__)

        _bus.subscribe(msg_name, call)
