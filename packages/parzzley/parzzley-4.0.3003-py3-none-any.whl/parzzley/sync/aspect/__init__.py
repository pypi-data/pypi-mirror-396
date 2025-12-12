#  SPDX-FileCopyrightText: © 2024 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
Aspect API. See :py:class:`Aspect`.
"""
import functools
import inspect
import typing as t

import parzzley.sync.aspect.events.item.dir
import parzzley.sync.aspect.events.item.stream
import parzzley.sync.aspect.events.sync_run
import parzzley.sync.aspect.only_if


class Aspect:
    """
    Aspects are plugins for the Parzzley sync engine. The engine itself does not much more than hosting and controlling
    these aspects. All visible effects from a sync run (i.e. all its actual duties) are realized by aspects; not by the
    engine itself.

    A typical aspect is a subclass of :py:class:`Aspect` that includes some event handlers.
    See also :py:func:`event_handler` and :py:mod:`parzzley.sync.aspect.events` for more details.
    """

    def __init__(self, *inner_aspects: "Aspect"):
        self.__inner_aspects = tuple(inner_aspects)

    def _all_event_handlers(self):
        result = []

        for aspect_subclass in type(self).mro():
            for aspect_attr_name in aspect_subclass.__dict__:
                aspect_attr = getattr(aspect_subclass, aspect_attr_name)
                aspect_attr_event_handler_spec = getattr(aspect_attr, "_parzzley_aspect_event_handler_for", None)

                if aspect_attr_event_handler_spec:
                    func_args = [
                        x
                        for x in inspect.signature(aspect_attr).parameters.values()
                        if x.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD
                    ]
                    if len(func_args) > 1 and func_args[1].annotation:

                        conditions, more_names, *dependencies = aspect_attr_event_handler_spec
                        result.append(
                            (
                                functools.partial(aspect_attr, self),
                                conditions,
                                func_args[1].annotation,
                                [aspect_attr.__qualname__, *more_names],
                                *dependencies,
                            )
                        )

        for aspect in self.__inner_aspects:
            result.extend(aspect._all_event_handlers())

        return tuple(result)


_TDependency = str | t.Callable


def event_handler(
    *conditions,
    more_names: t.Iterable[str] = (),
    beforehand: t.Iterable[_TDependency] = (),
    beforehand_optional: t.Iterable[_TDependency] = (),
    afterwards: t.Iterable[_TDependency] = (),
    afterwards_optional: t.Iterable[_TDependency] = ()
):
    """
    Decorate an aspect method to be an event handler.

    :param conditions: Conditions that need to be satisfied for execution. See :py:mod:`parzzley.sync.aspect.only_if`.
    :param more_names: Additional names of this event handler. Used for dependency specification together with the
                       following parameters.
    :param beforehand: Event handlers that must be executed before this one.
    :param beforehand_optional: Event handlers that must be executed before this one if they exist.
    :param afterwards: Event handlers that must be executed after this one.
    :param afterwards_optional: Event handlers that must be executed after this one if they exist.
    """

    def decorator(func_):
        func_._parzzley_aspect_event_handler_for = (
            conditions,
            tuple(more_names),
            _dep_list(beforehand),
            _dep_list(beforehand_optional),
            _dep_list(afterwards),
            _dep_list(afterwards_optional),
        )
        return func_

    return decorator


def _dep_str(dep: _TDependency) -> str:
    return dep if isinstance(dep, str) else dep.__qualname__


def _dep_list(orig_list: t.Iterable[_TDependency]) -> t.Sequence[str]:
    return tuple(_dep_str(dep) for dep in orig_list)


_registered_aspects = {}


def register_aspect(aspect_type: type[Aspect]) -> type[Aspect]:
    """
    Make an aspect class available to be used, e.g. in volume configurations.

    :param aspect_type: The aspect class to register.
    """
    _registered_aspects[aspect_type.__name__] = aspect_type
    return aspect_type


def aspect_type_by_name(name: str) -> type[Aspect] | None:
    """
    Return an aspect type by the type name.

    :param name: The aspect type name.
    """
    return _registered_aspects.get(name)
