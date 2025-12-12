#  SPDX-FileCopyrightText: © 2024 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
Low-level utils related to syncing.
"""
import asyncio
import threading
import uuid


def run_coroutine_in_new_thread(coro, *, thread_name: str | None = None, thread_name_postfix: str | None = None):
    """
    Run a coroutine in a new thread and return its result or forward its exception.

    :param coro: The coroutine to run.
    :param thread_name: Optional thread name.
    :param thread_name_postfix: Optional thread name postfix to append to the current thread name.
    """
    if not thread_name:
        if not thread_name_postfix:
            thread_name_postfix = str(uuid.uuid4())
        thread_name = f"{threading.current_thread().name} > {thread_name_postfix}"

    result = [None, None]
    thread = threading.Thread(target=__run_coroutine_in_new_thread__run, args=(coro, result), name=thread_name)
    thread.start()
    thread.join()
    if result[1]:
        raise result[1]  # pylint: disable=raising-bad-type
    return result[0]


def __run_coroutine_in_new_thread__run(coro, result) -> None:
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result[0] = loop.run_until_complete(coro)
    except Exception as ex:  # pylint: disable=broad-exception-caught
        result[1] = ex
