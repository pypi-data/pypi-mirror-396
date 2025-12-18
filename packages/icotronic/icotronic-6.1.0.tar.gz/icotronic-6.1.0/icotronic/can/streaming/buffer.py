"""Support for streaming (measurement) data in the ICOtronic system"""

# -- Imports ------------------------------------------------------------------

from __future__ import annotations

from asyncio import Queue, wait_for
from collections.abc import AsyncIterator
from time import time

from can import Listener, Message

from icotronic.can.protocol.identifier import Identifier
from icotronic.can.dataloss import MessageStats
from icotronic.can.streaming.error import (
    StreamingBufferError,
    StreamingTimeoutError,
)
from icotronic.can.streaming.data import StreamingData

# -- Classes ------------------------------------------------------------------


class AsyncStreamBuffer(Listener):
    """Buffer for streaming data

    Args:

        timeout:
            The amount of seconds between two consecutive messages, before
            a ``StreamingTimeoutError`` will be raised

        max_buffer_size:
            Maximum amount of buffered messages kept by the stream buffer.
            If this amount is exceeded, then this listener will raise a
            ``StreamingBufferError``. A large buffer indicates that the
            application is not able to keep up with the current rate of
            retrieved messages and therefore the probability of losing
            messages is quite high.

    """

    def __init__(
        self,
        timeout: float,
        max_buffer_size: int,
    ) -> None:

        # Expected identifier of received streaming messages
        self.identifier = Identifier(
            block="Streaming",
            block_command="Data",
            sender="STH 1",
            receiver="SPU 1",
            request=False,
        )
        self.queue: Queue[tuple[StreamingData, int]] = Queue()
        self.timeout = timeout
        self.last_counter = -1
        self.max_buffer_size = max_buffer_size
        self.stats = MessageStats()
        self.timestamp_offset: float | None = None

    def __aiter__(self) -> AsyncIterator[tuple[StreamingData, int]]:
        """Retrieve iterator for collected data

        Returns:

            An iterator over the received streaming data including the number
            of lost messages

        """

        return self

    async def __anext__(self) -> tuple[StreamingData, int]:
        """Retrieve next stream data object in collected data

        Returns:

            A tuple containing:

            - the data of the streaming message and
            - the number of lost streaming messages right before the returned
              streaming message

        """

        if self.queue.qsize() > self.max_buffer_size:
            raise StreamingBufferError(
                f"Maximum buffer size of {self.max_buffer_size} messages "
                "exceeded"
            )

        try:
            return await wait_for(self.queue.get(), self.timeout)
        except TimeoutError as error:
            raise StreamingTimeoutError(
                f"No data received for at least {self.timeout} seconds"
            ) from error

    def on_message_received(self, msg: Message) -> None:
        """Handle received messages

        Args:

            msg:
                The received CAN message

        """

        # Ignore messages with wrong id and “Stop Stream” messages
        if msg.arbitration_id != self.identifier.value or len(msg.data) <= 1:
            return

        receive_time = time()

        # Calculate timestamp offset for first received message
        if self.timestamp_offset is None:
            self.timestamp_offset = receive_time - msg.timestamp

        data = msg.data
        counter = data[1]
        timestamp = msg.timestamp + self.timestamp_offset
        data_bytes = (
            data[start : start + 2] for start in range(2, len(data) - 1, 2)
        )

        values: list[float] = [
            int.from_bytes(word, byteorder="little") for word in data_bytes
        ]
        assert len(values) == 2 or len(values) == 3

        streaming_data = StreamingData(
            timestamp=timestamp,
            counter=counter,
            values=values,
        )

        # Calculate amount of lost messages
        if self.last_counter < 0:
            self.last_counter = (counter - 1) % 256
        last_counter = self.last_counter
        lost_messages = (counter - last_counter) % 256 - 1
        self.last_counter = counter
        self.stats.lost += lost_messages
        self.stats.retrieved += 1

        self.queue.put_nowait((streaming_data, lost_messages))

    def on_error(self, exc: Exception) -> None:
        """This method is called to handle any exception in the receive thread.

        Args:

            exc:
                The exception causing the thread to stop

        """

        raise NotImplementedError()

    def stop(self) -> None:
        """Stop handling new messages"""

    def reset_stats(self) -> None:
        """Reset the message statistics

        This method resets the amount of lost an retrieved messages used in
        the calculation of the method ``dataloss``. Using this method can be
        useful, if you want to calculate the amount of data loss since a
        specific starting point.

        """

        self.stats.reset()

    def dataloss(self) -> float:
        """Calculate the overall amount of data loss

        Returns:

            The overall amount of data loss as number between 0 (no data loss)
            and 1 (all data lost).

        """

        return self.stats.dataloss()


# -- Main ---------------------------------------------------------------------

if __name__ == "__main__":
    from doctest import testmod

    testmod()
