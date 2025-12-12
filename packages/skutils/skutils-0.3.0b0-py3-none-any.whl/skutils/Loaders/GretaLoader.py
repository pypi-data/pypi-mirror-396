import ctypes
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
import numpy as np

from .BaseLoader import BaseLoader,ChannelData

# Directly translate the C structures here
class GretaPacketRoutingHeader(ctypes.LittleEndianStructure):
    _pack_ = 1
    _align_ = 4
    _fields_ = [
        ("version", ctypes.c_uint8),
        ("flags", ctypes.c_uint8),
        ("type", ctypes.c_uint8),
        ("subtype", ctypes.c_uint8),
        ("length", ctypes.c_uint16),
        ("sequence_number", ctypes.c_uint16),
        ("timestamp", ctypes.c_uint64),
        ("checksum", ctypes.c_uint64),
    ]


class GretaPacketWaveSubheader(ctypes.LittleEndianStructure):
    _pack_ = 1
    _align_ = 4
    _fields_ = [
        ("subheader_version", ctypes.c_int8),
        ("trig_count", ctypes.c_uint8),
        ("triggered", ctypes.c_int8),
        ("reserved_0", ctypes.c_int8),
        ("trigger_height", ctypes.c_int16),
        ("pulse_height", ctypes.c_int16),
        ("module_number", ctypes.c_uint16),
        ("channel", ctypes.c_uint16),
        ("start_location", ctypes.c_int16),
        ("reserved_1", ctypes.c_int16),
        ("qdc_base_sum", ctypes.c_int32),
        ("qdc_fast_sum", ctypes.c_int32),
        ("qdc_slow_sum", ctypes.c_int32),
        ("qdc_tail_sum", ctypes.c_int32),
        ("size", ctypes.c_uint32),
        ("reserved_3", ctypes.c_uint8 * 64),
    ]


class GretaPacketTotal(ctypes.LittleEndianStructure):
    _pack_ = 1
    _align_ = 4
    _fields_ = [
        ("header", GretaPacketRoutingHeader),
        ("subheader", GretaPacketWaveSubheader),
    ]


class GretaLoader(BaseLoader):
    """
    Loader for the SkuTek GRETA single-packet format
    """

    def __init__(self, fpath: str, rebuild_events_with_window: Optional[int] = None):
        self.file_handle: IO[bytes] = open(fpath, "rb")
        super().__init__(fpath, rebuild_events_with_window)

    def loadChannelBatch(self) -> Optional[Sequence[ChannelData]]:
        packet_initial_bytes = self.file_handle.read(ctypes.sizeof(GretaPacketTotal))
        if len(packet_initial_bytes) < ctypes.sizeof(GretaPacketTotal):
            return None
        total_initial_packet = GretaPacketTotal.from_buffer_copy(packet_initial_bytes)
        flexible_member_bytes: Optional[bytes] = None

        if total_initial_packet.subheader.size > 0:
            flexible_member_bytes = self.file_handle.read(
                ctypes.sizeof(ctypes.c_uint16 * total_initial_packet.subheader.size)
            )
        # Building the actual ChannelData
        if flexible_member_bytes is not None:
            flex_member_array_for_use = np.frombuffer(flexible_member_bytes, dtype=np.int16)
        else:
            flex_member_array_for_use = None
        channel = total_initial_packet.subheader.channel
        assert isinstance(total_initial_packet.subheader, GretaPacketWaveSubheader)
        build_dict: Dict[str, Any] = {}
        for item in total_initial_packet.subheader._fields_:
            build_dict[item[0]] = getattr(total_initial_packet.subheader, item[0])

        timestamp = total_initial_packet.header.timestamp
        return [
            ChannelData(
                channel,
                timestamp,
                build_dict,
                flex_member_array_for_use,
            )
        ]

