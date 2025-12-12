from typing import (
    Any,
    Dict,
    Generator,
    List,
    Optional,
    Sequence,
    Tuple,
    IO,
    Union,
)

import json
import numpy as np

from .BaseLoader import BaseLoader,ChannelData

class IGORPulseHeightLoader(BaseLoader):
    """
    IGOR pulse height loader, this type of loader does not actually have waveforms, but only the height and timestamp of a summary

    Only the pulse_height section of ChannelData and the timestamp will be filled
    """

    def __init__(self, fpath: str, rebuild_events_with_window: Optional[int] = None):
        self.file_handle: IO[str] = open(fpath)
        # First line starts with IGOR
        self.file_handle.readline()
        super().__init__(fpath, rebuild_events_with_window)
        self.in_waves = False
        self.timestamp_col = 0
        self.column_to_channel_map: Dict[int, str] = {}

    def loadChannelBatch(self) -> Optional[Sequence[ChannelData]]:
        if self.in_waves:
            line = self.file_handle.readline()
            if line == "" or line.startswith("END"):
                return None
            channels_to_load_2: List[ChannelData] = []
            # Begin parsing!
            split_line = line.split()
            timestamp = int(split_line[self.timestamp_col])
            for column, channel_name in self.column_to_channel_map.items():
                channel_called = int(channel_name)
                channels_to_load_2.append(
                    ChannelData(
                        channel_called,
                        timestamp,
                        {"pulse_height": int(split_line[column])},
                        None,
                    )
                )
            if len(channels_to_load_2) == 0:
                return None
            return channels_to_load_2
        if self.file_handle.closed:
            return None
        line = self.file_handle.readline()
        if line == "":
            return None
        while line.startswith("X") and line.split()[1] == "//":
            line = self.file_handle.readline()

        splitlines = line.split()
        column_to_channel_map: Dict[int, str] = {}
        assert splitlines[0].startswith("WAVES/o/D")
        timestamp_column = (
            list(
                filter(
                    lambda x: x,
                    [splitlines[i].startswith("timestamp") for i in range(len(splitlines))],
                )
            )
        )[0] - 1
        # Map a column to a channel, remember, we
        self.timestamp_col = timestamp_column

        def mapping_func() -> Generator[Tuple[int, str], Any, None]:
            for i in range(len(splitlines)):
                if splitlines[i].startswith("chan"):
                    yield (i - 1, splitlines[i].removeprefix("chan").removesuffix(","))

        for index, chan_name in mapping_func():
            column_to_channel_map[index] = chan_name
        self.column_to_channel_map = column_to_channel_map
        line = self.file_handle.readline()
        # Begin seeking the waveform, we're going to be looping from here-on-out
        if line.startswith("BEGIN"):
            line = self.file_handle.readline()
            self.in_waves = True

        channels_to_load: List[ChannelData] = []
        # Begin parsing!
        split_line = line.split()
        timestamp = int(split_line[timestamp_column])
        self.saved_timestamp = timestamp
        for column, channel_name in column_to_channel_map.items():
            channel_called = int(channel_name)
            channels_to_load.append(
                ChannelData(
                    channel_called,
                    timestamp,
                    {"pulse_height": int(split_line[column])},
                    None,
                )
            )

        if len(channels_to_load) == 0:
            return None

        return channels_to_load

