# SPDX-FileCopyrightText: 2024 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import functools
import inspect
import typing
from abc import ABC, abstractmethod
from collections.abc import Callable, Iterator, Sequence
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any, ClassVar, TypeVar

import click
import pydantic
from pydantic.fields import FieldInfo
from pydantic_core import ErrorDetails

from pglift.annotations import cli
from pglift.exceptions import MutuallyExclusiveError
from pglift.models.helpers import is_optional, optional_type
from pglift.models.interface import PresenceState
from pglift.types import (
    Operation,
    field_annotation,
    validation_context,
)
from pglift.util import deep_update, lenient_issubclass

from . import _site, logger

ModelType = type[pydantic.BaseModel]
T = TypeVar("T", bound=pydantic.BaseModel)
Callback = Callable[..., Any]
ClickDecorator = Callable[[Callback], Callback]
DEFAULT = object()


def as_parameters(model_type: ModelType, operation: Operation) -> ClickDecorator:
    """Attach click parameters (arguments or options) built from a pydantic
    model to the command.

    The argument in callback function must match the base name (lower-case) of
    the pydantic model class. Otherwise, a TypeError is raised.
    """

    def decorator(f: Callback) -> Callback:
        modelnames_and_argnames, paramspecs = zip(
            *reversed(list(_paramspecs_from_model(model_type, operation))), strict=True
        )

        def params_to_modelargs(kwargs: dict[str, Any]) -> dict[str, Any]:
            args = {}
            for modelname, argname in modelnames_and_argnames:
                value = kwargs.pop(argname)
                if value is DEFAULT:
                    continue  # ignore unset or set with default value parameters
                args[modelname] = value
            return args

        if operation == "update":
            # For update operation, we don't parse parameters into target
            # model.

            @functools.wraps(f)
            def callback(**kwargs: Any) -> Any:
                args = params_to_modelargs(kwargs)
                values = unnest(model_type, args)
                kwargs.update(values)
                with catch_validationerror(*paramspecs):
                    return f(**kwargs)

        else:
            s = inspect.signature(f)
            model_argname = model_type.__name__.lower()
            try:
                model_param = s.parameters[model_argname]
            except KeyError as e:
                raise TypeError(
                    f"expecting a '{model_argname}: {model_type.__name__}' parameter in '{f.__name__}{s}'"
                ) from e
            ptype = model_param.annotation
            if isinstance(ptype, str):
                # The annotation is "stringized"; we thus follow the wrapper
                # chain as suggested in Python how-to about annotations.
                # Implementation is simplified version of inspect.get_annotations().
                w = f
                while True:
                    if hasattr(w, "__wrapped__"):
                        w = w.__wrapped__
                    elif isinstance(w, functools.partial):
                        w = w.func
                    else:
                        break
                if hasattr(w, "__globals__"):
                    f_globals = w.__globals__
                ptype = eval(ptype, f_globals, None)  # nosec: B307
            if ptype not in (
                model_type,
                inspect.Signature.empty,
            ) and not issubclass(model_type, ptype):
                raise TypeError(
                    f"expecting a '{model_argname}: {model_type.__name__}' parameter in '{f.__name__}{s}'; got {model_param.annotation}"
                )

            @functools.wraps(f)
            def callback(**kwargs: Any) -> Any:
                args = params_to_modelargs(kwargs)
                with (
                    catch_validationerror(*paramspecs),
                    validation_context(operation=operation, settings=_site.SETTINGS),
                ):
                    model = parse_params_as(model_type, args)
                kwargs[model_argname] = model
                return f(**kwargs)

        cb = callback
        for p in paramspecs:
            cb = p.decorator(cb)
        return cb

    return decorator


def parse_params_as(model_type: type[T], params: dict[str, Any]) -> T:
    obj = unnest(model_type, params)
    return model_type.model_validate(obj)


