#  SPDX-FileCopyrightText: © 2024 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
Event runner. See :py:class:`Runner`.
"""
import asyncio
import dataclasses
import typing as t

import parzzley.sync.aspect.events


class Runner:
    """
    Event runner.

    This is a helper class used internally by the engine in order to run events (in particular, to execute event
    handlers registered by the configured aspects).
    """

    class _DependencyControlledHandlerCollection:
        """
        Collection of event handler nodes and some operations on it that allow to execute them in an order that obeys
        their dependencies.
        """

        def __init__(self, handler_nodes: list["Runner._HandlerNode"]):
            """
            :param handler_nodes: The event handler nodes.
            """
            self.__handler_nodes = handler_nodes
            self.__open_dependencies = {node: {n.handler for n in node.depends_on_handlers} for node in handler_nodes}
            self.__returned: set["Runner._Handler"] = set()

        @property
        def is_empty(self) -> bool:
            """
            Whether this collection is empty.
            """
            return len(self.__handler_nodes) == 0

        def available_nodes(self) -> t.Iterable["Runner._Handler"]:
            """
            Return all handler nodes that are available for execution and not marked as done yet.
            """
            avail = [node.handler for node in self.__handler_nodes if len(self.__open_dependencies[node]) == 0]
            result = [handler for handler in avail if handler not in self.__returned]
            self.__returned.update(result)
            return result

        def mark_done(self, *handlers: "Runner._Handler") -> None:
            """
            Mark some handler nodes as done.

            :param handlers: The handler nodes.
            """
            handlers_to_remove = set(handlers)
            for i_stored_node, stored_node in reversed(list(enumerate(self.__handler_nodes))):
                if stored_node.handler in handlers_to_remove:
                    self.__handler_nodes.pop(i_stored_node)
            for stored_node in self.__handler_nodes:
                self.__open_dependencies[stored_node] = self.__open_dependencies[stored_node] - handlers_to_remove

    @dataclasses.dataclass(eq=False)
    class _Handler:
        func: t.Callable[["parzzley.sync.aspect.events._Event"], None]
        site: "parzzley.fs.Site"
        conditions: t.Iterable["parzzley.sync.aspect.only_if.Condition"]
        event_type: type["parzzley.sync.aspect.events._Event"]
        names: t.Iterable[str]
        beforehand: t.Iterable[str]
        beforehand_optional: t.Iterable[str]
        afterwards: t.Iterable[str]
        afterwards_optional: t.Iterable[str]

    @dataclasses.dataclass(eq=False)
    class _HandlerNode:
        handler: "Runner._Handler"
        depends_on_handlers: list["Runner._HandlerNode"]

    def __init__(self, aspects: dict["parzzley.fs.Site", t.Iterable["parzzley.sync.aspect.Aspect"]]):
        self.__aspects = aspects
        self.__all_handler_nodes__cache = None

    async def run_event(
        self, event_type: type["parzzley.sync.aspect.events._Event"], event: "parzzley.sync.aspect.events._Event"
    ) -> None:
        """
        Run an event.

        :param event_type: The event type.
        :param event: The event instance.
        """
        handler_collection = self.__handlers_for_event_type(event_type)

        while not handler_collection.is_empty:
            nods = handler_collection.available_nodes()
            coroutines = []
            handler_collection.mark_done(*nods)
            for event_handler in nods:
                event_with_location = event.to_event_for_site(event_handler.site)

                is_met = True
                for condition in event_handler.conditions:
                    if not condition.is_met(event_with_location):
                        is_met = False
                        break
                if not is_met:
                    continue

                coroutines.append(event_handler.func(event_with_location))
            await asyncio.gather(*coroutines)

    def __handlers_for_event_type(
        self, event_type: type[parzzley.sync.aspect.events._Event]
    ) -> "_DependencyControlledHandlerCollection":
        return self._DependencyControlledHandlerCollection(
            [h for h in self.__all_handler_nodes() if h.handler.event_type is event_type]
        )

    def __all_handler_nodes(self) -> t.Sequence["Runner._HandlerNode"]:
        if self.__all_handler_nodes__cache is None:
            all_handlers = []

            for site, aspects in self.__aspects.items():
                for aspect in aspects:
                    for handler_tuple in aspect._all_event_handlers():
                        all_handlers.append(self._Handler(handler_tuple[0], site, *handler_tuple[1:]))
            all_handlers.sort(key=lambda h: tuple(h.names))

            handler_nodes: list[Runner._HandlerNode] = []
            handler_nodes_by_name: dict[str, list[Runner._HandlerNode]] = {}
            for handler in all_handlers:
                node = Runner._HandlerNode(handler, [])
                handler_nodes.append(node)
                for name in handler.names:
                    list_for_name = handler_nodes_by_name[name] = handler_nodes_by_name.get(name) or []
                    list_for_name.append(node)

            for handler_node in handler_nodes:
                self.__all_handler_nodes__find_dependencies(handler_node, handler_nodes_by_name)

            self.__all_handler_nodes__cache = handler_nodes

        return self.__all_handler_nodes__cache

    def __all_handler_nodes__find_dependencies(self, handler_node, handler_nodes_by_name) -> None:
        for d in handler_node.handler.beforehand:
            dns = handler_nodes_by_name.get(d) or ()
            if len(dns) == 0:
                raise RuntimeError(f"not met: {d}")
            for dn in dns:
                handler_node.depends_on_handlers.append(dn)

        for d in handler_node.handler.beforehand_optional:
            dns = handler_nodes_by_name.get(d) or ()
            for dn in dns:
                handler_node.depends_on_handlers.append(dn)

        for d in handler_node.handler.afterwards:
            dns = handler_nodes_by_name.get(d) or ()
            if len(dns) == 0:
                raise RuntimeError(f"not met: {d}")
            for dn in dns:
                dn.depends_on_handlers.append(handler_node)

        for d in handler_node.handler.afterwards_optional:
            dns = handler_nodes_by_name.get(d) or ()
            for dn in dns:
                dn.depends_on_handlers.append(handler_node)
