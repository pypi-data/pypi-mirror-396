"""Data formats for streaming data"""

# -- Imports ------------------------------------------------------------------

from icotronic.can.streaming.config import StreamingConfiguration

# -- Classes ------------------------------------------------------------------


class StreamingFormat:
    """Support for specifying the `data streaming format`_

    .. _data streaming format:
       https://mytoolit.github.io/Documentation/#block-streaming

    Args:

        *value:
            The value of the streaming format byte

        streaming:
            Specifies if this is a request for a stream of data bytes;
            If this value is not set or set to ``False``, then the request is
            only for a single value (or set of values).

        width:
            Specifies the width of a single value (either 2 or 3 bytes)

        channels:
            Specifies for which channels data should be transmitted or not

        sets:
            Specifies the number of data sets that should be transmitted

            The value 0 stops the stream. Other possible values for the
            number of sets are 1, 3, 6, 10, 15, 20 and 30.

        value_explanations:
            Three strings used to describe the first, second and third data
            value

    """

    data_set = [0, 1, 3, 6, 10, 15, 20, 30]
    """Possible number of data sets"""

    # pylint: disable=too-many-arguments

    def __init__(
        self,
        *value,
        streaming: bool | None = None,
        width: int | None = 2,
        channels: StreamingConfiguration | None = None,
        sets: int | None = None,
        value_explanations: tuple[str, str, str] = (
            "Value 1",
            "Value 2",
            "Value 3",
        ),
    ) -> None:

        def set_part(start, width, number):
            """Store bit pattern number at bit start of the identifier"""

            streaming_ones = 0xFF
            mask = (1 << width) - 1

            # Set all bits for targeted part to 0
            self.value &= (mask << start) ^ streaming_ones
            # Make sure we use the correct number of bits for number
            number = number & mask
            # Set bits to given value
            self.value |= number << start

        self.value_explanations = value_explanations

        if len(value) > 1:
            raise ValueError("More than one positional argument")

        self.value = value[0] if value else 0

        # =============
        # = Streaming =
        # =============

        if streaming:
            set_part(7, 1, int(streaming))

        # =========
        # = Width =
        # =========

        if width is not None:
            if not (isinstance(width, int) and 2 <= width <= 3):
                raise ValueError(f"Unsupported width value: {width}")

            set_part(6, 1, 1 if width == 3 else 0)

        # =================
        # = Active Values =
        # =================

        if channels:
            for shift, part in enumerate(
                [channels.third, channels.second, channels.first]
            ):
                if part is not False:
                    set_part(3 + shift, 1, part)

        # =============
        # = Data Sets =
        # =============

        if sets is not None:
            cls = type(self)

            if sets not in cls.data_set:
                raise ValueError(f"Unsupported number of data sets: {sets}")

            set_part(0, 3, cls.data_set.index(sets))

    # pylint: enable=too-many-arguments

    def __repr__(self) -> str:
        """Retrieve the textual representation of the streaming format

        Returns:

            A string that describes the streaming format

        Examples:

            Get the textual representation of some example streaming formats

            >>> StreamingFormat(width=3,
            ...                 channels=StreamingConfiguration(first=True),
            ...                 sets=15)
            Single Request, 3 Bytes, 15 Data Sets, Read Value 1

            >>> StreamingFormat(0b001, streaming=True)
            Streaming, 2 Bytes, 1 Data Set

            >>> StreamingFormat(0b110111)
            Single Request, 2 Bytes, 30 Data Sets, Read Value 1, Read Value 2

        """

        streaming = self.value >> 7

        data_sets = self.data_sets()
        data_set_explanation = (
            "Stop Stream"
            if data_sets == 0
            else f"{data_sets} Data Set{'' if data_sets == 1 else 's'}"
        )

        parts = [
            "Streaming" if streaming else "Single Request",
            f"{self.data_bytes()} Bytes",
            f"{data_set_explanation}",
        ]

        value_selection = (self.value >> 3) & 0b111

        first = value_selection >> 2
        second = value_selection >> 1 & 1
        third = value_selection & 1

        selected_values = [
            f"Read {value_explanation}"
            for selected, value_explanation in zip(
                (first, second, third), self.value_explanations
            )
            if selected
        ]

        value_explanation = (
            ", ".join(selected_values) if selected_values else ""
        )
        if value_explanation:
            parts.append(value_explanation)

        return ", ".join(parts)

    def data_sets(self) -> int:
        """Get the number of data sets of the streaming format

        Returns:

            The number of data sets

        Examples:

            Retrieve the number of data sets for some example streaming formats

            >>> StreamingFormat(
            ...     width=3,
            ...     channels=StreamingConfiguration(first=True),
            ...     sets=15
            ... ).data_sets()
            15

            >>> StreamingFormat(
            ...     channels=StreamingConfiguration(first=True, second=False),
            ...     sets=3
            ... ).data_sets()
            3

        """

        data_set_bits = self.value & 0b111
        cls = type(self)

        return cls.data_set[data_set_bits]

    def data_bytes(self) -> int:
        """Get the number of data bytes used for a single value

        Returns:

            The number of data bytes that represent a single streaming value

        Examples:

            Retrieve the number of data bytes for some streaming formats

            >>> StreamingFormat(width=3,
            ...                 channels=StreamingConfiguration(first=True),
            ...                 sets=15).data_bytes()
            3

            >>> StreamingFormat(
            ...     channels=StreamingConfiguration(first=True, second=False),
            ...     width=2
            ... ).data_bytes()
            2

        """

        return 3 if (self.value >> 6) & 1 else 2


class StreamingFormatVoltage(StreamingFormat):
    """Support for specifying the streaming format of voltage data

    Args:

        value:
            The value of the streaming format byte

        single:
            Specifies if the request was for a single value or not

        width:
            Specifies the width of a single value (either 2 or 3 bytes)

        channels:
            Specifies for which channels data should be transmitted or not

        sets:
            Specifies the number of data sets that should be transmitted

            The value 0 stops the stream. Other possible values for the
            number of sets are 1, 3, 6, 10, 15, 20 and 30.

    """

    def __init__(self, *arguments, **keyword_arguments) -> None:

        super().__init__(
            *arguments,
            **keyword_arguments,
            value_explanations=("Voltage 1", "Voltage 2", "Voltage 3"),
        )