def unnest(model_type: type[T], params: dict[str, Any]) -> dict[str, Any]:
    if is_optional(model_type):
        model_type = optional_type(model_type)
    known_fields: dict[str, FieldInfo] = {}
    for fname, f in model_type.model_fields.items():
        if field_annotation(f, cli.Hidden):
            continue
        known_fields[(f.alias or fname)] = f
    obj: dict[str, Any] = {}
    for k, v in params.items():
        if v is None:
            continue
        if k in known_fields:
            obj[k] = v
        elif "_" in k:
            p, subk = k.split("_", 1)
            try:
                field = known_fields[p]
            except KeyError as e:
                raise ValueError(k) from e
            assert field.annotation is not None
            nested = unnest(field.annotation, {subk: v})
            obj[p] = deep_update(obj.get(p, {}), nested)
        else:
            raise ValueError(k)
    return obj


@dataclass(frozen=True)
class ParamSpec(ABC):
    """Intermediate representation for a future click.Parameter."""

    param_decls: Sequence[str]
    field_info: FieldInfo
    attrs: dict[str, Any]
    loc: tuple[str, ...]
    description: str | None = None

    objtype: ClassVar[type[click.Parameter]] = click.Parameter

    @property
    def param(self) -> click.Parameter:
        return self.objtype(self.param_decls, **self.attrs)

    @property
    @abstractmethod
    def decorator(self) -> ClickDecorator:
        """The click decorator for this parameter."""

    def match_loc(self, loc: tuple[str | int, ...]) -> bool:
        """Return True if this parameter spec matches a 'loc' tuple (from
        pydantic.ValidationError).
        """
        return self.loc == loc

    def badparameter_exception(self, message: str) -> click.BadParameter:
        return click.BadParameter(message, None, param=self.param)


class ArgumentSpec(ParamSpec):
    """Intermediate representation for a future click.Argument."""

    objtype: ClassVar = click.Argument

    def __post_init__(self) -> None:
        assert len(self.param_decls) == 1, (
            f"expecting exactly one parameter declaration: {self.param_decls}"
        )

    @property
    def decorator(self) -> ClickDecorator:
        return click.argument(*self.param_decls, **self.attrs)


class OptionSpec(ParamSpec):
    """Intermediate representation for a future click.Option."""

    objtype: ClassVar = click.Option

    @property
    def decorator(self) -> ClickDecorator:
        return click.option(*self.param_decls, help=self._help(), **self.attrs)

    def _help(self) -> str | None:
        if description := (self.description or self.field_info.description):
            description = description[0].upper() + description[1:]
            if description[-1] not in ".?":
                description += "."
            if self.attrs.get("multiple", False):
                # pytest: (multi-allowed)
                description += " (Can be used multiple times.)"
            return description
        return None


@dataclass(frozen=True)
class _Parent:
    argname: str
    required: bool


def is_editable(ftype: Any) -> bool:
    """Determine whether a given type is considered "editable".

    A type is considered editable if:

    - It is a subclass of pydantic.BaseModel.
    - It has a type hint for a field named "state" of type PresenceState.

    This function also handles types wrapped with typing.Annotated,
    automatically extracting the underlying type for the check.

    >>> class Editable(pydantic.BaseModel):
    ...     state: typing.Annotated[PresenceState, object()]
    >>>
    >>> is_editable(Editable)
    True
    >>> class AlsoEditable(pydantic.BaseModel):
    ...     state: typing.Annotated[typing.Annotated[PresenceState, object()], object()]
    >>>
    >>> is_editable(AlsoEditable)
    True
    >>>
    >>> class EditableNotAnnotated(pydantic.BaseModel):
    ...     state: PresenceState
    >>>
    >>> is_editable(EditableNotAnnotated)
    True
    >>> class NotEditable(pydantic.BaseModel):
    ...     state: typing.Annotated[typing.Annotated[str, object()], object()]
    >>>
    >>> is_editable(NotEditable)
    False
    """
    # Check if there's a "state" field (PresenceState type)
    if typing.get_origin(ftype) is typing.Annotated:
        ftype = typing.get_args(ftype)[0]
        assert ftype is not None
    hints = typing.get_type_hints(ftype)
    return (
        lenient_issubclass(ftype, pydantic.BaseModel)
        and hints.get("state") is PresenceState
    )


