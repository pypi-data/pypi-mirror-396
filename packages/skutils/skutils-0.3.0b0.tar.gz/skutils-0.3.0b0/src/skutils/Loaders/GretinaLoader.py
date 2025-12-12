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
import warnings

from .BaseLoader import BaseLoader,ChannelData
from .LegacyGretinaLoader import LegacyGretinaLoader

class GretinaLoader(BaseLoader):
    """
    Different from the original GretinaLoader, this wraps that to the standard BaseLoader interface for consistency purposes.
    """

    def __init__(self, fpath: str, rebuild_events_with_window: Optional[int] = None):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.loader = LegacyGretinaLoader(fpath)  # type: ignore
        super().__init__(fpath, rebuild_events_with_window)

    def loadChannelBatch(self) -> Optional[Sequence[ChannelData]]:
        # contain all of the code without typing and get it into a typed set of code, sucks but, what can you do.
        metadata, event = self.loader.next_event()
        if metadata is None and event is None:
            return None
        assert metadata is not None
        chan_list = metadata["channels"]
        summaries = metadata["summaries"]
        timestamp = metadata["timestamp"]
        channel_list: List[ChannelData] = []
        for i in range(len(chan_list)):
            channel = chan_list[i]
            summary = None
            if summaries:
                summary = summaries[i]
            else:
                summary = {}
            if event.shape[1]: # type: ignore
                event_array = event[:, i] # type: ignore
                channel_list.append(ChannelData(channel, timestamp, summary, event_array))
            else:
                channel_list.append(ChannelData(channel, timestamp, summary, None))
        return channel_list

    def __exit__(self, type: Any, value: Any, traceback: Any) -> None:
        self.loader.__exit__(type, value, traceback)  # type: ignore

