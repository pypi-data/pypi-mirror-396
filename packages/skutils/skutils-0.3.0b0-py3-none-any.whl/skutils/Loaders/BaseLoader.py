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

# Python 3.8 minimum because of this and walrus
from functools import cached_property
import numpy as np

# Prep if we ever move up np minimum requirements to 1.21
# OurNumpyArrType = np.ndarray[tuple[int, ...], np.dtype[np.int16]]
OurNumpyArrType = np.ndarray


###############################################################################
class ChannelData:
    """
    All data related to a single channel, could be as part of an event or not as part of an event, and may or may not have a pulse summary or wave

    Check self.has_wave and self.has_summary to see if either are present

    .. autoattribute::

    """

    def __init__(
        self,
        channel: int,
        event_timestamp: int,
        pulse_summary: Optional[Dict[str, Any]],
        wave: Optional[OurNumpyArrType],
        other_data:Optional[Dict[str, Any]] = {},
    ):
        # General / Tracking Variables

        #: channel ID
        self.channel: int = channel
        #: FPGA Event Timestamp
        self.event_timestamp: int = event_timestamp

        #: Boolean indicating whether this channel contains waveform data
        self.has_wave: bool = isinstance(wave, np.ndarray)
        #: Boolean indicating whether this channel contains DSP summary data
        self.has_summary: bool = isinstance(pulse_summary, dict)

        #: Numpy Waveform for digitizer signal
        self.wave: Optional[OurNumpyArrType] = wave if self.has_wave else None

        #: Dictionary of Pulse Summary (DSP) Information
        self.pulse_summary: Dict[str, Any] = pulse_summary if isinstance(pulse_summary, dict) else {}

        #: Timestamp of this channels trigger. This will be equal to the event timestamp + relative channel offset defined in certain file formats
        if ('relative_timestamp' in self.pulse_summary) and ('relative_channel_timestamp' not in self.pulse_summary):
            self.pulse_summary['relative_channel_timestamp'] = self.pulse_summary.pop('relative_timestamp')
        self.channel_timestamp : int = event_timestamp + self.pulse_summary.get('relative_channel_timestamp', 0)


        #: Maximum height of pulse in the pulse height window. Subject to averaging
        self.pulse_height: Optional[int] = self.pulse_summary.get("pulse_height", None)
        #: Maximum height of trigger in the trigger active window. Subject to averaging
        self.trigger_height: Optional[int] = self.pulse_summary.get("trigger_height", None)
        if self.trigger_height is None:
            self.trigger_height = self.pulse_summary.get("trig_height", None)

        #: QuadQDC BASE Integration. Not supported on all digitizer models
        self.quadqdc_base: Optional[int] = self.pulse_summary.get("quadqdc_base", None)
        #: QuadQDC FAST Integration. Not supported on all digitizer models
        self.quadqdc_fast: Optional[int] = self.pulse_summary.get("quadqdc_fast", None)
        #: QuadQDC SLOW Integration. Not supported on all digitizer models
        self.quadqdc_slow: Optional[int] = self.pulse_summary.get("quadqdc_slow", None)
        #: QuadQDC TAIL Integration. Not supported on all digitizer models
        self.quadqdc_tail: Optional[int] = self.pulse_summary.get("quadqdc_tail", None)
        if self.quadqdc_base is None:
            self.quadqdc_base = self.pulse_summary.get("qdc_base_sum", None)
        if self.quadqdc_fast is None:
            self.quadqdc_fast = self.pulse_summary.get("qdc_fast_sum", None)
        if self.quadqdc_slow is None:
            self.quadqdc_slow = self.pulse_summary.get("qdc_slow_sum", None)
        if self.quadqdc_tail is None:
            self.quadqdc_tail = self.pulse_summary.get("qdc_tail_sum", None)
        #: Boolean indicating whether this channel triggered
        self.triggered: Optional[bool] = self.pulse_summary.get("triggered", None)
        #: The number of times the trigger for this channel fired in the trigger window
        #: Also known as pileup count
        self.trigger_multiplicity: Optional[int] = self.pulse_summary.get("trigger_count", None)
        if self.trigger_multiplicity is None:
            self.trigger_multiplicity = self.pulse_summary.get("trig_count", None)
        # Future:
        # self.qdc_rect     : int
        # self.qdc_tri      : int
        # self.mwd          : int

        #: other data not normally included in pulse summaries that may supported be in a special file format 
        self.other_data : Dict[str,Any] = {}

    # _________________________________________________________________________
    @cached_property
    def relative_channel_timestamp(self) -> Optional[int]:
        """
        Returns true if there have been multiple triggers in this channel
        """
        if self.channel_timestamp is not None:
            return (self.channel_timestamp - self.event_timestamp)
        return None

    # _________________________________________________________________________
    @cached_property
    def pileup(self) -> bool:
        """
        Returns true if there have been multiple triggers in this channel
        """
        if self.trigger_multiplicity:
            return True
        return False

    # _________________________________________________________________________
    @cached_property
    def num_wave_samples(self) -> int:
        """
        Returns the number of samples in the wave, 0 if this has no wave
        """
        if self.has_wave:
            if self.wave is not None:
                return self.wave.size
        return 0

    # _________________________________________________________________________
    def __str__(self) -> str:
        return f"<Channel{self.channel} Data: event_timestamp={self.event_timestamp} relative_channel_timestamp={self.relative_channel_timestamp} has_summary={self.has_summary} num_wave_samples={self.num_wave_samples}>"
    
    # _________________________________________________________________________
    def __repr__(self) -> str:
        return str(self)

