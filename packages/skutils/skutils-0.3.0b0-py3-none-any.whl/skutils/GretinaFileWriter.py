# import pandas as pd
import numpy as np
from struct import Struct
import bitstruct
import sys
import time
import hashlib
import zlib


from .constants import GebTypes, GebPacketHeader, SkutekWord1, SkutekWord2, SkutekWord3, ENDIAN_INDICATOR_TIMESTAMP
from .constants import (
    GEB_HEADER_SIZE,
    FULL_PACKET0_HEADER_SIZE,
    FULL_PACKET1_HEADER_SIZE,
    SKUTEK_WORD_SIZE,
    SAMPLE_SIZE,
    SKUTEK_WORDS_LENGTH,
)
from .constants import GEB_HEADER_BE, GEB_HEADER_LE, SKUTEK_WORD1, SKUTEK_WORD2, SKUTEK_WORD3, GEB_HEADER_NATIVE
from .constants import ASCII_VERSION_PREFIX


def channel_by_channel(event):
    """yield channel index and channel data"""
    for channel in range(event.shape[1]):
        yield channel, event[:, channel]


class GretinaFileWriter:
    """Writes Skutek formatted Gretina data to data files - the same format
    as the ".bin" files saved natively by our digitizer.

    """

    # --------------------------------------------------------------------------
    def __init__(self, fname, ascii_version_header=[]):
        """
        Args:
            fname(str): The filename to save data to. File will be overwritten if
                it already exists
            ascii_version_header(list of str): the ascii version data in the 2nd
                packet of Skutek Gretina files. usually [ddc_apps_version, git branch, firwmare revision]
        """
        self.fname = fname
        self.packets_written = 0
        self.bytes_written = 0
        self.fp = self._create_file()

        self.hasher = hashlib.md5()  # md5 running checksum for the file.
        # use the property self.checksum to get the hex

        self.__write_endian_packet()
        self.__write_ascii_version_packet(ascii_version_header)

    # --------------------------------------------------------------------------
    def _create_file(self):
        """creates the file pointer"""
        return open(self.fname, "wb")

    # --------------------------------------------------------------------------
    def __write_endian_packet(self):
        """writes system endian schema"""
        packet_data = GEB_HEADER_NATIVE.pack(GebTypes.endian_indicator, 0, ENDIAN_INDICATOR_TIMESTAMP)
        self.fp.write(packet_data)
        self.hasher.update(packet_data)
        self.bytes_written += len(packet_data)
        self.packets_written += 1

    # --------------------------------------------------------------------------
    def __write_ascii_version_packet(self, ascii_version_header):
        """writes ascii version data to the file

        Args:
            ascii_version_header(list of str): the ascii version data in the 2nd
                packet of Skutek Gretina files. usually [ddc_apps_version, git branch, firwmare revision]
        """

        version_string = "\n".join(ascii_version_header) + "\n"
        strlen = len(version_string)
        # length encoded as 32 bit integer
        length_word = Struct("=l").pack(ASCII_VERSION_PREFIX << 24 | strlen)
        payload_data = length_word + bytes(version_string, "utf-8")
        # encode the header now that we know the size
        header_data = GEB_HEADER_NATIVE.pack(GebTypes.version_info_ascii, len(payload_data), 0)
        packet_data = header_data + payload_data
        self.fp.write(packet_data)
        self.hasher.update(packet_data)
        self.bytes_written += len(packet_data)
        self.packets_written += 1

    # --------------------------------------------------------------------------
    def write_ascii_packet(self):
        raise NotImplementedError("not yet implemented")

    # --------------------------------------------------------------------------
    def write_data_packet(
        self, channel, data, timestamp, wave_type, module_num=0, version_num=0, bitdepth=14, compression=0
    ):
        """writes a packet to the file

        Args:
            channel(int): channel index of data
            data(numpy.ndarry): data. must be a 1D numpy array of dtype uint16 or int16
            timestamp(int): trigger timestamp
            wave_type(str):  GebTypes.raw_waveform or GebTypes.raw_histogram
            module_num(int): module number to go in skutek words. default is 0
            version_num(int): version number to go in skutek words. default is 0
            bitdepth(int): bitdepth to be encoded in packet. defaults to 14bit
            compression(int): compression level for zlib. 0 is None, 9 is max
        """
        # assert(wave_type == GebTypes.raw_waveform or GebTypes.raw_histogram), "wave_type must be histogram or wave gebtypes"
        # assert isinstance(timestamp,int), "timestamp must be integer"
        # assert isinstance(data,(np.ndarray), "data must be numpy array"
        assert data.dtype.itemsize == 2, "only 2byte datum types allowed"
        signed = 1 if (data.dtype == np.int16) else 0
        self.write_raw_packet(
            channel, data.tobytes(), signed, timestamp, wave_type, module_num, version_num, bitdepth, compression
        )

    # --------------------------------------------------------------------------
    def write_event(self, event, timestamp, wave_type, module_num=0, version_num=0, bitdepth=14, compression=0):
        """writes an event to the file. Event must be a pandas dataframe with
        the integer channel number being the column header

        Args:
            event(numpy.ndarry): The event data. If a pandas data
                frame, then Columns must be the integer channels number.
                If numpy array, then first column is assumed to be channel 0
            timestamp(int): trigger timestamp
            wave_type(str): skutils.GebTypes.raw_waveform OR skutils.GebTypes.raw_histogram
            module_num(int): module number to go in skutek words. default is 0
            version_num(int): module number to go in skutek words. default is 0
            bitdepth(int): bitdepth to be encoded in packets. defaults to 14bit
            compression(int): compression level for zlib. 0 is None, 9 is max
        """
        # assert(wave_type == "wave" or wave_type == "histogram"), "wave_type must be 'histogram' or 'wave'"
        # assert isinstance(timestamp,int), "timestamp must be integer"
        for ch, data in channel_by_channel(event):
            self.write_data_packet(ch, data, timestamp, wave_type, module_num, version_num, bitdepth, compression)

    # --------------------------------------------------------------------------
    def write_raw_packet(
        self, channel, raw_data, signed, timestamp, wave_type, module_num=0, version_num=0, bitdepth=14, compression=0
    ):
        n_samples = int(len(raw_data) // SAMPLE_SIZE)

        if compression:
            raw_data = zlib.compress(raw_data, level=compression)
        data_size = len(raw_data)
        packet_length = SKUTEK_WORDS_LENGTH + data_size  # length AFTER geb header

        # generate header binary
        geb_header = GEB_HEADER_NATIVE.pack(wave_type, packet_length, timestamp)
        # skutek words are always big endian?
        # subtract 1 from bitdepth per format spec
        word1 = bitstruct.byteswap("4", SKUTEK_WORD1.pack(version_num, module_num, signed, channel))
        word2 = bitstruct.byteswap("4", SKUTEK_WORD2.pack(bitdepth - 1, n_samples))

        full_header = geb_header + word1 + word2

        # write packet to preallocated byte array
        # start = time.time()
        packet_size = len(full_header) + data_size
        packet = bytearray(packet_size)
        packet[:FULL_PACKET_HEADER_SIZE] = full_header
        packet[FULL_PACKET_HEADER_SIZE:] = raw_data
        # t = time.time() - start
        # import pdb; pdb.set_trace()

        # save data
        n_written = self.fp.write(packet)
        self.hasher.update(packet)
        self.packets_written += 1
        self.bytes_written += n_written

        # # DEBUGGING
        # n_got = len(raw_data)

        if n_written != packet_size:
            print(f"packet was {packet_size} Bytes, but only wrote {n_written}", file=sys.stderr)

    # --------------------------------------------------------------------------
    def write_raw_event(
        self, channels, raw_event, signed, timestamp, wave_type, module_num=0, version_num=0, bitdepth=14, compression=0
    ):
        n_channels = len(channels)
        channel_size = len(raw_event) // n_channels
        n_samples = channel_size // 2
        idx = 0
        for i in range(n_channels):
            ch = channels[i]
            ch_data = raw_event[idx : idx + channel_size]
            self.write_raw_packet(
                ch, ch_data, signed, timestamp, wave_type, module_num, version_num, bitdepth, compression
            )
            idx += channel_size

    # --------------------------------------------------------------------------
    def close(self):
        self.fp.close()

    # --------------------------------------------------------------------------
    def __del__(self):
        if hasattr(self, "fp"):
            self.fp.close()

    # --------------------------------------------------------------------------
    def __enter__(self):
        return self

    # --------------------------------------------------------------------------
    def __exit__(self, exc_type, exc_value, exc_tb):
        self.fp.close()

    # --------------------------------------------------------------------------
    @property
    def checksum(self):
        return self.hasher.hexdigest()
