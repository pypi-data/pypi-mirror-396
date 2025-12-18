"""Measurement support code"""

# -- Imports ------------------------------------------------------------------

from __future__ import annotations

from typing import Callable, Iterator, NamedTuple

from icotronic.can.streaming.config import StreamingConfiguration
from icotronic.can.streaming.data import StreamingData
from icotronic.can.dataloss import calculate_dataloss_stats

# -- Classes ------------------------------------------------------------------


class DataPoint(NamedTuple):
    """Streaming data point"""

    counter: int
    """Message counter"""
    timestamp: float
    """Timestamp of data"""
    value: float
    """Data value"""

    def __repr__(self):
        """Get textual representation of data

        Returns:

            A string containing the attributes of this datapoint

        Examples:

            Get the textual representation of a data point

            >>> DataPoint(counter=1, timestamp=2, value=3)
            3@2 #1

        """

        return f"{self.value}@{self.timestamp} #{self.counter}"


class ChannelData:
    """Store measurement data for a single channel"""

    def __init__(self) -> None:
        self.data: list[DataPoint] = []

    def __repr__(self) -> str:
        """Get the string representation of the data

        Examples:

            Get string representation of some example data

            >>> t1 = 1756124450.256398
            >>> t2 = 1756124450.2564
            >>> data = ChannelData()
            >>> data.append(DataPoint(counter=1, timestamp=t1, value=4))
            >>> data.append(DataPoint(counter=1, timestamp=t1, value=5))
            >>> data.append(DataPoint(counter=1, timestamp=t1, value=6))
            >>> data.append(DataPoint(counter=2, timestamp=t2, value=7))
            >>> data.append(DataPoint(counter=2, timestamp=t2, value=8))
            >>> data.append(DataPoint(counter=2, timestamp=t2, value=9))

            >>> data # doctest:+NORMALIZE_WHITESPACE
            4@1756124450.256398 #1
            5@1756124450.256398 #1
            6@1756124450.256398 #1
            7@1756124450.2564 #2
            8@1756124450.2564 #2
            9@1756124450.2564 #2

        """

        return "\n".join([repr(datapoint) for datapoint in self.data])

    def __iter__(self) -> Iterator:
        """Iterate over the channel data

        Returns:

            An iterator over the data points of the channel data

        Examples:

            Print the timestamps of some channel data

            >>> data = ChannelData()
            >>> t1 = 1756124450.1234
            >>> t2 = 1756124450.1235

            >>> data.append(DataPoint(counter=1, timestamp=t1, value=4))
            >>> data.append(DataPoint(counter=1, timestamp=t2, value=5))

            >>> for point in data:
            ...     print(point.timestamp)
            1756124450.1234
            1756124450.1235

        """

        return iter(self.data)

    def append(self, data: DataPoint) -> None:
        """Append a value to the channel data

        Args:

            data:

                The data point that should be added to the channel data

        Examples:

            Add some data points to a channel data object

            >>> data = ChannelData()

            >>> t1 = 1756124450.256398
            >>> t2 = t1 + 0.000003
            >>> data.append(DataPoint(counter=255, timestamp=t1, value=10))
            >>> data.append(DataPoint(counter=1, timestamp=t2, value=20))
            >>> data
            10@1756124450.256398 #255
            20@1756124450.256401 #1

        """

        self.data.append(data)


# pylint: disable=too-few-public-methods


class Conversion:
    """Conversion functions for measurement data

    Args:

        first:

            The conversion function for the first channel

        second:

            The conversion function for the second channel

        third:

            The conversion function for the third channel

    Examples:

        Create a conversion object that doubles values of the first channel

        >>> double = lambda value: value * 2
        >>> conversion = Conversion(second=double)

    """

    def __init__(
        self,
        first: Callable[[float], float] | None = None,
        second: Callable[[float], float] | None = None,
        third: Callable[[float], float] | None = None,
    ) -> None:
        self.first = first
        self.second = second
        self.third = third


# pylint: enable=too-few-public-methods


