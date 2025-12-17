"""Ring buffer for audio samples."""

from collections import deque
from typing import List


class AudioRingBuffer:
    """Ring buffer for storing recent audio samples.

    Used by waveform widgets to maintain a scrolling display window.
    Automatically discards old samples when buffer is full.
    """

    def __init__(self, maxlen: int):
        """Initialize ring buffer.

        Args:
            maxlen: Maximum number of samples to store
        """
        self.buffer: deque[int | float] = deque(maxlen=maxlen)
        self.maxlen = maxlen

    def append(self, samples: List[int] | List[float]):
        """Append audio samples to buffer.

        Args:
            samples: List of audio sample values
        """
        self.buffer.extend(samples)

    def get_data(self) -> List[int] | List[float]:
        """Get all current samples as a list.

        Returns:
            List of audio samples
        """
        return list(self.buffer)

    def clear(self):
        """Clear all samples from buffer."""
        self.buffer.clear()

    def __len__(self) -> int:
        """Get current number of samples in buffer.

        Returns:
            Number of samples
        """
        return len(self.buffer)
