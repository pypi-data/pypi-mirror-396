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


class EventCSVLoader(BaseLoader):
    """
    Loader for the TSV-type format for the Vireo EventCSV Format
    """

    def __init__(self, fpath: str, rebuild_events_with_window: Optional[int] = None):
        self.file_handle: IO[str] = open(fpath)
        super().__init__(fpath, rebuild_events_with_window)

    def loadChannelBatch(self) -> Optional[Sequence[ChannelData]]:
        # The way this works is we have a file made up of lines, if the line starts with a pound sign it's a comment
        # Technically, the file is a TSV, but I didn't know that at the time, thus, I may eventually swap this to use a "CSV" reader in TSV mode
        if self.file_handle.closed:
            return None
        line = self.file_handle.readline()
        if line == "":
            self.file_handle.close()
            return None
        line = line.strip()
        while line.startswith("#"):
            line = self.file_handle.readline()
        # Splitting the line here is fine, because what we're doing is going through a space-separated value here.
        separated = line.split()
        # Timestamp being first is fine....
        timestamp = int(separated[0])
        # Here's where it's no longer fine, we need to find the systems where the start and end are brackets, not spaces, as a temporary measure, we can
        try:
            channel_list: Sequence[int] = json.loads(separated[1])
        except json.JSONDecodeError as e:
            raise RuntimeError(
                f"It is likely that you somehow inserted a space into the bracket array, this will cause the file to not be parsed, the underlying error: {e}"
            )
        data_list: List[ChannelData] = []
        start = 2
        for channel in channel_list:
            array = None
            try:
                array = np.asarray(json.loads(separated[start]))
                data = ChannelData(
                    channel=channel,
                    event_timestamp=timestamp,
                    pulse_summary=None,
                    wave=array,
                )
                data_list.append(data)
                start += 1
            except json.JSONDecodeError as e:
                raise RuntimeError(
                    f"It is likely that you somehow inserted a space into the bracket array, this will cause the file to not be parsed, the underlying error: {e}"
                )
        return data_list

