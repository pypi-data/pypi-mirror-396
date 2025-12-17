import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator, NoReturn, TypeVar

T = TypeVar("T")


async def timeout(seconds: float) -> NoReturn:
    """Wait for timeout duration before raising TimeoutError."""
    await asyncio.sleep(seconds)
    raise TimeoutError


@asynccontextmanager
async def task_context(
    tasks: list[asyncio.Task[T]],
) -> AsyncGenerator[list[asyncio.Task[T]], None]:
    """
    Context manager that:
    - ensures tasks are cancelled on exit (e.g. exception, return, etc.)
    - waits for all tasks to complete
    """
    try:
        yield tasks
    finally:
        # Cancel any tasks that are still running
        for task in tasks:
            if not task.done():
                task.cancel()

        # Wait for all tasks to complete
        await asyncio.gather(*tasks, return_exceptions=True)
