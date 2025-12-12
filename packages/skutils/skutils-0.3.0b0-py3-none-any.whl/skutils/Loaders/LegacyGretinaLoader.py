from collections import OrderedDict
import numpy as np

# import pandas as pd
import mmap
import bitstruct
import time
import sys

from ..constants import *

from typing_extensions import deprecated


################################################################################
class EventMetadata:
    def __init__(self, packets, number):
        # make sure all packets have the same timestamp
        if not all(packets[0].timestamp == p.timestamp for p in packets):
            raise RuntimeError("invalid packet list. packets have different timestamps")

        # sort packets by channel - smallest first
        self.packets = sorted(packets, key=lambda p: (p.channel, p.wave_type))
        self.number = number
        self.channels = list(set([p.channel for p in packets]))
        self.start = min(p.start for p in self.packets)
        self.end = max(p.end for p in self.packets)
        self.size = self.end - self.start

        self.trace_packets = [p for p in self.packets if (p.wave_type == GebTypes.raw_waveform)]
        self.hist_packets = [p for p in self.packets if (p.wave_type == GebTypes.raw_histogram)]
        self.ps_packets = [p for p in self.packets if (p.wave_type == GebTypes.raw_pulse_summary)]

        self.timestamp = self.packets[0].timestamp
        self.relative_channel_timestamp = self.packets[0].relative_channel_timestamp
        self.version = self.packets[0].version
        self.module = self.packets[0].module
        self.signed = self.packets[0].signed
        self.bitdepth = self.packets[0].bitdepth
        self.wave_type = self.packets[0].wave_type
        self.wave_type_string = self.packets[0].wave_type_string
        if self.trace_packets:
            self.sample_offset = self.trace_packets[0].sample_offset
            self.number_samples = self.trace_packets[0].number_samples
        else:
            self.sample_offset = 0
            self.number_samples = 0

    # --------------------------------------------------------------------------
    def as_dict(self):
        metadata = {
            "sample_offset": self.sample_offset,
            "number_samples": self.number_samples,
            "event_number": self.number,
            "packets": self.packets,
            "channels": self.channels,
            "timestamp": self.timestamp,
            "relative_channel_timestamp": self.relative_channel_timestamp,
            "version_num": self.version,
            "module_num": self.module,
            "signed": self.signed,
            "bitdepth": self.bitdepth,
            "wave_types": self.wave_type,
            "wave_type_strings": self.wave_type_string,
        }
        return metadata

    # --------------------------------------------------------------------------
    def load_arrays_from_file(self, fp, big_endian, wave_type):
        """Loads hists or traces for this event into a dataframe"""
        pos = fp.tell()

        fp.seek(self.start)
        event_buffer = fp.read(self.size)

        packets = [p for p in self.packets if (p.wave_type == wave_type)]
        raw_arrays = [
            p.extract_data_from_event_buffer(event_buffer, self.start, big_endian, wave_type) for p in packets
        ]
        channels = [p.channel for p in packets]
        if len(raw_arrays) == 0:
            # event = pd.DataFrame()
            event = np.asarray([[]])
        else:
            n_samples = packets[0].number_samples
            sample_offset = packets[0].sample_offset

            # NOTE: in testing this system. stacking or building the dataframe
            # usually took 0us, but occasionally took about 1000us. Never between the two
            # The reason for the inconsistency is unknown, but I'm assuming is more
            # OS/python related than this code -JM

            # start = time.time() # DEBUG
            # build a pandas dataframe. Rows are indices. Columns are channels
            event = np.stack(raw_arrays, axis=1)
            # index = np.arange(sample_offset, (sample_offset+n_samples))
            # event = pd.DataFrame(stacked_data, columns=channels, index=index, dtype=stacked_data.dtype)
            # end = time.time() # DEBUG
            # print(f"stacked and DF built in {round(1e6*(end-start),0)}us") # DEBUG

        fp.seek(pos)
        return event

    # --------------------------------------------------------------------------
    def load_histograms_from_file(self, fp, big_endian):
        """Loads HIST data for this event into a dataframe"""
        return self.load_arrays_from_file(fp, big_endian, GebTypes.raw_histogram)

    # --------------------------------------------------------------------------
    def load_traces_from_file(self, fp, big_endian):
        """Loads TRACE data for this event into a dataframe"""
        return self.load_arrays_from_file(fp, big_endian, GebTypes.raw_waveform)

    # --------------------------------------------------------------------------
    def load_summaries_from_file(self, fp, big_endian):
        """Loads PULSER SUMMARY data for this event into a dataframe"""
        pos = fp.tell()
        fp.seek(self.start)

        packets = [p for p in self.packets if (p.wave_type == GebTypes.raw_pulse_summary)]
        summary_struct = PULSE_SUMMARY0_BE if big_endian else PULSE_SUMMARY0_LE
        summaries = []
        for p in packets:
            fp.seek(p.data_start)
            raw = fp.read(p.data_length)
            summary = PulseSummary0(*summary_struct.unpack(raw))
            summaries.append(summary._asdict())

        fp.seek(pos)
        # df = pd.DataFrame.from_records(summaries, columns=PulseSummary0._fields)
        return summaries


