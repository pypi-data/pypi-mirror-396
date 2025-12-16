import asyncio
import pathlib
import threading
from typing import Callable

from snorkelai.sdk.utils.logging import get_logger

logger = get_logger("Snorkel SDK context")


class FileWatcher:
    def __init__(self, file: pathlib.Path, callback: Callable[[str], None]) -> None:
        self.loop = asyncio.new_event_loop()
        self.event: threading.Event = threading.Event()
        self.thread = threading.Thread(
            name=f"{file} file watcher",
            target=self.loop.run_forever,
            daemon=False,
        )
        self.thread.start()
        self.task = asyncio.run_coroutine_threadsafe(
            self.__watch__(file=file, event=self.event, callback=callback), self.loop
        )
        self.task.add_done_callback(lambda _: self.loop.stop())

    async def __watch__(
        self,
        file: pathlib.Path,
        event: threading.Event,
        callback: Callable[[str], None],
    ) -> None:
        try:
            from watchfiles import Change, awatch

            async for changes in awatch(file.parent, recursive=False, stop_event=event):
                logger.info(f"watcher event: {changes}")
                if str(file) in {
                    change[1] for change in changes if change[0] != Change.deleted
                }:
                    result = file.read_text().rstrip()
                    logger.info("watched file updated")
                    callback(result)
            logger.info("exiting watcher")
        except ImportError:
            logger.info(
                "watchfiles package not available, not watching for api_key changes"
            )
        except asyncio.CancelledError:
            logger.exception("watcher cancelled")

    def __del__(self) -> None:
        self.event.set()
        self.thread.join(timeout=30)
