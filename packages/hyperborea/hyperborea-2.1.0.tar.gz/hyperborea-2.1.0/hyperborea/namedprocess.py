import logging
import multiprocessing.spawn
import os
import sys
import threading
from typing import Any

try:
    import setproctitle
except ModuleNotFoundError:
    setproctitle = None  # type: ignore


logger = logging.getLogger(__name__)

lock = threading.Lock()


if sys.platform == 'win32':
    class NamedProcess(multiprocessing.Process):
        def __init__(self, name: str, description: str, **kwargs: Any):
            self.title = f"{name} {description}"
            with lock:
                original_name = multiprocessing.spawn.get_executable()

            new_name = os.path.abspath(os.path.join(
                os.path.dirname(original_name), name + ".exe"))

            self.executable: str | None
            if os.path.isfile(new_name):
                self.executable = new_name
            else:
                self.executable = None

            super().__init__(name=name, **kwargs)

        def start(self) -> None:
            if self.executable:
                with lock:
                    old_name = multiprocessing.spawn.get_executable()
                    try:
                        multiprocessing.spawn.set_executable(self.executable)
                        super().start()
                    finally:
                        multiprocessing.spawn.set_executable(old_name)
            else:
                super().start()

        def run(self) -> None:
            if setproctitle:
                setproctitle.setproctitle(self.title)
            super().run()
else:
    class NamedProcess(multiprocessing.Process):
        def __init__(self, name: str, description: str, **kwargs):
            self.title = f"{name} {description}"
            super().__init__(name=name, **kwargs)

        def run(self) -> None:
            if setproctitle:
                setproctitle.setproctitle(self.title)
            super().run()
