"""Streaming configuration support"""

# -- Imports ------------------------------------------------------------------

from ctypes import c_uint8, LittleEndianStructure

# -- Classes ------------------------------------------------------------------

# pylint: disable=too-few-public-methods


class StreamingConfigBits(LittleEndianStructure):
    """Store enable/disabled channels of streaming configuration"""

    _fields_ = [
        ("first", c_uint8, 1),
        ("second", c_uint8, 1),
        ("third", c_uint8, 1),
    ]


# pylint: enable=too-few-public-methods


class StreamingConfiguration:
    """Streaming configuration

    Args:

        first:
            Specifies if the first channel is enabled or not

        second:
            Specifies if the second channel is enabled or not

        third:
            Specifies if the third channel is enabled or not

    Raises:

        ValueError:
            if none of the channels is active

    Examples:

        Create some example streaming configurations

        >>> config = StreamingConfiguration()
        >>> config = StreamingConfiguration(
        ...          first=False, second=True, third=True)

        Creating streaming configurations without active channels will fail

        >>> config = StreamingConfiguration(first=False)
        Traceback (most recent call last):
           ...
        ValueError: At least one channel needs to be active

        >>> config = StreamingConfiguration(
        ...     first=False, second=False, third=False)
        Traceback (most recent call last):
           ...
        ValueError: At least one channel needs to be active

    """

    def __init__(
        self, first: bool = True, second: bool = False, third: bool = False
    ) -> None:

        if first + second + third <= 0:
            raise ValueError("At least one channel needs to be active")

        self.channels = StreamingConfigBits(
            first=first, second=second, third=third
        )

    def __repr__(self) -> str:
        """Return the string representation of the streaming configuration

        Examples:

            Get the textual representation of some example streaming configs

            >>> StreamingConfiguration()
            Channel 1 enabled, Channel 2 disabled, Channel 3 disabled

            >>> StreamingConfiguration(first=False, second=True, third=False)
            Channel 1 disabled, Channel 2 enabled, Channel 3 disabled

            >>> StreamingConfiguration(first=True, second=True, third=True)
            Channel 1 enabled, Channel 2 enabled, Channel 3 enabled

        """

        channels = self.channels

        return ", ".join([
            f"Channel {name} {'en' if status else 'dis'}abled"
            for name, status in enumerate(
                (channels.first, channels.second, channels.third), start=1
            )
        ])

    def enabled_channels(self) -> int:
        """Get the number of activated channels

        Returns:

            The number of enabled channels

        Examples:

            Get the number of enabled channels for example streaming configs

            >>> StreamingConfiguration(first=True).enabled_channels()
            1

            >>> StreamingConfiguration(first=False, second=True, third=False
            ...                       ).enabled_channels()
            1

            >>> StreamingConfiguration(first=True, second=True, third=True
            ...                       ).enabled_channels()
            3

        """

        channels = self.channels

        return channels.first + channels.second + channels.third

    def data_length(self) -> int:
        """Returns the streaming data length

        This will be either:

        - 2 (when 2 channels are active), or
        - 3 (when 1 or 3 channels are active)

        For more information, please take a look `here`_.

        .. _here: https://mytoolit.github.io/Documentation/#command-data

        Returns:

            The length of the streaming data resulting from this channel
            configuration

        Examples:

            Get the data length of example streaming configurations

            >>> StreamingConfiguration().data_length()
            3

            >>> StreamingConfiguration(
            ...     first=False, second=True, third=False).data_length()
            3

            >>> StreamingConfiguration(
            ...     first=True, second=True, third=True).data_length()
            3

            >>> StreamingConfiguration(
            ...     first=False, second=True, third=True).data_length()
            2

        """

        return 2 if self.enabled_channels() == 2 else 3

    def axes(self) -> list[str]:
        """Get the activated axes returned by this streaming configuration

        Returns:

            A list containing all activated axes in alphabetical order

        Examples:

            Get the activated axes for example streaming configurations

            >>> StreamingConfiguration(
            ...     first=False, second=True, third=True).axes()
            ['y', 'z']
            >>> StreamingConfiguration(
            ...     first=True, second=True, third=False).axes()
            ['x', 'y']

        """

        channels = self.channels
        return [
            axis
            for axis, status in zip(
                "xyz",
                (channels.first, channels.second, channels.third),
            )
            if status
        ]

    @property
    def first(self) -> bool:
        """Check the activation state of the first channel

        Returns:

        ``True``, if the first channel is enabled or ``False`` otherwise

        Examples:

            Check channel one activation status for example configs

            >>> StreamingConfiguration(first=True, second=False,
            ...                        third=False).first
            True
            >>> StreamingConfiguration(first=False, second=False,
            ...                        third=True).first
            False

        """

        return bool(self.channels.first)

    @property
    def second(self) -> bool:
        """Check the activation state of the second channel

        Returns:

            ``True``, if the second channel is enabled or ``False`` otherwise

        Examples:

            Check channel two activation status for example configs

            >>> StreamingConfiguration(
            ...     first=True, second=False, third=False).second
            False
            >>> StreamingConfiguration(
            ...     first=False, second=True, third=True).second
            True

        """

        return bool(self.channels.second)

    @property
    def third(self) -> bool:
        """Check the activation state of the third channel

        Returns:

        ``True``, if the third channel is enabled or ``False`` otherwise

        Examples:

            Check channel three activation status for example configs

            >>> StreamingConfiguration(
            ...     first=True, second=False, third=False).third
            False
            >>> StreamingConfiguration(
            ...     first=False, second=False, third=True).third
            True

        """

        return bool(self.channels.third)
