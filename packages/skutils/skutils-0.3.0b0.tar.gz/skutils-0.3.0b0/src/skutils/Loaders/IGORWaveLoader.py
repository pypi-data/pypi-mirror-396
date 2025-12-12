
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
import re
import io
import numpy as np
from collections import OrderedDict

from .BaseLoader import BaseLoader,ChannelData

class IGORWaveLoader(BaseLoader):
    """
    A loader for the IGOR wave format type, this is an event type format and will consistently have events correctly built so long as the orignial event was made.
    """
    __BYTES_TO_BUFFER = 1024
    def __init__(self, fpath: str, rebuild_events_with_window: Optional[int] = None):
        self.file_handle: IO[str] = open(fpath)
        # First line starts with IGOR
        super().__init__(fpath, rebuild_events_with_window)
        self.buffer = io.StringIO()

        self.event_group_regex        = re.compile(r"(?:X\sevt_num.*?X\sProcessOneEvent.*?\))", flags=re.DOTALL | re.IGNORECASE)
        self.comment_regex            = re.compile(r"X\s//.*\n", flags=re.IGNORECASE)

        self.timestamp_regex          = re.compile(r"X\stimestamp\s*=\s*(?P<timestamp>[0-9-]{1,})\n", 
                                                    flags=re.IGNORECASE)
        self.evt_num_regex            = re.compile(r"X\sevt_num\s*=\s*(?P<evt_num>[0-9-]{1,})\n", 
                                                    flags=re.IGNORECASE)
        self.ps_wave_regex            = re.compile(r"WAVES/o/D\/N=\((?P<num_quantities>\d*),(?P<num_channels>\d*)\)\spulse_summaries\sBEGIN\n(?P<data>.*?)\nEND", 
                                                    flags=re.IGNORECASE | re.DOTALL)
        self.ps_dim_label_regex       = re.compile(r"X\sSetDimLabel\s*(?P<igor_axis>\d)\s*,\s*(?P<quantity_index>\d)\s*,\s*'(?P<quantity_label>.*?)'\s*,\s*pulse_summaries", 
                                                    flags=re.IGNORECASE | re.MULTILINE)
        self.waveform_wave_regex      = re.compile(r"WAVES/o/D\s(?P<channel_names>.*?)\nBEGIN\n(?P<data>.*?)\sEND",
                                                    flags=re.IGNORECASE | re.MULTILINE | re.DOTALL)
        
    # _________________________________________________________________________
    def __readNextEventTextBlockWithBuffering(self):
        # import time; lap_start_t = time.monotonic(); init_start_t = lap_start_t; idx = 0
        # .....................................................................
        # Buffer until we detect that the entire content of an event if in memory
        event_text = ""
        # idx += 1; print(f"==== loop start {idx} : {1000*(time.monotonic()-lap_start_t):.1f}ms"); lap_start_t = time.monotonic()
        while True:
            tmp_buf = self.file_handle.read(self.__BYTES_TO_BUFFER)
            # print(f"reading : {1000*(time.monotonic()-lap_start_t):.1f}ms"); lap_start_t = time.monotonic()
            bytes_read = len(tmp_buf)
            self.buffer.write(tmp_buf)
            # print(f"writing to buffer : {1000*(time.monotonic()-lap_start_t):.1f}ms"); lap_start_t = time.monotonic()
            if "ProcessOneEvent" in self.buffer.getvalue():
            
                event_match = re.search(self.event_group_regex, self.buffer.getvalue())
                # print(f"event search : {1000*(time.monotonic()-lap_start_t):.1f}ms"); lap_start_t = time.monotonic()
                if event_match:
                    # grab block of text that represents an event in the IGOR format
                    event_text = event_match.group(0)

                    # roll the remaining data into a new buffer
                    self.buffer.seek( event_match.end(0) )
                    remaining_data = self.buffer.read()
                    self.buffer = io.StringIO()
                    self.buffer.write(remaining_data)
                    # print(f"rolling over buffer : {1000*(time.monotonic()-lap_start_t):.1f}ms"); lap_start_t = time.monotonic()
                    break
            
            if bytes_read == 0:
                break
        # idx += 1; print(f"==== loop end {idx} : {1000*(time.monotonic()-lap_start_t):.1f}ms"); lap_start_t = time.monotonic()

        # print(f"Total Time is {1000*(time.monotonic()-init_start_t):.2f}ms"); 

        return event_text

    # _________________________________________________________________________
    def loadChannelBatch(self) -> Optional[Sequence[ChannelData]]:
        # import time; lap_start_t = time.monotonic(); init_start_t = lap_start_t; idx = 0
        # .....................................................................
        # Get the next block of Event Text
        event_text = self.__readNextEventTextBlockWithBuffering()
        if event_text == "":
            return None
        # remove comments
        event_text = re.sub(self.comment_regex, "", event_text)
        # # print(f"{idx} : {1000*(time.monotonic()-lap_start_t):.1f}ms"); lap_start_t = time.monotonic(); idx += 1

        # .....................................................................
        # timestamp parsing
        timestamp_match = re.search(self.timestamp_regex, event_text)
        if timestamp_match:
            # use the last timestamp specified in the event text. Should only ever be 1
            timestamp = int( timestamp_match.group('timestamp') )
        else:
            timestamp = -1

        # .....................................................................
        # evt_num parsing
        evt_num_match = re.search(self.evt_num_regex, event_text)
        if evt_num_match:
            # use the last evt_num specified in the event text. Should only ever be 1
            evt_num = int( evt_num_match.group('evt_num') )
        else:
            evt_num = -1
        # # print(f"{idx} : {1000*(time.monotonic()-lap_start_t):.1f}ms"); lap_start_t = time.monotonic(); idx += 1
            
        # .....................................................................
        # Pulse Summary Parsing
        all_ps_dicts = []
        ps_data_match = re.search(self.ps_wave_regex, event_text)
        ps_dim_matches = [m for m in re.finditer(self.ps_dim_label_regex, event_text)]
        # # print(f"{idx} : {1000*(time.monotonic()-lap_start_t):.1f}ms"); lap_start_t = time.monotonic(); idx += 1

        if ps_data_match and ps_dim_matches:
            # ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
            # The following block converts the pulse summary WAVE into a numpy array
            num_quantities = int(ps_data_match.group('num_quantities'))
            num_channels   = int(ps_data_match.group('num_channels'))
            raw_ps_data = ps_data_match.group('data')   
            # # print(f"{idx} : {1000*(time.monotonic()-lap_start_t):.1f}ms"); lap_start_t = time.monotonic(); idx += 1

            tmp_array = np.fromstring(raw_ps_data, dtype=np.int64, sep=" ")
            tmp_array = tmp_array.reshape( (num_quantities,num_channels) )
            # # print(f"{idx} : {1000*(time.monotonic()-lap_start_t):.1f}ms"); lap_start_t = time.monotonic(); idx += 1

            # ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
            # The following block decodes which column/row contains the pulse summary data
            # that we need. In IGOR this is specified by the "SetDimLabel" command

            # create a dictionary storing pulse summary information for each column (ie channel) in the event
            all_ps_dicts = [{} for i in range(tmp_array.shape[1])] 
            # iterate through every single line in this event that contains "SetDimLabel"
            for dim_components in ps_dim_matches:
                igor_axis      = int( dim_components.group('igor_axis') )
                quantity_index = int( dim_components.group('quantity_index') )
                quantity_label = dim_components.group('quantity_label').lower()
                # # print(f"{idx} : {1000*(time.monotonic()-lap_start_t):.1f}ms"); lap_start_t = time.monotonic(); idx += 1

                # if the SetDimLabel axus is 0, then we are specifying the name and index 
                # of the quantity in the pulse summary. 
                if igor_axis == 0:
                    for col_idx in range(tmp_array.shape[1]):
                        all_ps_dicts[col_idx][quantity_label] = int(tmp_array[quantity_index,col_idx])
                # otherwise the SetDimLabel row is referring to the experimenter-defined name of 
                # the column itself
                else:
                    col_idx = quantity_index
                    all_ps_dicts[col_idx]['channel_name'] = quantity_label
                # # print(f"{idx} : {1000*(time.monotonic()-lap_start_t):.1f}ms"); lap_start_t = time.monotonic(); idx += 1

        ps_by_channel : Dict[int,Dict] = {int(ps['channel']):ps for ps in all_ps_dicts}

        # Not used at this time. For future where we can specify name of channel in FemtoDAQ GUI
        names_to_channels : Dict[str,int] = {ps['channel_name']:ps['channel'] for ps in all_ps_dicts} # type: ignore
        
        # .....................................................................
        # Waveform Parsing
        wave_by_channel = {}
        wavedata = None
        waveform_match = re.search(self.waveform_wave_regex, event_text)
        # # print(f"{idx} : {1000*(time.monotonic()-lap_start_t):.1f}ms"); lap_start_t = time.monotonic(); idx += 1
        if waveform_match:
            channel_names = waveform_match.group('channel_names').split(',')
            raw_wavedata  = waveform_match.group('data')

            # NOTE: In future we may want to replace this with a lookup using `names_to_channels`
            wavedata_channels = [int(re.sub(r"\D","",name)) for name in channel_names]
            wavedata = np.fromstring(raw_wavedata, dtype=np.int16, sep=" ")
            wavedata = wavedata.reshape((-1, len(wavedata_channels)))

            wave_by_channel = {ch:wavedata[:,i] for i,ch in enumerate(wavedata_channels)}
        # # print(f"{idx} : {1000*(time.monotonic()-lap_start_t):.1f}ms"); lap_start_t = time.monotonic(); idx += 1
            
        # .....................................................................
        # Build the list of Channels and return

        ret = None
        all_channels = set(wave_by_channel.keys()).union(ps_by_channel.keys())
        if all_channels:
            channel_data_batch: List[ChannelData] = []

            for channel in all_channels:
                waveform = wave_by_channel.get(channel, None)
                summary  = ps_by_channel.get(channel, None)
                channel_data_batch.append( ChannelData(channel, timestamp, summary, waveform, other_data={'evt_num':evt_num}) )

            ret = channel_data_batch
        # # print(f"{idx} : {1000*(time.monotonic()-lap_start_t):.1f}ms"); lap_start_t = time.monotonic(); idx += 1
        # print(f"Total Time is {1000*(time.monotonic()-init_start_t):.2f}ms"); \
        return ret