###############################################################################
class EventInfo:
    """
    Information related to a group of channels collated as an "Event"
    as defined by either the file format or a rebuilt coincidence window.
    """

    def __init__(self, channel_data: Sequence[ChannelData]):
        """
        :channel_data: A list of more than one channel constituting an event
        """
        #: number of channels in this event
        self.num_channels = len(channel_data)
        assert self.num_channels > 0, "At least one channel must be provided"
        # Ensure channel data is homogenous
        if not all(channel_data[0].has_wave == channel_data[i].has_wave for i in range(self.num_channels)):
            raise ValueError("Events require every channel to have a waveform OR for none of them to have waveforms")
        
        if not all(channel_data[0].has_summary == channel_data[i].has_summary for i in range(self.num_channels)):
            raise ValueError("Events require every channel to have a pulse_summary OR for none of them to have pulse_summaries")

        self.channel_data = sorted(channel_data, key=lambda cd: cd.channel)

    @cached_property
    def has_waves(self):
        """True if this Event contains waveform data for ALL of it's channels"""
        return all(cd.has_wave for cd in self.channel_data)

    @cached_property
    def has_summary(self):
        """True if this Event contains pulse summary data for ALL of it's channels"""
        return all(cd.has_summary for cd in self.channel_data)

    # _________________________________________________________________________
    # Waveforms Shape
    # _________________________________________________________________________
    def wavedata(self) -> OurNumpyArrType:
        """
        An np.ndarray of waves in the event. Rows are samples, columns are the
        channels in this event. see `channels` for the list of channel numbers
        """
        if self.has_waves:
            # stack multiple waves into a single array. Each channel is one column
            arrays: List[OurNumpyArrType] = [cd.wave for cd in self.channel_data] # type:ignore 
            return np.stack(arrays=arrays, axis=1)

        raise RuntimeError("No Waveform waves found for this Event!")

    @cached_property
    def num_wave_samples(self) -> Optional[int]:
        """
        Returns the number of samples in each channel's waveform or None if
        no waveforms exist
        """
        if self.has_waves:
            return self.channel_data[0].num_wave_samples
        return None

    @cached_property
    def shape(self):
        """
        Returns the shape of :meth:`.wavedata' or None if no waveforms exist
        """
        if self.has_waves:
            return (self.num_wave_samples, self.num_channels)
        return tuple()

    # _________________________________________________________________________
    # Channels
    # _________________________________________________________________________
    @cached_property
    def channels(self) -> Sequence[int]:
        """
        List of all channels in the event in the order they appear
        """
        return [cd.channel for cd in self.channel_data]

    # _________________________________________________________________________
    # Timestamps
    # _________________________________________________________________________
    @cached_property
    def timestamp(self) -> int:
        """
        The timestamp of this event. Defined as the timestamp of the first trigger
         in an event. This quantity is also saved in each channel's data as :py:ref:`ChannelData.event_timestamp`
        """
        return min(cd.event_timestamp for cd in self.channel_data)

    # .........................................................................
    @cached_property
    def channel_timestamps(self) -> Sequence[Optional[int]]:
        """
        Timestamps for each
        """
        return [cd.channel_timestamp for cd in self.channel_data]
    
    # _________________________________________________________________________
    @cached_property
    def relative_channel_timestamps(self) -> Sequence[Optional[int]]:
        """
        All timestamps found throughout all of the channels we have
        """
        return [cd.relative_channel_timestamp for cd in self.channel_data]
    
    # .........................................................................
    @cached_property
    def channel_timestamp_range(self) -> int:
        """
        Returns the difference between the maximum and minimum channel timestamp in this event
        """
        channel_timestamps = [t for t in self.relative_channel_timestamps if t is not None]
        if channel_timestamps:
            return max(channel_timestamps) - min(channel_timestamps)
        return 0

    # _________________________________________________________________________
    # Pulse Heights
    # _________________________________________________________________________
    @cached_property
    def pulse_heights(self) -> Union[Sequence[int], Sequence[None]]:
        """Returns the pulse heights on each channel."""
        return [cd.pulse_height for cd in self.channel_data] # type: ignore

    # _________________________________________________________________________
    # Trigger Data
    # _________________________________________________________________________
    @cached_property
    def trigger_heights(self) -> Union[Sequence[int], Sequence[None]]:
        """Returns the trigger heights trigger on each channel."""
        return [cd.trigger_height for cd in self.channel_data] # type: ignore

    # .........................................................................
    @cached_property
    def channel_multiplicity(self) -> int:
        """Returns the number of channels that triggered at least once in this event"""
        return sum(cd.triggered for cd in self.channel_data) # type: ignore

    # .........................................................................
    @cached_property
    def pileup_count(self) -> Union[Sequence[int], Sequence[None]]:
        """Returns a list of the number of triggers fired for each channel"""
        return [cd.trigger_multiplicity for cd in self.channel_data if cd.triggered] # type: ignore

    # .........................................................................
    @cached_property
    def total_triggers(self) -> int:
        """Returns the total number of triggers that fired across all channels.
        AKA Hit Multiplicity
        """
        return sum(self.pileup_count) # type: ignore

    # .........................................................................
    def __str__(self) -> str:
        return f"<EventInfo: timestamp={self.timestamp}, channels={self.channels}, has_summary={self.has_summary}, shape={self.shape}>"
        
    # .........................................................................
    def __repr__(self) -> str:
        return str(self)

    # .........................................................................
    def __getitem__(self, chan:int) -> ChannelData:
        """grabs the data associated with the channel number `chan`. The first occurance of the channel in this event will be returned"""
        if chan not in self.channels:
            raise KeyError(f"Channel {chan} is not in this Event")
        ch_idx = self.channels.index(chan)
        return self.channel_data[ch_idx]
    
    # .........................................................................
    def __iter__(self) -> Generator[ChannelData, Any, None]:
        for chan_data in self.channel_data:
            yield chan_data
    
