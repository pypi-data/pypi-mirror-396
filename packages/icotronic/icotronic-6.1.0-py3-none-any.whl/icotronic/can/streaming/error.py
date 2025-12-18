"""Streaming errors"""

# -- Classes ------------------------------------------------------------------


class StreamingError(Exception):
    """General exception for streaming errors"""


class StreamingTimeoutError(StreamingError):
    """Raised if no streaming data was received for a certain amount of time"""


class StreamingBufferError(StreamingError):
    """Raised if there are too many streaming messages in the buffer"""
