"""Data formats for storing streaming data"""

# -- Imports ------------------------------------------------------------------

from __future__ import annotations

from collections.abc import Callable

# -- Classes ------------------------------------------------------------------


class StreamingData:
    """Support for storing data of a streaming message

    Args:

        counter:
            The message counter value

        timestamp:
            The message timestamp

        values:
            The streaming values

    Examples:

        Create new streaming data

        >>> StreamingData(values=[1, 2, 3], counter=21, timestamp=1)
        [1, 2, 3]@1 #21

        Streaming data must store either two or three values

        >>> StreamingData(values=[1], counter=21, timestamp=1)
        Traceback (most recent call last):
        ...
        ValueError: Incorrect number of streaming values: 1 (instead of 2 or 3)

        >>> StreamingData(values=[1, 2, 3, 4], counter=21, timestamp=1
        ...              ) # doctest:+ELLIPSIS
        Traceback (most recent call last):
        ...
        ValueError: Incorrect number of ... values: 4 (instead of 2 or 3)

    """

    def __init__(
        self, counter: int, timestamp: float, values: list[float]
    ) -> None:

        if not 2 <= len(values) <= 3:
            raise ValueError(
                f"Incorrect number of streaming values: {len(values)} "
                "(instead of 2 or 3)"
            )

        self.counter = counter
        self.timestamp = timestamp
        self.values = values

    def apply(
        self,
        function: Callable[[float], float],
    ) -> StreamingData:
        """Apply a certain function to the streaming data

        Note:

            This function changes the stored values in the streaming data and
            (as convenience feature) also returns the modified streaming data
            itself. This is useful if you want to use the modified streaming
            as parameter in a function call, i.e. you can use something like
            ``function(stream_data.apply())``.

        Args:

            function:
                The function that should be applied to the streaming data

        Returns:

            The modified streaming data

        Examples:

            Add the constant 10 to some example streaming data

            >>> data = StreamingData(values=[1, 2, 3], counter=21, timestamp=1)
            >>> data.apply(lambda value: value + 10)
            [11, 12, 13]@1 #21
            >>> data.values
            [11, 12, 13]

        """

        updated_values = [function(value) for value in self.values]
        assert len(updated_values) == 2 or len(updated_values) == 3
        self.values = updated_values

        return self

    def __repr__(self):
        """Get the string representation of the stream data

        Examples:

            Get the string representation of some streaming data

            >>> StreamingData(values=[1, 2, 3], counter=21, timestamp=1)
            [1, 2, 3]@1 #21

        """

        return f"{self.values}@{self.timestamp} #{self.counter}"