class MeasurementData:
    """Measurement data

    Args:

        configuration:

            The streaming configuration that was used to collect the
            measurement data

    """

    def __init__(self, configuration: StreamingConfiguration) -> None:
        self.configuration = configuration
        self.streaming_data_list: list[StreamingData] = []

    def __repr__(self) -> str:
        """Get the textual representation of the measurement data

        Returns:

            The textual representation of the measurement data

        Examples:

            >>> config = StreamingConfiguration(first=True, second=True,
            ...                                 third=False)
            >>> data = MeasurementData(config)
            >>> s1 = StreamingData(values=[1, 2], counter=255,
            ...                    timestamp=1756125747.528234)
            >>> s2 = StreamingData(values=[3, 4], counter=0,
            ...                    timestamp=1756125747.528237)
            >>> data.append(s1)

            >>> data
            Channel 1 enabled, Channel 2 enabled, Channel 3 disabled
            [1, 2]@1756125747.528234 #255

            >>> data.append(s2)
            >>> data
            Channel 1 enabled, Channel 2 enabled, Channel 3 disabled
            [1, 2]@1756125747.528234 #255
            [3, 4]@1756125747.528237 #0

        """

        return (
            f"{self.configuration}"
            + ("\n" if self.streaming_data_list else "")
            + "\n".join([
                str(streaming_data)
                for streaming_data in self.streaming_data_list
            ])
        )

    def __iter__(self) -> Iterator:
        """Iterate over the measurement data

        Returns:

            An iterator over the streaming dat objects contained in the
            measurement data

        Examples:

            Iterate over some example measurement data

            >>> config = StreamingConfiguration(first=False, second=True,
            ...                                 third=False)
            >>> data = MeasurementData(config)
            >>> s1 = StreamingData(values=[123, 456], counter=155,
            ...                    timestamp=1758029094.7407959)
            >>> s2 = StreamingData(values=[78, 9], counter=156,
            ...                    timestamp=1758029094.7407968)
            >>> data.append(s1)
            >>> data.append(s2)

            >>> for stream_data in data:
            ...     print(stream_data)
            [123, 456]@1758029094.7407959 #155
            [78, 9]@1758029094.7407968 #156

        """

        return iter(self.streaming_data_list)

    def __len__(self) -> int:
        """Get the length of the measurement data

        The length is defined as the number of streaming data items contained
        in the measurement data.

        Returns:

            The number of streaming data elements in the measurement data

        Examples:

            >>> config = StreamingConfiguration(first=True, second=True,
            ...                                 third=False)
            >>> data = MeasurementData(config)
            >>> len(data)
            0

            >>> s1 = StreamingData(values=[1, 2], counter=255,
            ...                    timestamp=1756125747.528234)
            >>> data.append(s1)
            >>> len(data)
            1

            >>> s2 = StreamingData(values=[3, 4], counter=0,
            ...                    timestamp=1756125747.528237)
            >>> data.append(s2)
            >>> len(data)
            2

        """

        return len(self.streaming_data_list)

    def first(self) -> ChannelData:
        """Get all data of the first measurement channel

        Returns:

            Data values for the first measurement channel

        Examples:

            Get first channel data of measurement with two enabled channels

            >>> config = StreamingConfiguration(first=True, second=True,
            ...                                 third=False)
            >>> data = MeasurementData(config)
            >>> s1 = StreamingData(values=[1, 2], counter=255,
            ...                    timestamp=1756125747.528234)
            >>> s2 = StreamingData(values=[3, 4], counter=0,
            ...                    timestamp=1756125747.528237)
            >>> data.append(s1)
            >>> data.append(s2)
            >>> data.first() # doctest:+NORMALIZE_WHITESPACE
            1@1756125747.528234 #255
            3@1756125747.528237 #0
            >>> data.second() # doctest:+NORMALIZE_WHITESPACE
            2@1756125747.528234 #255
            4@1756125747.528237 #0
            >>> data.third()
            <BLANKLINE>

            Get first channel data of measurement with one enabled channel

            >>> config = StreamingConfiguration(first=True, second=False,
            ...                                 third=False)
            >>> data = MeasurementData(config)
            >>> s1 = StreamingData(values=[1, 2, 3], counter=10,
            ...                    timestamp=1756126628.820695)
            >>> s2 = StreamingData(values=[4, 5, 6], counter=20,
            ...                    timestamp=1756126628.8207)
            >>> data.append(s1)
            >>> data.append(s2)
            >>> data.first() # doctest:+NORMALIZE_WHITESPACE
            1@1756126628.820695 #10
            2@1756126628.820695 #10
            3@1756126628.820695 #10
            4@1756126628.8207 #20
            5@1756126628.8207 #20
            6@1756126628.8207 #20
            >>> data.second()
            <BLANKLINE>
            >>> data.third()
            <BLANKLINE>

        """

        channel_data = ChannelData()
        configuration = self.configuration

        if configuration.first:
            if not configuration.second and not configuration.third:
                # Three values
                for streaming_data in self.streaming_data_list:
                    counter = streaming_data.counter
                    timestamp = streaming_data.timestamp
                    for value in streaming_data.values:
                        channel_data.append(
                            DataPoint(
                                counter=counter,
                                timestamp=timestamp,
                                value=value,
                            )
                        )
            else:
                # One value
                for streaming_data in self.streaming_data_list:
                    channel_data.append(
                        DataPoint(
                            counter=streaming_data.counter,
                            timestamp=streaming_data.timestamp,
                            value=streaming_data.values[0],
                        )
                    )

        return channel_data

    def second(self) -> ChannelData:
        """Get all data of the second measurement channel

        Returns:

            Data values for the second measurement channel

        Examples:

            Get second channel data of measurement with two enabled channels

            >>> config = StreamingConfiguration(first=False, second=True,
            ...                                 third=True)
            >>> data = MeasurementData(config)
            >>> s1 = StreamingData(values=[1, 2], counter=255,
            ...                    timestamp=1756125747.528234)
            >>> s2 = StreamingData(values=[3, 4], counter=0,
            ...                    timestamp=1756125747.528237)
            >>> data.append(s1)
            >>> data.append(s2)
            >>> data.first()
            <BLANKLINE>
            >>> data.second() # doctest:+NORMALIZE_WHITESPACE
            1@1756125747.528234 #255
            3@1756125747.528237 #0
            >>> data.third() # doctest:+NORMALIZE_WHITESPACE
            2@1756125747.528234 #255
            4@1756125747.528237 #0

            Get second channel data of measurement with one enabled channel

            >>> config = StreamingConfiguration(first=False, second=True,
            ...                                 third=False)
            >>> data = MeasurementData(config)
            >>> s1 = StreamingData(values=[1, 2, 3], counter=10,
            ...                    timestamp=1756126628.820695)
            >>> s2 = StreamingData(values=[4, 5, 6], counter=20,
            ...                    timestamp=1756126628.8207)
            >>> data.append(s1)
            >>> data.append(s2)
            >>> data.first()
            <BLANKLINE>
            >>> data.second() # doctest:+NORMALIZE_WHITESPACE
            1@1756126628.820695 #10
            2@1756126628.820695 #10
            3@1756126628.820695 #10
            4@1756126628.8207 #20
            5@1756126628.8207 #20
            6@1756126628.8207 #20
            >>> data.third()
            <BLANKLINE>

        """

        channel_data = ChannelData()
        configuration = self.configuration

        if configuration.second:
            if not configuration.first and not configuration.third:
                # Three values
                for streaming_data in self.streaming_data_list:
                    counter = streaming_data.counter
                    timestamp = streaming_data.timestamp
                    for value in streaming_data.values:
                        channel_data.append(
                            DataPoint(
                                counter=counter,
                                timestamp=timestamp,
                                value=value,
                            )
                        )
            else:
                # One value
                for streaming_data in self.streaming_data_list:
                    channel_data.append(
                        DataPoint(
                            counter=streaming_data.counter,
                            timestamp=streaming_data.timestamp,
                            value=(
                                streaming_data.values[0]
                                if not configuration.first
                                else streaming_data.values[1]
                            ),
                        )
                    )

        return channel_data

    def third(self) -> ChannelData:
        """Get all data of the third measurement channel

        Returns:

            Data values for the third measurement channel

        Examples:

            Get third channel data of measurement with two enabled channels

            >>> config = StreamingConfiguration(first=True, second=False,
            ...                                 third=True)
            >>> data = MeasurementData(config)
            >>> s1 = StreamingData(values=[1, 2], counter=255,
            ...                    timestamp=1756125747.528234)
            >>> s2 = StreamingData(values=[3, 4], counter=0,
            ...                    timestamp=1756125747.528237)
            >>> data.append(s1)
            >>> data.append(s2)
            >>> data.first() # doctest:+NORMALIZE_WHITESPACE
            1@1756125747.528234 #255
            3@1756125747.528237 #0
            >>> data.second()
            <BLANKLINE>
            >>> data.third() # doctest:+NORMALIZE_WHITESPACE
            2@1756125747.528234 #255
            4@1756125747.528237 #0

            Get third channel data of measurement with one enabled channel

            >>> config = StreamingConfiguration(first=False, second=False,
            ...                                 third=True)
            >>> data = MeasurementData(config)
            >>> s1 = StreamingData(values=[1, 2, 3], counter=10,
            ...                    timestamp=1756126628.820695)
            >>> s2 = StreamingData(values=[4, 5, 6], counter=20,
            ...                    timestamp=1756126628.8207)
            >>> data.append(s1)
            >>> data.append(s2)
            >>> data.first()
            <BLANKLINE>
            >>> data.second()
            <BLANKLINE>
            >>> data.third() # doctest:+NORMALIZE_WHITESPACE
            1@1756126628.820695 #10
            2@1756126628.820695 #10
            3@1756126628.820695 #10
            4@1756126628.8207 #20
            5@1756126628.8207 #20
            6@1756126628.8207 #20

        """

        channel_data = ChannelData()
        configuration = self.configuration

        if configuration.third:
            if not configuration.first and not configuration.second:
                # Three values
                for streaming_data in self.streaming_data_list:
                    counter = streaming_data.counter
                    timestamp = streaming_data.timestamp
                    for value in streaming_data.values:
                        channel_data.append(
                            DataPoint(
                                counter=counter,
                                timestamp=timestamp,
                                value=value,
                            )
                        )
            else:
                # One value
                for streaming_data in self.streaming_data_list:
                    channel_data.append(
                        DataPoint(
                            counter=streaming_data.counter,
                            timestamp=streaming_data.timestamp,
                            value=streaming_data.values[-1],
                        )
                    )

        return channel_data

    def dataloss(self) -> float:
        """Get measurement dataloss based on message counters

        Returns:

            The overall amount of dataloss as number between 0 (no data loss)
            and 1 (all data lost).

        """

        return calculate_dataloss_stats((
            streaming_data.counter
            for streaming_data in self.streaming_data_list
        )).dataloss()

    def append(self, data: StreamingData) -> None:
        """Append some streaming data to the measurement

        Args:

            data:

                The streaming data that should be added to the measurement

        Examples:

            Append some streaming data to a measurement

            >>> config = StreamingConfiguration(first=True, second=True,
            ...                                 third=True)
            >>> data = MeasurementData(config)
            >>> data
            Channel 1 enabled, Channel 2 enabled, Channel 3 enabled

            >>> s1 = StreamingData(values=[4, 5, 3], counter=15,
            ...                    timestamp=1756197008.776551)
            >>> data.append(s1)
            >>> data
            Channel 1 enabled, Channel 2 enabled, Channel 3 enabled
            [4, 5, 3]@1756197008.776551 #15

        """

        self.streaming_data_list.append(data)

    def extend(self, data: MeasurementData) -> None:
        """Extend this measurement data with some other measurement data

        Args:

            data:

                The measurement data that should be added to this measurement

        Examples:

            Extend measurement data with other measurement data

            >>> config = StreamingConfiguration(first=True, second=False,
            ...                                 third=True)
            >>> data1 = MeasurementData(config)
            >>> s1 = StreamingData(values=[1, 2], counter=255,
            ...                    timestamp=1756125747.528234)
            >>> s2 = StreamingData(values=[3, 4], counter=0,
            ...                    timestamp=1756125747.528237)
            >>> data1.append(s1)
            >>> data1.append(s2)
            >>> data1
            Channel 1 enabled, Channel 2 disabled, Channel 3 enabled
            [1, 2]@1756125747.528234 #255
            [3, 4]@1756125747.528237 #0

            >>> data2 = MeasurementData(config)
            >>> s3 = StreamingData(values=[10, 20], counter=1,
            ...                    timestamp=1756125747.678912)
            >>> data2.append(s3)
            >>> data2
            Channel 1 enabled, Channel 2 disabled, Channel 3 enabled
            [10, 20]@1756125747.678912 #1

            >>> data1.extend(data2)
            >>> data1
            Channel 1 enabled, Channel 2 disabled, Channel 3 enabled
            [1, 2]@1756125747.528234 #255
            [3, 4]@1756125747.528237 #0
            [10, 20]@1756125747.678912 #1

        """

        if self.configuration != data.configuration:
            raise ValueError(
                f"Trying to merge measurement data {self.configuration} with "
                "different streaming configuration: {data.configuration}"
            )

        self.streaming_data_list.extend(data.streaming_data_list)

    def apply(self, conversion: Conversion) -> MeasurementData:
        """Apply functions to the values stored in the measurement

        Args:

            conversion:

                The conversion functions that will be applied to the
                measurement

        Returns:

            The measurement data itself, after the conversion was applied

        Examples:

            Apply functions to some measurement data with one active channel


            >>> config = StreamingConfiguration(first=False, second=True,
            ...                                 third=False)
            >>> data = MeasurementData(config)
            >>> s1 = StreamingData(values=[1, 20, 81], counter=22,
            ...                    timestamp=1756125747.528234)
            >>> s2 = StreamingData(values=[50, 1, 29], counter=25,
            ...                    timestamp=1756125747.528254)
            >>> data.append(s1)
            >>> data.append(s2)

            >>> plus_two = (lambda value: value + 2)
            >>> conversion = Conversion(second=plus_two)

            >>> data
            Channel 1 disabled, Channel 2 enabled, Channel 3 disabled
            [1, 20, 81]@1756125747.528234 #22
            [50, 1, 29]@1756125747.528254 #25
            >>> data.apply(conversion)
            Channel 1 disabled, Channel 2 enabled, Channel 3 disabled
            [3, 22, 83]@1756125747.528234 #22
            [52, 3, 31]@1756125747.528254 #25

            Apply functions to some measurement data with two active channels

            >>> config = StreamingConfiguration(first=True, second=False,
            ...                                 third=True)
            >>> data = MeasurementData(config)
            >>> s1 = StreamingData(values=[1, 2], counter=255,
            ...                    timestamp=1756125747.528234)
            >>> s2 = StreamingData(values=[3, 4], counter=0,
            ...                    timestamp=1756125747.528237)
            >>> data.append(s1)
            >>> data.append(s2)

            >>> conversion = Conversion(third=plus_two)

            >>> data
            Channel 1 enabled, Channel 2 disabled, Channel 3 enabled
            [1, 2]@1756125747.528234 #255
            [3, 4]@1756125747.528237 #0

            >>> data.apply(conversion)
            Channel 1 enabled, Channel 2 disabled, Channel 3 enabled
            [1, 4]@1756125747.528234 #255
            [3, 6]@1756125747.528237 #0

            Apply functions to some measurement data with three active channels

            >>> config = StreamingConfiguration(first=True, second=True,
            ...                                 third=True)
            >>> data = MeasurementData(config)
            >>> s1 = StreamingData(values=[4, 5, 3], counter=15,
            ...                    timestamp=1756197008.776551)
            >>> s2 = StreamingData(values=[8, 10, 6], counter=16,
            ...                    timestamp=1756197008.776559)
            >>> data.append(s1)
            >>> data.append(s2)

            >>> double = (lambda value: value * 2)
            >>> conversion = Conversion(first=double, third=plus_two)

            >>> data
            Channel 1 enabled, Channel 2 enabled, Channel 3 enabled
            [4, 5, 3]@1756197008.776551 #15
            [8, 10, 6]@1756197008.776559 #16

            >>> data.apply(conversion)
            Channel 1 enabled, Channel 2 enabled, Channel 3 enabled
            [8, 5, 5]@1756197008.776551 #15
            [16, 10, 8]@1756197008.776559 #16

        """

        enabled_channels = self.configuration.enabled_channels()
        config = self.configuration

        functions: list[Callable[[float], float] | None] = []

        if enabled_channels == 1:
            # Apply single function to all values
            function = (
                conversion.first
                if config.first
                else (conversion.second if config.second else conversion.third)
            )
            if function is not None:
                functions = [function, function, function]

        elif enabled_channels == 2:
            # Apply single function to single value
            if config.first:
                functions = [
                    conversion.first,
                    conversion.second if config.second else conversion.third,
                ]
            else:
                functions = [conversion.second, conversion.third]

        elif enabled_channels == 3:
            functions = [conversion.first, conversion.second, conversion.third]

        for streaming_data in self.streaming_data_list:
            values = streaming_data.values
            for (index, value), function in zip(enumerate(values), functions):
                if function is not None:
                    values[index] = function(value)

        return self


# -- Main ---------------------------------------------------------------------

if __name__ == "__main__":
    from doctest import testmod

    testmod()
