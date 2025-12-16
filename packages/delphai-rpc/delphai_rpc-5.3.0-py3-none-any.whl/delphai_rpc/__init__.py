import asyncio
import logging
import signal
import typing

from .client import RpcClient
from .models import Options, RpcCall
from .queue_client import QueueClient
from .server import RpcServer
from .workflow import RpcWorkflow

__all__ = ["Options", "Rpc", "RpcCall", "run_forever"]

logger = logging.getLogger(__name__)


class Rpc:
    def __init__(self, service_name: str, connection_string: str) -> None:
        self._connection_string = connection_string
        self._queue_client = QueueClient(service_name, self._connection_string)

        self.client = RpcClient(self._queue_client)
        self.server = RpcServer(self._queue_client)
        self.workflow = RpcWorkflow(self._queue_client)

        self._servers: dict[str, RpcServer] = {
            service_name: self.server,
        }

    async def run(self) -> None:
        if not self._connection_string:
            logger.warning(
                "RPC hasn't been run because `connection_string` is undefined."
                "Pass a non-empty `connection_string` while initializing."
            )
            await asyncio.Future()
            return

        for server in self._servers.values():
            await server.start()

        await self.workflow.start()

        try:
            await asyncio.Future()
        finally:
            await self._queue_client.stop()

    def get_server(self, service_name: str) -> RpcServer:
        server = self._servers.get(service_name)
        if not server:
            self._servers[service_name] = RpcServer(
                self._queue_client,
                service_name=service_name,
            )

        return self._servers[service_name]


class _ShutdownError(Exception): ...


async def run_forever(*coros: typing.Coroutine) -> None:
    loop = asyncio.get_running_loop()
    signal_event = asyncio.Event()

    for signum in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(signum, signal_event.set)

    async def wait_shutdown() -> None:
        await signal_event.wait()

        for signum in (signal.SIGINT, signal.SIGTERM):
            loop.remove_signal_handler(signum)

        raise _ShutdownError

    try:
        async with asyncio.TaskGroup() as task_group:
            task_group.create_task(wait_shutdown())
            [task_group.create_task(coro) for coro in coros]
    except* _ShutdownError:
        pass