def _paramspecs_from_model(
    model_type: ModelType,
    operation: Operation,
    *,
    _parents: tuple[_Parent, ...] = (),
) -> Iterator[tuple[tuple[str, str], ParamSpec]]:
    """Yield parameter declarations for click corresponding to fields of a
    pydantic model type.
    """

    def default(_ctx: click.Context, param: click.Argument, value: Any) -> Any:
        """This function is intended to distinguish parameters that were
        explicitly provided by the user versus those that were omitted (or
        explicitly provided with value equal to the default).

        If the parameter value is unset (or equal to the default value), it
        returns DEFAULT instead of the raw value.
        """
        if (param.multiple and value == ()) or (value == param.default):
            return DEFAULT
        return value

    def add_state_field_callback(
        ctx: click.Context,
        _param: click.Argument,
        value: Any,
        *,
        optname: str,
        key: str = "name",
        remove: bool = False,
    ) -> None:
        """Callback that appends each value to ctx.params[optname] as a dictionary
        with the specified key and a "state" field, set to either "present" or
        "absent" depending on the remove argument.


         Example, --add-user alice --add-user bob --remove-user carol will
         result to:

         ctx.params["user"] = (
                    {"name": "alice", "state": "present"},
                    {"name": "bob", "state": "present"},
                    {"name": "carol", "state": "absent"},
        )
        """
        if optname not in ctx.params:
            ctx.params[optname] = ()
        ctx.params[optname] += tuple(
            {key: v, "state": "absent" if remove else "present"} for v in value
        )
        return

    for fname, field in model_type.model_fields.items():
        if field_annotation(field, cli.Hidden):
            continue
        if (
            operation == "update"
            and isinstance(field.json_schema_extra, dict)
            and field.json_schema_extra.get("readOnly")
        ):
            continue

        modelname = argname = field.alias or fname
        if config := field_annotation(field, cli.Parameter):
            if config.name is not None:
                argname = config.name

        ftype = field.annotation
        assert ftype is not None
        if is_optional(ftype):
            ftype = optional_type(ftype)
        origin_type = typing.get_origin(ftype)
        if origin_type is typing.Annotated:
            ftype = typing.get_args(ftype)[0]
            assert ftype is not None
        required = field.is_required()

        if lenient_issubclass(origin_type or ftype, pydantic.BaseModel):
            yield from _paramspecs_from_model(
                ftype, operation, _parents=_parents + (_Parent(argname, required),)
            )
            continue

        attrs: dict[str, Any] = {}
        if not _parents and required:
            if origin_type is typing.Literal:
                choices = list(typing.get_args(ftype))
                if config is not None:
                    assert isinstance(config, cli.Choices)
                    choices = config.choices
                attrs["type"] = click.Choice(choices)
            if config is not None and isinstance(config, cli.Option):
                attrs["required"] = True
                yield (
                    (modelname, argname),
                    OptionSpec(
                        (f"--{argname.replace('_', '-')}",),
                        field,
                        attrs,
                        loc=(modelname,),
                    ),
                )

            else:
                yield (
                    (modelname, argname),
                    ArgumentSpec(
                        (argname.replace("_", "-"),), field, attrs, loc=(modelname,)
                    ),
                )

        else:
            if (
                config
                and isinstance(config, cli.Argument | cli.Option)
                and config.metavar is not None
            ):
                metavar = config.metavar
            else:
                metavar = argname
            metavar = metavar.upper()
            argparts = tuple(p.argname for p in _parents) + tuple(argname.split("_"))
            argname = "_".join(argparts)
            loc = tuple(p.argname for p in _parents) + (modelname,)
            modelname = "_".join(loc)
            fname = f"--{'-'.join(argparts)}"
            description = field.description

            if required and all(p.required for p in _parents):
                attrs["required"] = True

            if origin_type is typing.Literal:
                choices = list(typing.get_args(ftype))
                if len(choices) == 1:  # const
                    continue
                if config:
                    assert isinstance(config, cli.Choices)
                    choices = config.choices
                attrs["type"] = click.Choice(choices)

            elif lenient_issubclass(origin_type or ftype, list):
                attrs["multiple"] = True
                try:
                    (itemtype,) = ftype.__args__
                except ValueError:
                    pass
                else:
                    attrs["metavar"] = metavar
                if not _parents and operation == "update" and is_editable(itemtype):
                    # List fields for the "update" operation are mapped to
                    # --add-<fname>, --remove-<fname> options; built and yield
                    # directly here.
                    if config is None:
                        continue
                    assert isinstance(config, cli.ListOption)
                    add_argname, remove_argname = config.argnames(argname)
                    add_option, remove_option = config.optnames(fname[2:])
                    add_description, remove_description = config.optdescs(description)
                    yield (
                        (modelname, add_argname),
                        OptionSpec(
                            (add_option,),
                            field,
                            {
                                "callback": functools.partial(
                                    add_state_field_callback,
                                    optname=modelname,
                                    key=config.item_key,
                                ),
                                **attrs,
                            },
                            loc=loc,
                            description=add_description,
                        ),
                    )

                    yield (
                        (modelname, remove_argname),
                        OptionSpec(
                            (remove_option,),
                            field,
                            {
                                "callback": functools.partial(
                                    add_state_field_callback,
                                    optname=modelname,
                                    remove=True,
                                    key=config.item_key,
                                ),
                                **attrs,
                            },
                            loc=loc,
                            description=remove_description,
                        ),
                    )

                    continue

                elif operation != "create":
                    continue

            elif lenient_issubclass(ftype, pydantic.SecretStr):
                attrs["prompt"] = (
                    field.description.rstrip(".")
                    if field.description is not None
                    else True
                )
                attrs["prompt_required"] = False
                attrs["confirmation_prompt"] = True
                attrs["hide_input"] = True
                attrs["metavar"] = metavar

            elif lenient_issubclass(ftype, bool):
                fname = f"{fname}/--no-{fname[2:]}"
                # Use None to distinguish unspecified option from the default value.
                attrs["default"] = None

            else:
                attrs["metavar"] = metavar

            yield (
                (modelname, argname),
                OptionSpec(
                    (fname,),
                    field,
                    {"callback": default, **attrs},
                    loc=loc,
                    description=description,
                ),
            )


