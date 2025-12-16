import collections
import threading

import numpy
from numpy.typing import NDArray


class RingBuffer:
    def __init__(self, maxlen: int, element_size: int = 1) -> None:
        self.maxlen = maxlen
        self.element_size = element_size

        self.lock = threading.Lock()

        self.length = 0
        self.index = 0

        shape = (maxlen, element_size)
        self.data: NDArray[numpy.float64] = numpy.empty(
            shape, dtype=numpy.float64)

        # NOTE: maxlen isn't quite right, because the deque stores chunks, not
        # elements. But there can never be more than maxlen chunks of useful
        # data, so it is sufficient to prevent unbounded memory growth
        self.pending: collections.deque[NDArray[numpy.float64]] = \
            collections.deque(maxlen=maxlen)

    def _handle_pending(self) -> None:
        pass

    def __len__(self) -> int:
        with self.lock:
            return self.length

    def clear(self) -> None:
        with self.lock:
            self.length = 0
            self.index = 0

    def get_contents(self) -> NDArray[numpy.float64]:
        with self.lock:
            return self.data[0:self.length]

    def append(self, value: NDArray[numpy.float64]) -> None:
        with self.lock:
            self.data[self.index] = value
            self.index += 1
            self.length += 1
            if self.length == self.maxlen:
                self.index = 0
                self.__class__ = RingBufferFull  # pyright: ignore

    def extend(self, array: NDArray[numpy.float64]) -> None:
        with self.lock:
            if len(array) >= self.maxlen:
                # oddball case, fill the entire buffer with the array end
                self.data = array[-self.maxlen:]
                self.index = 0
                self.length = self.maxlen
                self.pending.clear()  # address an unlikely race
                self.__class__ = RingBufferFull  # pyright: ignore
            elif len(array) + self.index >= self.maxlen:
                end_length = self.maxlen - self.index
                start_length = len(array) - end_length
                self.data[self.index:] = array[0:end_length]
                self.data[0:start_length] = array[end_length:]
                self.index = start_length
                self.length = self.maxlen
                self.pending.clear()  # address an unlikely race with clear
                self.__class__ = RingBufferFull  # pyright: ignore
            else:
                self.data[self.index:self.index + len(array)] = array
                self.length += len(array)
                self.index = self.length


class RingBufferFull(RingBuffer):
    def _handle_pending(self) -> None:
        if self.pending:
            array = numpy.concatenate(self.pending)
            self.pending.clear()
            if len(array) + self.index > self.maxlen:
                if len(array) >= self.maxlen:
                    # oddball case, fill the entire buffer with the array end
                    self.data = array[-self.maxlen:]
                    self.index = 0
                else:
                    end_length = self.maxlen - self.index
                    start_length = len(array) - end_length
                    self.data[self.index:] = array[0:end_length]
                    self.data[0:start_length] = array[end_length:]
                    self.index = start_length
            else:
                self.data[self.index:self.index + len(array)] = array
                self.index += len(array)

    def clear(self) -> None:
        with self.lock:
            self.pending.clear()
            self.length = 0
            self.index = 0
            self.__class__ = RingBuffer  # type: ignore

    def get_contents(self) -> NDArray[numpy.float64]:
        with self.lock:
            self._handle_pending()
            return numpy.roll(self.data, -self.index, axis=0)

    def append(self, value: NDArray[numpy.float64]) -> None:
        with self.lock:
            self.data[self.index] = value
            self.index += 1
            if self.index == self.maxlen:
                self.index = 0

    def extend(self, array: NDArray[numpy.float64]) -> None:
        with self.lock:
            self.pending.append(array)
