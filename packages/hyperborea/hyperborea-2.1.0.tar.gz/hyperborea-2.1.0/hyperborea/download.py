import logging
import threading
from typing import Any, BinaryIO
import urllib.parse

from PySide6 import QtCore
from packaging.version import InvalidVersion, Version, parse
import requests

Logger = logging.Logger | logging.LoggerAdapter[logging.Logger]


def ref_sort_key(value: str) -> tuple[bool, Version | str]:
    try:
        return (True, parse(value))
    except InvalidVersion:
        return (False, value)


class _Fetcher(QtCore.QObject):
    completed = QtCore.Signal(object, object)
    error = QtCore.Signal(str)

    def __init__(self, logger: Logger, extra: Any | None = None):
        super().__init__()
        self.logger = logger
        self.extra = extra

    def start(self, url: str, log_type: str) -> None:
        self.request_thread = threading.Thread(
            target=self.request_thread_run, args=(url, log_type))
        self.request_thread.start()

    def request_thread_run(self, url: str, log_type: str) -> None:
        try:
            self.logger.debug("Requesting %s from url %s", log_type, url)
            response = requests.get(url)

            if not response.ok:
                self.logger.error("Error requesting %s: %s", log_type,
                                  response.text)
                self.error.emit(f"Error requesting {log_type}!")
                return

            data = response.json()

            if not data:
                self.logger.error("Empty response for %s request!", log_type)
                self.error.emit(f"Error requesting {log_type}!")
                return

            self.completed.emit(data, self.extra)
        except Exception:
            self.logger.exception('Error requesting %s', log_type)
            self.error.emit(f"Error requesting {log_type}!")


class FirmwareFinder(QtCore.QObject):
    completed = QtCore.Signal(object)
    error = QtCore.Signal(str)

    def __init__(self, logger: Logger):
        super().__init__()
        self.logger = logger

    def find_firmware(self, build_type: str | None,
                      board_info: tuple[str, int] | None = None,
                      repo: str | None = None,
                      branch: str | None = None,
                      commit: str | None = None) -> None:
        keys: list[str] = []
        # need either board_info or repo, but not both
        if board_info:
            if repo:
                raise ValueError("Cannot specify both board_info and repo")
            else:
                board_name, board_rev = board_info
                keys.append("boardname={}".format(
                    urllib.parse.quote(board_name)))
                keys.append("boardrev={}".format(board_rev))
        else:
            if repo:
                keys.append("repo={}".format(urllib.parse.quote(repo)))
            else:
                raise ValueError("Must specify one of board_info or repo")

        # need at most one of branch and commit
        if commit and branch:
            raise ValueError("Cannot specify both commit and branch")
        elif commit is not None:
            keys.append("hash={}".format(commit))
        elif branch is not None:
            keys.append("branch={}".format(branch))

        base_url = "https://api.suprocktech.com/firmwareinfo/findfirmware"
        url = base_url + "?" + "&".join(keys)

        self.fetcher = _Fetcher(self.logger, build_type)
        self.fetcher.error.connect(self.error)
        self.fetcher.completed.connect(self.got_data)
        self.fetcher.start(url, "findfirmware")

    @QtCore.Slot(object, object)
    def got_data(self, build_urls: dict[str, Any],
                 build_type: str | None) -> None:
        try:
            if build_type is not None and build_type in build_urls:
                build_urls = {build_type: build_urls[build_type]}
            self.completed.emit(build_urls)
        except Exception:
            self.logger.exception('Error finding firmware')
            self.error.emit('Unknown error finding firmware!')


class SoftwareFinder(QtCore.QObject):
    completed = QtCore.Signal(object)
    error = QtCore.Signal(str)

    def __init__(self, logger: Logger):
        super().__init__()
        self.logger = logger

    def find_software(self, repo: str,
                      build_key: str,
                      branch: str | None = None,
                      commit: str | None = None) -> None:
        base_url = "https://api.suprocktech.com/software/findsoftware"
        keys = ["repo={}".format(repo), "key={}".format(build_key)]
        if commit:
            keys.append("hash={}".format(commit))
        if branch:
            keys.append("branch={}".format(branch))

        url = base_url + "?" + "&".join(keys)

        self.fetcher = _Fetcher(self.logger)
        self.fetcher.error.connect(self.error)
        self.fetcher.completed.connect(self.got_data)
        self.fetcher.start(url, "findsoftware")

    @QtCore.Slot(object)
    def got_data(self, values: dict[str, Any]) -> None:
        try:
            if "url" not in values:
                self.logger.error("Empty response to findsoftware!")
                self.error.emit("Error requesting software information!")
                return

            url = values['url']
            commit = values.get('commit', None)
            state = values.get('state', "SUCCESSFUL")
            ready = (state == "SUCCESSFUL")

            self.completed.emit((url, commit, ready))
        except Exception:
            self.logger.exception('Error finding software')
            self.error.emit("Unknown error finding software!")


class RefFinder(QtCore.QObject):
    completed = QtCore.Signal(object)
    error = QtCore.Signal(str)

    def __init__(self, logger: Logger):
        super().__init__()
        self.logger = logger

        self.fetcher = _Fetcher(self.logger)
        self.fetcher.error.connect(self.error)
        self.fetcher.completed.connect(self.completed)

    def get_software_refs(self, repo: str) -> None:
        base_url = "https://api.suprocktech.com/software/findsoftware"
        keys = ["repo={}".format(repo), "listrefs=1"]

        url = base_url + "?" + "&".join(keys)

        self.fetcher.start(url, "listrefs")

    def get_firmware_refs(self, board_info: tuple[str, int] | None = None,
                          repo: str | None = None) -> None:
        keys = ["listrefs=1"]
        # need either board_info or repo, but not both
        if board_info:
            if repo:
                raise ValueError("Cannot specify both board_info and repo")
            else:
                board_name, board_rev = board_info
                keys.append("boardname={}".format(
                    urllib.parse.quote(board_name)))
                keys.append("boardrev={}".format(board_rev))
        else:
            if repo:
                keys.append("repo={}".format(urllib.parse.quote(repo)))
            else:
                raise ValueError("Must specify one of board_info or repo")

        base_url = "https://api.suprocktech.com/firmwareinfo/findfirmware"
        url = base_url + "?" + "&".join(keys)

        self.fetcher.start(url, "listrefs")


class Downloader(QtCore.QObject):
    update = QtCore.Signal(int, int)  # read_bytes, total_bytes
    completed = QtCore.Signal(str, object)  # url, file
    error = QtCore.Signal(object, str)  # file, err

    def __init__(self, logger: Logger):
        super().__init__()
        self.logger = logger

    def start_download(self, url: str, file: BinaryIO) -> None:
        self.download_thread = threading.Thread(
            target=self.download_thread_run, args=(url, file))
        self.download_thread.start()

    def download_thread_run(self, url: str, file: BinaryIO) -> None:
        try:
            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                total_length_str = r.headers.get('content-length')
                written_bytes = 0
                if total_length_str:
                    try:
                        total_length = int(total_length_str)
                    except ValueError:
                        total_length = 0
                else:
                    total_length = 0

                for chunk in r.iter_content(chunk_size=4096):
                    if chunk:
                        file.write(chunk)
                        written_bytes += len(chunk)
                        self.update.emit(written_bytes, total_length)
                self.completed.emit(url, file)
        except Exception:
            self.logger.exception('Error downloading file')
            self.error.emit(file, 'Error downloading file')