################################################################################
class PacketMetadata:
    TRACE_DTYPES = [
        [np.dtype("<u2"), np.dtype("<i2")],  # little endian: unsigned, signed
        [np.dtype(">u2"), np.dtype(">i2")],
    ]  # big endian: unsigned, signed
    HIST_DTYPES = [
        [np.dtype("<u4"), np.dtype("<i4")],  # little endian: unsigned, signed
        [np.dtype(">u4"), np.dtype(">i4")],
    ]  # big endian: unsigned, signed
    PS_DTYPES = [
        [np.dtype("<u1")],  # little endian: unsigned
        [np.dtype(">u1")],
    ]  # big endian: unsigned
    ALL_DTYPES = {
        GebTypes.raw_waveform: TRACE_DTYPES,
        GebTypes.raw_histogram: HIST_DTYPES,
        GebTypes.raw_pulse_summary: PS_DTYPES,
    }

    def __init__(self, packet_header, word1, word2, word3, start):
        self.start = start
        self.wave_type = packet_header.type
        self.length = packet_header.length
        self.timestamp = packet_header.timestamp
        self.version = word1.version
        self.module = word1.module
        self.signed = word1.signed if (self.wave_type != GebTypes.raw_pulse_summary) else False
        self.channel = word1.channel

        self.pre_payload_size = 0
        self.pre_payload_size += GEB_HEADER_SIZE
        self.pre_payload_size += SKUTEK_WORD_SIZE

        if word2:
            self.bitdepth = word2.bitdepth + 1  # need to add one to bitdepth per DDC standard
            self.number_samples = word2.number_samples
            self.pre_payload_size += SKUTEK_WORD_SIZE
        else:
            self.bitdepth = -1
            self.number_samples = self.length - self.pre_payload_size

        if word3:
            self.sample_offset = word3.sample_offset
            self.relative_channel_timestamp = word3.relative_channel_timestamp
            self.pre_payload_size += SKUTEK_WORD_SIZE
        else:
            self.sample_offset = 0
            self.relative_channel_timestamp = 0

        # Calculated values
        self.wave_type_string = GebTypes.WAVE_TYPE_STRINGS.get(
            self.wave_type, "unknown"
        )  # "unknown" if unrecognized type
        self.full_length = packet_header.length + GEB_HEADER_SIZE
        self.sample_size = (
            self.ALL_DTYPES[self.wave_type][0][0].itemsize if (self.wave_type in self.ALL_DTYPES) else 1
        )  # get size of each sample. Default to 1 Byte

        if self.wave_type == GebTypes.raw_pulse_summary:
            self.data_length = PULSE_SUMMARY0_LE.size
        else:
            self.data_length = self.number_samples * self.sample_size

        self.data_start = self.start + self.pre_payload_size

        self.end = self.start + self.full_length
        self.null_padding_size = self.full_length - (self.pre_payload_size + self.data_length)

    # --------------------------------------------------------------------------
    def extract_data_from_event_buffer(self, buf, event_start, big_endian, wave_type=GebTypes.raw_waveform):
        """pulls the packet data from the byte array of event data"""
        wave_start = self.data_start - event_start
        wave_end = wave_start + self.data_length

        # finally read out the data and cast the type required
        dtype = self.ALL_DTYPES[wave_type][big_endian][self.signed]
        data = np.frombuffer(buf[wave_start:wave_end], dtype=dtype)
        return data

    # --------------------------------------------------------------------------
    def __str__(self):
        return f"PacketMetadataCh{self.channel}"

    def __repr__(self):
        return str(self)


