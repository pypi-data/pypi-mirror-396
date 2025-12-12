from typing import Dict, Literal, Union
import re

HitPatternType = Union[Literal["A", "C", "I"], str]


class HitPatternCoincidenceBuilder:
    """
    A utility class for easy building of hit pattern coincidences.
    """

    BUILDER_STRING = "channel_{0}_trigger_hit_pattern"

    def __init__(self, num_channels: int):
        """
        Initialize a new builder with the number of channels for a particular FemtoDAQ device.
        """
        self.num_channels = num_channels
        self.built_object: Dict[str, str] = {}

    def addChannel(self, channel: int, pattern: HitPatternType) -> None:
        """
        Add a channel to the coincidence pattern

        :param channel: A zero-indexed integer representing a channel on a device
        :param pattern: A string that starts with the letters A, C, or I (lower or upper case).
        The letter each corresponds with Anticoincidence, Coincidence, or Ignore, respectively

        """
        if channel not in range(0, self.num_channels):
            raise ValueError("Invalid channel passed to HitPatternCoincidenceBuilder!")
        key = self.BUILDER_STRING.format(channel)
        my_str = pattern.upper()

        map_of_vals = {"A": "ANTICOINCIDENCE", "C": "COINCIDENCE", "I": "IGNORE"}

        if len(my_str) == 0 or my_str[0] not in map_of_vals:
            raise ValueError("String must have a length and must start with one of the following letters: A, C, I")
        self.built_object[key] = map_of_vals[my_str[0]]

    def reset(self) -> None:
        self.built_object = {}

    def buildForSend(self) -> Dict[str, str]:
        for channel in range(self.num_channels):
            if self.BUILDER_STRING.format(channel) not in self.built_object:
                self.addChannel(channel, "i")
        return self.built_object

    def __getitem__(self, key: Union[int, str]) -> str:
        if isinstance(key, int):
            key = self.BUILDER_STRING.format(key)
        return self.built_object[key]

    def __setitem__(self, key: Union[int, str], pattern: str) -> None:
        if isinstance(key, int):
            return self.addChannel(key, pattern)
        # Run a check
        int_val = re.match(r"channel_([0-9]+)_trigger_hit_pattern", key)
        if int_val is None:
            raise ValueError("Key was not an integer or channel_([0-9]+)_trigger_hit_pattern!")
        chan_key = int(int_val.group(0))
        return self.addChannel(chan_key, pattern)