def fieldname_and_options(*paramspec: ParamSpec) -> dict[str, str]:
    """Return a mapping between model field name and corresponding CLI options."""
    r: dict[str, str] = {}
    for pspec in paramspec:
        param = pspec.param
        assert param.name
        r[param.name] = ", ".join(param.opts)
    return r


def format_error_message(error: ErrorDetails, *paramspec: ParamSpec) -> str:
    """Format templated error message"""
    try:
        ctx_error = error["ctx"]["error"]
    except KeyError:
        return error["msg"]
    if isinstance(ctx_error, MutuallyExclusiveError):
        options = fieldname_and_options(*paramspec)
        return ctx_error.format(options)
    return str(ctx_error)


@contextmanager
def catch_validationerror(*paramspec: ParamSpec) -> Iterator[None]:
    try:
        yield None
    except pydantic.ValidationError as e:
        errors = e.errors()
        for err in errors:
            if not err.get("loc"):
                raise click.UsageError(format_error_message(err, *paramspec)) from None
        for pspec in paramspec:
            for err in errors:
                if pspec.match_loc(err["loc"]):
                    raise pspec.badparameter_exception(
                        format_error_message(err, *paramspec)
                    ) from None
        logger.debug("a validation error occurred", exc_info=True)
        raise click.ClickException(str(e)) from None