################################################################################
@deprecated(
    "This class is deprecated, it will be removed in a future update. For future support switch to 'GretinaLoader'"
)
class LegacyGretinaLoader:
    """
    NOTE: Public facing access to LegacyGretinaLoader is deprecated, future versions may remove LegacyGretinaLoader from public access entirely.
    Object to load in event data from Skutek Gretina formats. unrecognized
    packet types will be ignored

    UNTESTED WITH BIG ENDIAN DATA

    Attributes:
        filename(str): filename being loaded
        memmap(bool): whether or not the whole file was loaded into memory.
        cache_event_metadata(bool): if True, then cache the positions of
        events as they are loaded. This makes traversing backwards through
        the file much faster. default is True
        fp(IoBuffer): open file or memory mapped file object
        big_endian(bool): whether or the not the file is big endian or small endian.
            defaults to system byte order, but is updated as soon as an endian packet
            is parsed
            None if no ascii version packet is parsed
        ascii_header(list): list of ascii version data. Typically
            [ddc_apps_version, git_branch_name, firmware_revision]
            empty list `[]` if no ascii version packet is parsed
        event_number(int): index of most recently parsed event
        packet_parser_functions(dict): dictionary of functions to parse packet
            contents. wave and histogram packets are parsed independently of this
            list. Functions are called with arguments (file_pointer, packet_start, packet_end)
            and are expected not to advance the file position.
    """

    # --------------------------------------------------------------------------
    def __init__(self, filename, memmap=False, cache_event_metadata=True):
        """Instantiates the Gretina File Loader

        Args:
            filename(str): filename to load in
            memmap(bool): whether or not to load the file into memory. Can be
                much faster especially when seeking events, but at cost of extra memory
            cache_event_metadata(bool): if True, then cache the positions of
                events as they are loaded. This makes traversing backwards through
                the file much faster. default is True
        """
        self.filename = filename
        self.memmap = None  # assigned in __make_memmap()
        self.cache_event_metadata = cache_event_metadata

        self.cache = {}
        self.fp = open(filename, "rb")
        # assumed to be true by default, but will be updated to reflect the
        # contents of endian indicator packets
        self.big_endian = sys.byteorder == "big"  # updated if/when endian packet is parsed
        self.ascii_header = []  # assigned if/when ascii version packet is parsed
        self.event_number = None  # assigned in __reset()

        self.packet_parser_functions = {
            GebTypes.general_ascii: self.__parse_version_packet,
            GebTypes.version_info_ascii: self.__parse_version_packet,
            GebTypes.endian_indicator: self.__parse_endian_packet,
            GebTypes.endian_indicator_nonnative: self.__parse_endian_packet,
        }
        # if we want to memory map this file, then we'll replace the file IOBuffer
        # with a memory mapped I/O buffer. This will load the file into memory
        # but we can still use standard file I/O operations
        if memmap:
            self.__make_memmap()

        # reset event number and file position
        self.__reset()
        # peek at the first packet. This will usually load endian and version info
        self.peek_at_next_packet_metadata()

    # --------------------------------------------------------------------------
    def __reset(self):
        """resets file position and event number"""
        self.fp.seek(0)
        self.event_number = 0

    # --------------------------------------------------------------------------
    def __make_memmap(self):
        """sets up the memory mapped I/O buffer"""
        self.memmap = True
        # 2nd arg as 0 loads the whole file into memory
        mmap_fp = mmap.mmap(self.fp.fileno(), 0, access=mmap.ACCESS_READ)
        self.old_fp = self.fp
        # self.fp.close() # close the file on disk
        self.fp = mmap_fp  # replace the file pointer with the mmap

    # --------------------------------------------------------------------------
    def __parse_nondata_packet(self, packet_header, start, end):
        """parses non-data packets. calls the contents of self.packet_parser_functions"""
        func = self.packet_parser_functions.get(packet_header.type, None)
        if func:
            func(self.fp, start, end)
        else:
            if packet_header.type == GebTypes.raw_histogram:
                print(f"currently unable to parse histograms")
            elif packet_header.type == GebTypes.raw_pulse_summary:
                print(f"currently unable to parse pulse summaries")
            else:
                print(f"unable to parse packet type {hex(packet_header.type)}")

    # --------------------------------------------------------------------------
    def __parse_endian_packet(self, fp, start, end):
        """parses the endian packet type and updates the self.endian attribute"""
        pos = fp.tell()
        fp.seek(start)
        raw_geb = self.fp.read(GEB_HEADER_SIZE)  # read the endian indicator
        # parse as little endian and check if the timestamp is correct
        packet_header = GebPacketHeader(*GEB_HEADER_LE.unpack(raw_geb))
        if packet_header.timestamp == ENDIAN_INDICATOR_TIMESTAMP:
            self.big_endian = False
        else:
            self.big_endian = True
        fp.seek(pos)

    # --------------------------------------------------------------------------
    def __parse_version_packet(self, fp, start, end):
        """parses version_info_ascii packets and updates the version info attributes"""
        pos = fp.tell()
        fp.seek(start)
        raw_geb = self.fp.read(GEB_HEADER_SIZE)

        # read the geb header at the start of the packet
        header_type = GEB_HEADER_BE if self.big_endian else GEB_HEADER_LE
        packet_header = GebPacketHeader(*header_type.unpack(raw_geb))

        try:
            # read and decode the skutek word which contains the length of the string
            # unused currently, but here for completeness
            raw_length = fp.read(SKUTEK_WORD_SIZE)
            strlength = int.from_bytes(raw_length, ["little", "big"][self.big_endian])

            # read the ascii version data
            raw = fp.read(packet_header.length - SKUTEK_WORD_SIZE)
            raw = raw[:strlength]  # remove padding
            text = raw.decode("utf-8", errors="ignore").splitlines()
            self.ascii_header.extend(text)

        except IndexError:
            print(f"unable to parse ascii version packet at file index={start}")

        fp.seek(pos)

    # --------------------------------------------------------------------------
    def peek_at_next_packet_metadata(self):
        """returns the metadata for the next data packet in the file without advancing
        the file position. Returns None if the end of the file is hit. If it encounters
        non-data packets during its peeking, then it will pass positional information
        to whatever function is defined for that packet in `packet_parser_functions`

        Args:
            None

        Returns:
            PacketMetadata: metadata and info about the next data packet. This includes
                GEB Headers, Skutek words, and position information in the file.
                OR None if we've reached the end of the file
        """
        pos = self.fp.tell()
        raw_geb = self.fp.read(GEB_HEADER_SIZE)
        # Check if we've reached EOF, and return None if true
        if len(raw_geb) != GEB_HEADER_SIZE:
            self.fp.seek(pos)
            return None

        # read the geb header at the start of the packet
        header_type = GEB_HEADER_BE if self.big_endian else GEB_HEADER_LE
        packet_header = GebPacketHeader(*header_type.unpack(raw_geb))

        # NON-DATA PACKET PARSING
        # If this isn't a data packet, then parse the contents in a separate function
        # and continue onto the next data packet
        if packet_header.type not in (GebTypes.raw_waveform, GebTypes.raw_histogram, GebTypes.raw_pulse_summary):
            # run the function meant to handle this packet type. assuming it
            # won't change file position
            end = pos + GEB_HEADER_SIZE + packet_header.length
            self.__parse_nondata_packet(packet_header, pos, end)
            # meanwhile advance to the start of next packet and return the next data packet
            self.fp.seek(end)

            return self.peek_at_next_packet_metadata()

        elif packet_header.type == GebTypes.raw_pulse_summary:
            word1_raw = self.fp.read(SKUTEK_WORD_SIZE)
            word1_raw = bitstruct.byteswap("4", word1_raw)
            skutek_word1 = SkutekWord1(*SKUTEK_WORD1.unpack(word1_raw))
            # no other words in pulse summary
            skutek_word2 = None
            skutek_word3 = None

        else:
            # DATA PACKET PARSING
            # this is a data packet, we continue to read the skutek words
            # and then the data.
            raw_skutek = self.fp.read(2 * SKUTEK_WORD_SIZE)
            # Check if we've reached EOF, and return None if true
            if len(raw_skutek) != 2 * SKUTEK_WORD_SIZE:
                self.fp.seek(pos)
                return None

            # read the two skutek-defined metadata words

            # skutek words are always big endian?
            word1_raw = bitstruct.byteswap("4", raw_skutek[0:4])
            word2_raw = bitstruct.byteswap("4", raw_skutek[4:8])
            skutek_word1 = SkutekWord1(*SKUTEK_WORD1.unpack(word1_raw))
            skutek_word2 = SkutekWord2(*SKUTEK_WORD2.unpack(word2_raw))

            # verison 1 packets have an extra word
            if skutek_word1.version == 1:
                tmp = self.fp.read(SKUTEK_WORD_SIZE)
                if len(tmp) != SKUTEK_WORD_SIZE:
                    self.fp.seek(pos)
                    return None
                word3_raw = bitstruct.byteswap("4", tmp)
                skutek_word3 = SkutekWord3(*SKUTEK_WORD3.unpack(word3_raw))
            else:
                skutek_word3 = None

        packet = PacketMetadata(packet_header, skutek_word1, skutek_word2, skutek_word3, pos)
        self.fp.seek(pos)
        return packet

    # --------------------------------------------------------------------------
    def peek_at_next_event_metadata(self):
        """Finds all packets associated with the next event and returns metadata
        about the next event which can be used to read it. Does not advance file position

        returns None if there are no more events in the file
        """
        # If the metadata is already in the cache, then don't bother parsing
        # the file
        if self.cache_event_metadata:
            if self.event_number in self.cache:
                return self.cache[self.event_number]

        pos = self.fp.tell()
        # parse the first packet and use it's timestamp to identify event association
        packet1 = self.peek_at_next_packet_metadata()
        # If there are no more packets, then we are at the end of the file and
        # out of events. So we return None
        if packet1 is None:
            self.fp.seek(pos)
            return None

        packets = [packet1]
        self.fp.seek(packet1.end)
        while True:
            next_packet = self.peek_at_next_packet_metadata()
            # If there are no more packets, then we are at the end of the file
            # and thus also the event of this event
            if next_packet is None:
                break

            # If true, then we are in the same event and can advance to the next packet
            if packet1.timestamp == next_packet.timestamp:
                packets.append(next_packet)
                self.fp.seek(next_packet.end)
            else:
                break

        event_metadata = EventMetadata(packets, self.event_number)

        if self.cache_event_metadata:
            self.cache[self.event_number] = event_metadata

        self.fp.seek(pos)
        return event_metadata

    # --------------------------------------------------------------------------
    def seek_event(self, desired_event):
        """goes to the specified event in the file

        Args:
            desired_event(int): the desired event number

        Returns:
            None

        Raises:
            RuntimeError if event does not exist in this file
        """
        pos = self.fp.tell()  # only used for failure conditions
        event_num = self.event_number  # only used for failure conditions

        # if the next event is the desired event, then we don't have to do anything
        if desired_event == self.event_number:
            return

        if self.cache_event_metadata:
            # Check if this event already exists in cache. load it if exists
            if desired_event in self.cache:
                self.fp.seek(self.cache[desired_event].start)
                self.event_number = desired_event
                return
            # If we are caching, but haven't cached across the one we want
            # then seek to the closest cached event prior to the desired event
            else:
                # gambling that descending order will be slightly faster for most applications
                for num in sorted(self.cache.keys(), reverse=True):
                    if (desired_event - num) > 0:
                        self.seek_event(num)
                        break

        # if we are past the desired event, then reset file location to zero
        if desired_event < self.event_number:
            self.__reset()

        # iterate through the file event by event until we get to the desired one
        while self.event_number < desired_event:
            event_metadata = self.peek_at_next_event_metadata()
            self.fp.seek(event_metadata.end)
            self.event_number += 1

            # if we hit the end of the file and still haven't found the event
            # then throw a runtime error
            if event_metadata is None:
                # reset position so other operations aren't affected if this
                # error is ignored by calling process
                self.fp.seek(pos)
                self.event_number = event_num
                raise RuntimeError(f"event {desired_event} does not exist")

    # --------------------------------------------------------------------------
    def fetch_event(self, desired_event):
        """fetches the specified event in the file. Does not advance event number
        or file position

        Returns:
            Tuple:
                dict: dictionary of metadata about the packet. keys are 'packets',
                    'channels', 'wave_type_string', 'timestamp', 'event_number'
                pandas.DataFrame: The event data. Columns are channels (smallest first),
                    row is the index of the event sample
        Raises:
            RuntimeError if event does not exist in this file
        """
        pos = self.fp.tell()
        event_num = self.event_number

        self.seek_event(desired_event)
        metadata, event = self.next_event()

        self.fp.seek(pos)
        self.event_number = event_num
        return metadata, event

    # --------------------------------------------------------------------------
    def next_event(self):
        """Reads next event from the current file location and returns a metadata dictionary
        and a pandas dataframe of the event data. This will advance the location
        in the file.

        Events are defined as a series of contiguous packets with the same timestamp

        Warning:
            if end of file has been reached, then this will return (None, None)

        Returns:
            Tuple:
                dict: dictionary of metadata about the packet. keys are 'packets',
                    'channels', 'wave_type_string', 'timestamp', 'event_number'. OR None if EOF
                pandas.DataFrame: The event data. Columns are channels (smallest first),
                    row is the index of the event sample. OR None if EOF
        """
        event_metadata = self.peek_at_next_event_metadata()
        # we've reached the end of the file. Return None in this case
        if event_metadata is None:
            return None, None

        event = event_metadata.load_traces_from_file(self.fp, self.big_endian)
        self.event_number += 1
        self.fp.seek(event_metadata.end)

        metadata = event_metadata.as_dict()
        metadata["histograms"] = event_metadata.load_histograms_from_file(self.fp, self.big_endian)
        metadata["summaries"] = event_metadata.load_summaries_from_file(self.fp, self.big_endian)
        return metadata, event

    # --------------------------------------------------------------------------
    def load_and_sort_all_events(self):
        """Retrieves a list of all events sorted by timestamp. Unlike fetch_event
        and seek_event, all packets with the same timestamp are defined as an
        event even if the packets are non-contiguous in the file.

        Regardless of instantiation parameters, this function will enable memmap
        to seek the process up

        Returns:
            tuple:
                list of dicts: metadata for all events, ordered by timestamp (smallest first)
                list of DataFrames: data for all events, ordered by timestamp (smallest first)

        """
        # force memory mapping mode. No matter what this data will be loaded
        # into memory, so we aren't gaining anything with memmap=False
        if not self.memmap:
            self.__make_memmap()

        # return to the beginning of the file
        self.__reset()

        # Assume that timestamps are mostly in order from smallest-greatest
        # we can use an ordered dictionary to retain timestamp keys that are
        # already mostly or already sorted
        all_packets = OrderedDict()

        # iterate through all packets and add them to the timestamp dictionary
        packet = self.peek_at_next_packet_metadata()
        while packet:
            if packet.timestamp in all_packets:
                all_packets[packet.timestamp].append(packet)
            else:
                all_packets[packet.timestamp] = [packet]
            self.fp.seek(packet.end)
            packet = self.peek_at_next_packet_metadata()

        # build list of all events sorted by timestamp
        event_metadata = []
        for i, t in enumerate(sorted(all_packets)):
            p = all_packets[t]
            event_metadata.append(EventMetadata(p, i))

        # generate metadata dictionaries
        metadata_dicts = [m.as_dict() for m in event_metadata]
        # metadata_dicts = []
        # for em in event_metadata:
        #     em_dict = em.as_dict()
        #     # add histograms if they exist to the dict
        #     em_dict['hists'] = em.load_histograms_from_file(self.fp, self.big_endian)
        #     metadata_dicts.append(em_dict)
        # generate event data
        events = [m.load_traces_from_file(self.fp, self.big_endian) for m in event_metadata]

        return metadata_dicts, events

    # --------------------------------------------------------------------------
    def calculate_number_of_events(self):
        # if we're already at the end of the file, we can just fetch the event_number + 1
        pos = self.fp.tell()
        ev_num = self.event_number
        ev = self.peek_at_next_event_metadata()
        if ev is None:
            return self.event_number + 1

        # otherwise we have to iterate through all event headers until we find the last one
        while True:
            next_ev = self.peek_at_next_event_metadata()
            if next_ev is None:
                break
            ev_num += 1
            self.fp.seek(next_ev.end)
            ev = next_ev

        self.fp.seek(pos)  # reset file back to old state
        return ev.number + 1  # because events are 0-based indexing

    # --------------------------------------------------------------------------
    def reopen(self):
        if self.fp.closed:
            self.fp = open(self.filename, "rb")

    # --------------------------------------------------------------------------
    def close(self):
        if getattr(self, "old_fp", None) is not None:
            if not self.old_fp.closed:
                self.old_fp.close()
        self.fp.close()

    # --------------------------------------------------------------------------
    @property
    def next_event_num(self):
        return self.event_number + 1

    # --------------------------------------------------------------------------
    def __del__(self):
        if hasattr(self, "fp"):
            self.fp.close()

    # --------------------------------------------------------------------------
    def __iter__(self):
        metadata, event = self.next_event()
        while event is not None:
            yield metadata, event
            # event will become None if EOF
            metadata, event = self.next_event()

    # --------------------------------------------------------------------------
    def __enter__(self):
        return self

    # --------------------------------------------------------------------------
    def __exit__(self, exc_type, exc_value, exc_tb):
        self.close()
