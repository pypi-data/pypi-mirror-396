#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
See :py:class:`Backend`.
"""
import pathlib

import parzzley.builtin.fs
import parzzley.fs


@parzzley.fs.register_backend
class Backend(parzzley.builtin.fs.ShellBasedBackend):
    """
    ssh filesystem backend implementation.
    """

    def _shell(self, **kwargs):
        return Backend._Shell(**kwargs)

    class _Shell(parzzley.builtin.fs.ShellBasedBackend.Shell):

        def __init__(
            self, *, host: str, port: int = 22, user: str, id_file: pathlib.Path, skip_host_key_check: bool = False
        ):
            super().__init__()
            self.__host = host
            self.__port = int(port)
            self.__user = user
            self.__id_file = pathlib.Path(id_file)
            self.__skip_host_key_check = skip_host_key_check

        def _shell_cmdline(self):
            args = ("-oServerAliveInterval=50", "-oConnectTimeout=20")

            if self.__skip_host_key_check:
                args = (
                    *args,
                    "-oStrictHostKeyChecking=no",
                    "-oUserKnownHostsFile=/dev/null",
                    "-oGlobalKnownHostsFile=/dev/null",
                )

            return "ssh", *args, f"-p{self.__port}", "-i", self.__id_file, "-T", f"{self.__user}@{self.__host}", "sh"