###############################################################################
class BaseLoader:
    """
    The base class that all Loader types are an extension of, Loaders extending this subclass this class and then implement load_channel_batch

    All BaseLoader derived classes can be used as a context manager, i.e.:

    with <loader>(file) as loader:
        # Do whatever

    NOTE:
        An individual BaseLoader instance is able to run exactly *once* before needing to -reopen the file, please keep this in mind.
    """

    # _________________________________________________________________________
    def __init__(self, fpath: str, rebuild_events_with_window: Optional[int] = None):
        """

        :fpath: filepath to the data file
        :rebuild_events_with_window: timestamp window where channel data is considered part of the same event. If None, then it will return events as they are defined in the file.

        FUTURE:
            Add a parameter `resort_by_timestamp` that resorts all data
            by the timestamp in the rare case that data isn't written to disk in
            sequence. This is a slow and memory intensive operation that is never required
            if your data is generated using the UI of a SkuTek digitizer. So it's not
            worth doing at this time

        """
        self.fpath = fpath
        self.rebuild_events_with_window = rebuild_events_with_window
        self.active_event_building = self.rebuild_events_with_window is not None
        self.values: Optional[Sequence[ChannelData]] = []
        self.current_chan_in_values: int = 0
        self.channel_ran: bool = False
        self.file_handle: IO  # type: ignore

    def __enter__(self) -> "BaseLoader":
        return self

    def __exit__(self, type: Any, value: Any, traceback: Any) -> None:
        self.file_handle.close()  # type: ignore

    # _________________________________________________________________________
    def loadChannelBatch(self) -> Optional[Sequence[ChannelData]]:
        """
        The base method for loading channels, this loads a sequence of channels (events) or individual channels.

        This is specialized for all loader types.
        """
        # Many file formats save channels in columns and samples in rows
        # which means it's nigh impossible to just load in one channel at a time
        # For file formats where this is possible this function will return a single
        # ChannelData. For file formats (like IGOR or EventCSV) where it's not,
        # then we'll return a list of ChannelData
        raise NotImplementedError("required overload")

    # _________________________________________________________________________
    def channelByChannel(self) -> Generator[ChannelData, Any, None]:
        """
        Get the individual channels, loaded one at a time
        """
        # This code is less complex than it looks, the first repeated while statement is basically just the previous one, but again
        while True:
            # Does a "Not none" check and also is just an entry-point to finish a list for an unfinished generator
            while self.channel_ran and self.values is not None and self.current_chan_in_values < len(self.values):
                yield self.values[self.current_chan_in_values]
                self.current_chan_in_values += 1

            # Load in the batch to a class-based variable
            self.current_chan_in_values = 0
            self.values = self.loadChannelBatch()
            self.channel_ran = True
            if self.values is None:
                return

            # Yield as many channels as we can yield before we return
            while self.current_chan_in_values < len(self.values):
                yield self.values[self.current_chan_in_values]
                self.current_chan_in_values += 1

    # _________________________________________________________________________
    def nextEvent(self) -> Optional[EventInfo]:
        """
        Obtain the next event by loading the next batch.
        """
        # .....................................................................
        # if we are not actively event building then we just define
        # an event as it is defined in the file as a batch of channels
        # i.e. no timestamp coincidence window checking
        if not self.active_event_building:
            channel_batch = self.loadChannelBatch()
            if channel_batch is None:
                return None

            return EventInfo(channel_batch)

        # .....................................................................
        # Otherwise we go through the data channel by channel
        # and define an event by it's timestamp and coincidence window
        else:
            # grab the next channel data first to make sure we're not
            # at the end of the file
            channel_data_generator = self.channelByChannel()
            try:
                first_cd = next(channel_data_generator)
            except StopIteration:
                return None

            # There's probably a smart walrus operator way to do this
            channels_in_event: List[ChannelData] = []
            cd = first_cd
            if self.rebuild_events_with_window is None:
                self.rebuild_events_with_window = 0
            while True:
                # channel_timestamp = cd.timestamp if cd.timestamp else cd.event_timestamp
                # check to make sure the timestamp is in the event's coincidence window
                if cd.channel_timestamp <= (first_cd.channel_timestamp + self.rebuild_events_with_window):
                    channels_in_event.append(cd)
                else:
                    break
                try:
                    cd = next(channel_data_generator)
                except StopIteration:
                    break
            return EventInfo(channels_in_event)

    # _________________________________________________________________________
    def lazyLoad(self) -> Generator[EventInfo, Any, None]:
        """
        Lazily yield events, returns the next event in a generator fashion for iterating
        """
        # The while will be false if it's None, otherwise it's true
        while event_tuple := self.nextEvent():
            yield event_tuple

    # _________________________________________________________________________
    def __iter__(self) -> Generator[EventInfo, Any, None]:
        """
        Iterate over a lazy-loading of events
        """
        return self.lazyLoad()

    # _________________________________________________________________________
    @property
    def bytes_read(self) -> int:
        """
        Returns the number of bytes parsed by this loader so far
        """
        return self.file_handle.tell()



