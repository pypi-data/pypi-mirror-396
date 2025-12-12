from typing import List, Union, Optional, Literal, Dict, Any, Generator
import requests
from .helpers.internal_solidago_helpers import (
    Timer,
    ipv4_to_num,
    mac_to_num,
    num_to_ipv4,
)
import time
from enum import Enum
import math
from collections.abc import Sequence

# This is verbose psuedo code. You are expected to modify as necessary.
MAX_48bit = 2**48 - 1
BITS_PER_WORD = 64
ROUTING_HEADER_SIZE = 14
IPV4_HEADER_SIZE = 20
UDP_HEADER_SIZE = 8
# this is a routing header added by the FS Switch for internal routing. Not part of GRETA despite the similar name. It probably can be deleted.
SWITCH_GRE_HEADER_SIZE = 24
GRETA_HEADER_SIZE = 24


# """
# from skutils import SolidagoController

# # #############################################################################
# # Desired Usage
# # Instantiate class using URL/PORT to the rest API
# solidago = SolidagoController("012.345.678.9AB", port=9999)

# # Stream configuration
# # 1) the ability to index into individual streams
# # configure individual streams via numerical index
# for i in range(num_streams):
#     solidago[i].configure_by_pulse_rate(freq=1, width=1)
#     # OR
#     # solidago[i].configure_by_constant_speed(1)
#     # OR
#     # solidago[i].configure_raw(**dict_of_configs)

#     solidago[i].set_source(*args)
#     solidago[i].set_destination(*args)
#     solidago[i].set_greta_format(*args)

#     print(f"Stream {i} configured to stream T {solidago[i].estimated_gpbs()} Gbps")

# # 2)

# solidago.set_mode("Independent") # Set streams to operate in independent mode (options will be "Sync", "Independent", "ExternallyDriven")
# solidago.configure()
# solidago.enable_streams( range(0,10) ) #
# print(f"Solidago configured to stream {solidago.estimated_gpbs()} Gbps net across all stream ports")

# solidago.start()
# status = solidago.status()
# solidago.stop()
# """


class BoardStates(Enum):
    OFFLINE = 0
    INITIALIZING = 1
    INITIALIZED = 2
    CONFIGURING = 3
    CONFIGURED = 4
    UPDATING_STREAM = 5
    STREAMING = 6


class URL_LIST(Enum):
    BASE_URL = "alinxrest"

    GET_STATUS_URL = f"{BASE_URL}/getStatus"
    SET_CONFIG_URL = f"{BASE_URL}/setConfig"
    GET_CONFIG_URL = f"{BASE_URL}/getConfig"
    START_STREAM_URL = f"{BASE_URL}/startStream"
    STOP_STREAM_URL = f"{BASE_URL}/stopStream"

    GET_PULSE_SETTINGS_URL = f"{BASE_URL}/getPulseSettings"

    SET_MASTER_URL = f"{BASE_URL}/setMasterSlave"
    GET_MASTER_URL = f"{BASE_URL}/getMasterSlave"

    UDP_SFP_RECORD_URL = f"{BASE_URL}/updSfpRecord"
    UPD_CANNON_REC_URL = f"{BASE_URL}/updUdpCannonRec"
    UPD_GET_LAST_CONFIG_URL = f"{BASE_URL}/GetLastConfig"
    UPD_UDPC_SYNC_REC = f"{BASE_URL}/updUdpcSyncRec"
    UPD_UDPC_IND_SFP_REC_URL = f"{BASE_URL}/updUdpcIndSfpRec"

    CTRL_CONFIG_URL = f"{BASE_URL}/ctrlConfig"
    CTRL_START_URL = f"{BASE_URL}/ctrlStart"
    CTRL_ABORT_URL = f"{BASE_URL}/ctrlAbort"
    CTRL_GET_STATUS_URL = f"{BASE_URL}/ctrlGetStatus"
    CTRL_GET_CONFIG_URL = f"{BASE_URL}/ctrlGetConfig"


# #############################################################################
class Stream:
    """This Class will represent a single 10G port on Solidago and by the sub-boards"""

    def __init__(
        self,
        board_id: int,  # internally used by REST api to distinquish ports
        sfp_id: int,  # 0-3 index of port on the ALINX board
        default_words_per_packet: int = 1100,  # TOTAL size of packet following network headers in 64 bit words
        total_packet_count: int = MAX_48bit,  # this is the maximum packet count before streams stop. 48 bit max
        seed: int = -1,  # -1 means random seed
    ):
        self.minimum_packet_payload_size = GRETA_HEADER_SIZE
        # add your code here
        self.board_id: int = board_id
        self.words_per_packet: int = default_words_per_packet
        self.total_packet_count: int = total_packet_count
        self.sfp_id: int = sfp_id
        self.random_seed: int = seed
        self.packets_per_event: int = 0
        self.packets_per_event_range: int = 0
        self.inter_event_pause: int = 32
        self.inter_event_pause_range: int = 0
        self.inter_packet_pause: int = 32
        self.inter_packet_pause_range: int = 0
        self.greta_version: int = 0
        self.greta_type: int = 0
        self.greta_subtype: int = 0
        self.greta_subtype_range: int = 0
        self.greta_flags: int = 0
        self.dst_port: int = 0
        self._dst_mac: str = ""
        self.dst_ip: str = ""
        self.src_ip: str = ""
        self.src_port: int = 0
        self._src_mac: str = ""
        # this is a placeholder for a future update when we'll have configurable packet formats
        self.format = "GRETA"

        # disabled by default
        self._enabled = False

    def reset(self) -> None:
        """
        Reset the settings to default, notably inter-event-pause is set to 32, inter-packet-pause is set to 32, and packets per event is set to 1.
        All port information, mac information, and ip information is also wiped.
        Words per packet is also set to just the GRETA_HEADER_SIZE
        """
        # define a "Default" config here which will be updated by other functions
        self.minimum_packet_payload_size = GRETA_HEADER_SIZE
        self.packets_per_event = 1
        self.packets_per_event_range = 0
        self.inter_event_pause = 32
        self.inter_event_pause_range = 0
        self.inter_packet_pause = 32
        self.inter_packet_pause_range = 0
        self.greta_version = 0
        self.greta_type = 0
        self.greta_subtype = 0
        self.greta_subtype_range = 0
        self.greta_flags = 0
        self.dst_port = 0
        self._dst_mac = ""
        self.dst_ip = ""
        self.src_ip = ""
        self.src_port = 0
        self._src_mac = ""
        # this is a placeholder for a future update when we'll have configurable packet formats
        self.format = "GRETA"

    def apply_existing(
        self,
        sfp: int,
        words_per_packet: int,
        random_seed: int,
        total_number_packets: int,
        packets_per_event: int,
        packets_per_event_range: int,
        inter_event_pause: int,
        inter_event_pause_range: int,
        inter_packet_pause: int,
        inter_packet_pause_range: int,
        greta_version: int,
        greta_type: int,
        greta_subtype: int,
        greta_subtype_range: int,
        greta_flags: int,
        dst_port: int,
        dst_mac: str,
        dst_ip: str,
        src_ip: str,
        src_port: int,
        src_mac: str,
        **kwargs: Any,
    ):
        """Apply an existing config, intended usage is to take in each kwarg from a json expansion"""
        self.words_per_packet = words_per_packet
        self.random_seed = random_seed
        self.total_packet_count = total_number_packets
        self.packets_per_event = packets_per_event
        self.packets_per_event_range = packets_per_event_range
        self.inter_event_pause = inter_event_pause
        self.inter_event_pause_range = inter_event_pause_range
        self.inter_packet_pause = inter_packet_pause
        self.inter_packet_pause_range = inter_packet_pause_range
        self.greta_version = greta_version
        self.greta_type = greta_type
        self.greta_subtype = greta_subtype
        self.greta_subtype_range = greta_subtype_range
        self.greta_flags = greta_flags
        self.dst_port = dst_port
        self._dst_mac = dst_mac
        self.dst_ip = dst_ip
        self.src_ip = src_ip
        self.src_port = src_port
        self._src_mac = src_mac

    def set_packet_size_words(self, nwords: int):
        """
        Set the packet size in number of 64 bit words.

        :param nwords: The number of 64 bit words to set the packet size to.

            NOTE: nwords is the number of 64 bit words, that means to get the number of bytes being sent you multiply this number by 8!!!!
            MUST be greater than the minimum for the GRETA header
        """
        assert (nwords * 8) > self.minimum_packet_payload_size

        self.words_per_packet = nwords

    def set_packet_size_bytes(self, nbytes: int):
        """
        Set the packet size by an approxmiate number of bytes, it is rounded up to the nearest multiple of 8
        :param nbytes: Number of bytes to set the payload size to (the input is rounded up to the nearest multiple of 8)

            NOTE: nbytes is rounded up to the nearest multiple of 8(!)
        """
        assert nbytes > self.minimum_packet_payload_size

        # Easy way to round up is to add the remainder by the number you need to round up to.
        # the value // does INTEGER not FLOAT division, important!!! This type is an INTEGER
        self.words_per_packet = (nbytes + (nbytes % 8)) // 8

    def set_source(self, src_ip: str, src_mac: Union[int, str], src_port: Union[int, str]):
        """
        The source of the packets being streamed out, Solidago does not do DHCP discovery, so it cannot automatically assign itself these parameters.
        :param src_ip: The ip that the stream will say it's sending from.
        :param src_mac: the mac address the stream will say it's sending from.
        :param src_port: the port the stream will say it's sending from.
        """
        self.src_ip = src_ip
        self.src_mac = src_mac
        if isinstance(src_port, str):
            src_port = int(src_port)
        self.src_port = src_port

    def set_destination(self, dst_ip: str, dst_mac: Union[str, int], dst_port: Union[int, str]):
        """
        Set the target information's packet information, as the Solidago is designed to be "dumb", it cannot do MAC address discovery.
        :param dst_ip: The destination IP the stream will send to.
        :param dst_mac: The MAC address associated with the target IP.
        :param dst_port: The port designated to receive the UDP stream.
        """
        self.dst_ip = dst_ip  # type: ignore
        self.dst_mac = dst_mac  # type: ignore
        if isinstance(dst_port, str):
            dst_port = int(dst_port)
        self.dst_port = dst_port

    def set_greta_format(
        self,
        version: int,
        flags: int,
        type: int,
        subtype: int,
        subtype_range: int,
    ):
        """Set various information about the GRETA packet being sent by Solidago, this API may change as the product updates

        :param version: The GRETA version
        :param flags: The GRETA flags
        :param type: The GRETA type, the Solidago will not actually change the packet format based on the type
        :param subtype: The default subtype to set, Solidago will not change the packet based on the subtype other than simply setting the subtype
        :param subtype_range: The maximum range of the subtype, calculated as subtype + rand(1, subtype_range)
        """
        self.greta_version = version
        self.greta_flags = flags
        self.greta_type = type
        self.greta_subtype = subtype
        self.greta_subtype_range = subtype_range

    def __pulse_to_ALINX_settings(
        self,
        pulse_width: float,
        pulse_frequency: float,
        inter_packet_pause: int,
        words_per_packet: int,
    ):
        """INPUT
            width_min         [microseconds]
            frequency_min     [Hz]
            ipp_min           [clock ticks]
            t_data            [words/packet]

            OUTPUT
            ibp_min           [clock ticks]
            ibp_range         [clock ticks]
            ppb_min           [clock ticks]
            ppb_range         [clock ticks]

            For this function:
        (1 / frequency_min) > (width_min / 1,000,000)"""

        freq_min_calc = 1 / pulse_frequency
        width_min_calc = pulse_width / 1000000
        if freq_min_calc < width_min_calc:
            raise ValueError("Pulse width too long for frequency (see manual)")

        # Constants
        CLOCK_FREQUENCY = 156.25e6  # 10G core clock speed [ticks/sec]
        # convert bytes to words by dividing by 8 (1 word == 1 clock tick long)
        ROUTING_HEADER_SIZE = 14 / 8  # [words]
        IPV4_HEADER_SIZE = 20 / 8  # [words]
        UDP_HEADER_SIZE = 8 / 8  # [words]

        # assume the range cannot be changed, so each range is 1
        width_range = 1
        frequency_range = 1
        ipp_range = 1

        # sum header component and round up to integer clock ticks
        t_header = math.ceil(ROUTING_HEADER_SIZE + IPV4_HEADER_SIZE + UDP_HEADER_SIZE)  #    [ticks]

        # size of each packet in clock ticks
        t_packet = words_per_packet + t_header  # [ticks]
        # average inter-packet pause time in clock cycles
        ipp_bar = inter_packet_pause + ((ipp_range - 1) / 2)  # [ticks]

        # average width in clock cycles
        width_bar = (pulse_width + ((width_range - 1) / 2)) * CLOCK_FREQUENCY / 1000000  # [ticks]

        # average frequency per burst
        frequency_bar = (pulse_frequency + ((frequency_range - 1) / 2)) / CLOCK_FREQUENCY  # [1 / ticks]

        # average number of packets per burst
        npb_bar = (width_bar + ipp_bar) / (t_packet + ipp_bar)  # [dimensionless]

        # average interburst pause time
        ibp_bar = 1 / frequency_bar - width_bar  # [ticks]

        self.packets_per_event = math.floor(npb_bar)
        self.packets_per_event_range = 0
        self.inter_event_pause = math.floor(ibp_bar)
        self.inter_event_pause_range = 0
        # status_msg = "ERROR: (1 / frequency_min) is not greater than (width_min / 1,000,000)"

    def configure_by_pulse_rate(
        self, pulse_freq_hz: float, pulse_width_us: float, inter_packet_pause: int = 32
    ) -> float:
        """
        This configures this stream to have specific packets per event and inter event pause ranges based on the frequency of pulses and pulse widths as well as the distance between packets
        The minimum inter event pause is 32 clk cycles
        :param pulse_freq_hz: The pulse frequency in terms of number of pulses per second
        :param  pulse_width_us: The width of the pulses in microseconds
        :param inter_packet_pause: Length of a pause in FPGA clock ticks.

        :returns: The estimated speed in gbps of the settings
        """
        assert inter_packet_pause >= 32

        self.__pulse_to_ALINX_settings(pulse_width_us, pulse_freq_hz, inter_packet_pause, self.words_per_packet)
        return self.estimated_gbps()

    def configure_by_constant_speed(self, speed_gbps: float) -> float:
        """
        Configure speed, in GIGABITS per packet, close approximation

        :param speed_gbps: wanted speed in gigabits per second

            NOTE: KNOWN TO CURRENTLY NOT WORK PROPERLY

        :returns: The estimated speed in gbps of the settings
        """
        # We'll need to do some math here. I don't believe we've developed this prior.
        # We want to take in a desired speed and generate a set of parameters that create that speed.
        # We can only actually solve for 1 parameter (inter_event_pause) so use the following settings for all others
        # - all ranges should be 0
        # - packets per event should be 1
        # - inter packet pause should be 32 (the minimum number of clock cycles according to 10G spec)
        #
        # We need to reverse engineer Jackson's speed calculated code to solve for inter_event_pause. see estimated_speed
        self.inter_event_pause_range = 0
        self.packets_per_event_range = 0
        self.inter_packet_pause_range = 0

        self.inter_packet_pause = 32
        # One event
        self.packets_per_event = 1
        tps = 156.25e6
        rate = speed_gbps * 1e9 / tps
        t_data = self.words_per_packet
        self.inter_event_pause = math.ceil(((64 * t_data) / rate) - 5.25 - t_data)
        assert self.inter_event_pause >= 32

        return self.estimated_gbps()

    # Stored for easy posterity
    # def alt_configure_constant_speed(self, speed_gbps: float) -> float:
    #     bps = speed_gbps * 1e9
    #     spb = 1 / bps
    #     total = spb * (64 * (self.words_per_packet + (42 / 8))) * 156.25e6
    #     self.inter_event_pause_range = 0
    #     self.packets_per_event_range = 0
    #     self.inter_packet_pause_range = 0
    #
    #     self.inter_packet_pause = 32
    #     self.packets_per_event = 100
    #
    #     self.inter_event_pause = self.packets_per_event * math.ceil(
    #         (total - ((self.words_per_packet + 42 / 8) + self.inter_packet_pause))
    #     )
    #     assert self.inter_event_pause >= 32
    #     return self.estimated_gbps()

    def configure_raw(
        self,
        packets_per_event: Optional[int] = None,
        packets_per_event_range: Optional[int] = None,
        inter_event_pause: Optional[int] = None,
        inter_event_pause_range: Optional[int] = None,
        inter_packet_pause: Optional[int] = None,
        inter_packet_pause_range: Optional[int] = None,
        words_per_packet: Optional[int] = None,
    ):
        """
        Set various internal variables of the same name, all variables are optional so if None is passed in no change happens on that variable

        :param packets_per_event: The number of packets in a specific event to send as a baseline
        :param packets_per_event_range: An extra range of packets sent as part of the event, allows for a random number of packets to be sent from a particular stream

        :param inter_event_pause: The length of a pause (in FPGA ticks) between events
        :param inter_event_pause_range: A number indicating an extra "range" of ticks that are used in the length of a pause in packets

        :param inter_packet_pause: The pause (in FPGA ticks) between packets in an event
        :param inter_packet_pause_range: The range of the length of the pause (in ticks) of an event

        :param words_per_packet: The number of FPGA words in a packet, this is multiplied by 8 to get the number of bytes in the packet.
        """
        if packets_per_event is not None:
            self.packets_per_event = packets_per_event
        if packets_per_event_range is not None:
            self.packets_per_event_range = packets_per_event_range
        if inter_event_pause is not None:
            self.inter_event_pause = inter_event_pause
        if inter_event_pause_range is not None:
            self.inter_event_pause_range = inter_event_pause_range
        if inter_packet_pause is not None:
            self.inter_packet_pause = inter_packet_pause
        if inter_packet_pause_range is not None:
            self.inter_packet_pause_range = inter_packet_pause_range
        if words_per_packet is not None:
            assert words_per_packet > SWITCH_GRE_HEADER_SIZE
            self.words_per_packet = words_per_packet

    def get_rest_configuration(self) -> Dict[str, Any]:
        """
        Get the total configuration for this sfp, as part of the board, as a json value.
        :returns: A dictionary usable as a packet for configuring this specific SFP via json
        """
        return {
            "description": "",
            "board": self.board_id,
            "data": {
                "net_ifs": [
                    {
                        "sfp": self.sfp_id,
                        "words_per_packet": self.words_per_packet,
                        "random_seed": self.random_seed,
                        "total_number_packets": self.total_packet_count,
                        "packets_per_event": self.packets_per_event,
                        "packets_per_event_range": self.packets_per_event_range,
                        "inter_event_pause": self.inter_event_pause,
                        "inter_event_pause_range": self.inter_event_pause_range,
                        "inter_packet_pause": self.inter_packet_pause,
                        "inter_packet_pause_range": self.inter_packet_pause_range,
                        "greta_version": self.greta_version,
                        "greta_type": self.greta_type,
                        "greta_subtype": self.greta_subtype,
                        "greta_subtype_range": self.greta_subtype_range,
                        "greta_flags": self.greta_flags,
                        "dst_port": self.dst_port,
                        "dst_mac": self._dst_mac,
                        "dst_ip": self.dst_ip,
                        "src_ip": self.src_ip,
                        "src_port": self.src_port,
                        "src_mac": self._src_mac,
                    }
                ]
            },
        }

    def get_netifs(self) -> Dict[str, Any]:
        """
        Get these network settings for a steram as a json value
        :returns: a packet usable for communication for updating an SFP
        """
        return {
            "sfp": self.super_id,
            "words_per_packet": self.words_per_packet,
            "random_seed": self.random_seed,
            "total_number_packets": self.total_packet_count,
            "packets_per_event": self.packets_per_event,
            "packets_per_event_range": self.packets_per_event_range,
            "inter_event_pause": self.inter_event_pause,
            "inter_event_pause_range": self.inter_event_pause_range,
            "inter_packet_pause": self.inter_packet_pause,
            "inter_packet_pause_range": self.inter_packet_pause_range,
            "greta_version": self.greta_version,
            "greta_type": self.greta_type,
            "greta_subtype": self.greta_subtype,
            "greta_subtype_range": self.greta_subtype_range,
            "greta_flags": self.greta_flags,
            "dst_port": self.dst_port,
            "dst_mac": self._dst_mac,
            "dst_ip": self.dst_ip,
            "src_ip": self.src_ip,
            "src_port": self.src_port,
            "src_mac": self._src_mac,
        }

    def __speed(
        self,
        ppe_min: int,
        ppe_range: int,
        iep_min: int,
        iep_range: int,
        ipp_min: int,
        ipp_range: int,
        t_data: int,
    ) -> float:
        # NOTE: ALL INPUTS ARE IN UNITS OF CLOCK CYCLES

        f = 156.25e6  # 10G core clock speed [ticks/sec]
        bits_per_word = 64  # [bits]
        ROUTING_HEADER_SIZE = 14
        IPV4_HEADER_SIZE = 20
        UDP_HEADER_SIZE = 8

        # size of each header in clock cycles
        t_header = (ROUTING_HEADER_SIZE + IPV4_HEADER_SIZE + UDP_HEADER_SIZE) / 8  # [ticks]

        # size of each packet in clock cycles
        t_packet = t_data + t_header

        # .........................................................................
        # Calculating Numerator
        packet_size = bits_per_word * (t_data + t_header)  # [bits]

        # .........................................................................
        # Calculating Denominator

        # average interpacket pause time in clock cycles
        ipp_bar = ipp_min + ((ipp_range - 1) / 2)  # ticks
        # average interburst pause time in clock cycles
        ibp_bar = iep_min + ((iep_range - 1) / 2)  # ticks
        # average number of packets per burst
        nbp_bar = ppe_min + ((ppe_range - 1) / 2)  # ticks

        # add components together to get average total time per packet in clock cycles
        total_time = t_packet + (ibp_bar / nbp_bar) + ((nbp_bar - 1) / nbp_bar) * ipp_bar  # ticks
        # convert clock cycles to seconds
        total_time_sec = total_time / f  # sec

        return (packet_size / total_time_sec) / 1e9  # [gigabits/second]

    # def __speed1(
    #     self,
    #     ppe_min: int,
    #     ppe_range: int,
    #     iep_min: int,
    #     iep_range: int,
    #     ipp_min: int,
    #     ipp_range: int,
    #     t_data: int,
    # ) -> float:
    #     # NOTE: ALL INPUTS ARE IN UNITS OF CLOCK CYCLES

    #     f = 156.25e6  # 10G core clock speed [ticks/sec]
    #     bits_per_word = 64  # [bits]
    #     ROUTING_HEADER_SIZE = 14
    #     IPV4_HEADER_SIZE = 20
    #     UDP_HEADER_SIZE = 8

    #     # size of each header in clock cycles
    #     t_header = (
    #         ROUTING_HEADER_SIZE + IPV4_HEADER_SIZE + UDP_HEADER_SIZE
    #     ) / 8  # [ticks]

    #     # size of each packet in clock cycles
    #     t_packet = t_data + t_header

    #     # .........................................................................
    #     # Calculating Numerator
    #     packet_size = bits_per_word * (t_data + t_header)  # [bits]

    #     # .........................................................................
    #     # Calculating Denominator

    #     # average interpacket pause time in clock cycles
    #     ipp_bar = ipp_min + ((ipp_range - 1) / 2)  # ticks
    #     # average interburst pause time in clock cycles
    #     ibp_bar = iep_min + ((iep_range - 1) / 2)  # ticks
    #     # average number of packets per burst
    #     nbp_bar = ppe_min + ((ppe_range - 1) / 2)  # ticks

    #     # add components together to get average total time per packet in clock cycles
    #     total_time = t_packet + (ibp_bar / nbp_bar) + ipp_bar  # ticks
    #     # convert clock cycles to seconds
    #     total_time_sec = total_time / f  # sec

    #     return (packet_size / total_time_sec) / 1e9  # [gigabits/second]

    def __speed_pps(
        self,
        ppe_min: int,
        ppe_range: int,
        iep_min: int,
        iep_range: int,
        ipp_min: int,
        ipp_range: int,
        t_data: int,
    ) -> float:
        # NOTE: ALL INPUTS ARE IN UNITS OF CLOCK CYCLES
        f = 156.25e6  # 10G core clock speed [ticks/sec]

        ROUTING_HEADER_SIZE = 14
        IPV4_HEADER_SIZE = 20
        UDP_HEADER_SIZE = 8

        # size of each header in clock cycles
        t_header = (ROUTING_HEADER_SIZE + IPV4_HEADER_SIZE + UDP_HEADER_SIZE) / 8  # [ticks]

        # size of each packet in clock cycles
        t_packet = t_data + t_header
        # .........................................................................
        # Calculating Denominator

        # average interpacket pause time in clock cycles
        ipp_bar = ipp_min + ((ipp_range - 1) / 2)  # ticks
        # average interburst pause time in clock cycles
        ibp_bar = iep_min + ((iep_range - 1) / 2)  # ticks
        # average number of packets per burst
        nbp_bar = ppe_min + ((ppe_range - 1) / 2)  # ticks
        ticks_per_packet = t_packet + (ibp_bar / nbp_bar) + ipp_bar
        return f / ticks_per_packet

    def estimated_gbps(self) -> float:
        """
        Get the estimated gigabytes per second your settings will produce

        :returns: A float represented the expected SFP speed in GB/s
        """
        return self.__speed(
            self.packets_per_event,
            self.packets_per_event_range,
            self.inter_event_pause,
            self.inter_event_pause_range,
            self.inter_packet_pause,
            self.inter_event_pause_range,
            self.words_per_packet,
        )

    def estimated_pps(self) -> float:
        """
        Get the estimated number of packets per second your settings will produces

        :returns: A float estimating the number of packets sent out per second, similar number to gbps, but also different.
        """
        return self.__speed_pps(
            self.packets_per_event,
            self.packets_per_event_range,
            self.inter_event_pause,
            self.inter_event_pause_range,
            self.inter_packet_pause,
            self.inter_event_pause_range,
            self.words_per_packet,
        )

    @property
    def board_id_real(self) -> int:
        """
        Board ID used for internal communication, boards are 1-indexed, but lists are 0-indexed, which is why this property even exists
        """
        return self.board_id - 1

    @property
    def enabled(self) -> bool:
        """
        Whether this stream is to be streaming when the board is set to a STREAMING state
        """
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool):
        self._enabled = value

    @property
    def super_id(self) -> int:
        """
        The ID of the Stream, this is the "total index" across everything
        """
        return self.sfp_id + self.board_id_real * 4

    @property
    def dst_mac(self) -> str:
        """
        The destination mac address for this stream
        """
        return self._dst_mac

    @dst_mac.setter
    def dst_mac(self, val: Union[int, str]) -> None:
        if isinstance(val, int):
            self._dst_mac = f"{val:0x}"
        else:
            self._dst_mac = val

    @property
    def src_mac(self) -> str:
        """
        The source mac address for this stream
        """
        return self._src_mac

    @src_mac.setter
    def src_mac(self, val: Union[int, str]) -> None:
        if isinstance(val, int):
            self._src_mac = f"{val:0x}"
        else:
            self._src_mac = val


class SolidagoController:
    """
    A controller to control the various functions of a given Solidago unit.
    A solidago Unit is made up of individual streams, the boards that send those streams, and the control unit.
    The boards themselves are almost irrelevant except for the modes in which they can be used.

    Important note: Almost universally ALL boards are 1-indexed, and ALL streams are 0-indexed.
    Yes, this is annoying, yes this is confusing, and yes, we are aware that that is a problem.
    """

    # ** For all these functions, send the post request and then wait for a sucess/failure status code before returning**
    def __init__(
        self,
        ip: str,
        port: Union[int, str] = 80,
        num_boards: int = 4,
        sfps_per_board: int = 4,
    ):
        self.ip = ip
        self.port = str(port)
        self.num_boards = num_boards
        self.sfps_per_board = sfps_per_board
        # add your code here
        self.streams: List[Stream] = []
        # grab current configs for all streams and build stream objects
        for board_id in range(1, num_boards + 1):
            for sfp in range(sfps_per_board):
                self.streams.append(Stream(board_id, sfp))
        try:
            self.pull_configs()
        except RuntimeError:
            pass
        except TypeError:
            pass

    def __get_url(self, url: URL_LIST):
        return f"http://{self.ip}:{self.port}/{url.value}"

    def __wait_until_state(
        self,
        board: int,
        desired_state: BoardStates,
        timeout: int = 10,
        poll_time_ms: int = 100,
    ):
        url = self.__get_url(URL_LIST.GET_STATUS_URL)
        timer = Timer()
        timer.set_countdown(timeout)
        data = {"board": board}
        while True:
            raw = requests.post(url, json=data)
            resp = raw.json()
            state: int = -1
            if not resp["status"]:
                print(f"unable to reach alinx board {board}")
            else:
                state = resp["data"]["state"]
            if state == desired_state.value:
                break
            elif timer.has_countdown_ended():
                raise TimeoutError(
                    f"timeout after {timeout}sec waiting for Alinx server. Waited for state {desired_state}, got state {BoardStates(state)} "
                )
            else:
                time.sleep(poll_time_ms / 1000)

    def autoincrement_stream_sources(
        self,
        starting_src_ip: Union[int, str],
        starting_src_mac: Union[int, str],
        starting_src_port: int,
    ):
        """
        Automatically set every stream's source ip, mac, and port, incrementing for every IP, mac, and port number

        :param starting_src_ip: The starting ip to set the Streams to send from, increments for every SFP
        :param starting_src_mac: The starting mac address to begin streaming from, increments for every SFP
        :param starting_src_port: The starting port to stream from, increments for every SFP
        """
        if isinstance(starting_src_ip, str):
            starting_src_ip = ipv4_to_num(starting_src_ip)
        if isinstance(starting_src_mac, str):
            starting_src_mac = mac_to_num(starting_src_mac)

        for stream in self.streams:
            stream.set_source(
                num_to_ipv4(starting_src_ip),
                f"{starting_src_mac:0x}",
                starting_src_port,
            )
            starting_src_ip += 1
            starting_src_mac += 1
            starting_src_port += 1

    def autoincrement_stream_destinations(
        self,
        dst_ip: Union[int, str],
        dst_mac: Union[int, str],
        starting_dst_port: int,
    ):
        """
        Automatically sets the dst and mac, and sets the destination port, but increments the port each time.

        :param dst_ip: The IP to set all streams to send to
        :param dst_mac: The MAC Address to set all streams to send to
        :param starting_dst_port: The starting port to send to, increments for every stream
        """
        if isinstance(dst_ip, str):
            dst_ip = ipv4_to_num(dst_ip)
        if isinstance(dst_mac, str):
            dst_mac = mac_to_num(dst_mac)

        for stream in self.streams:
            stream.set_destination(
                num_to_ipv4(dst_ip),
                f"{dst_mac:0x}",
                starting_dst_port,
            )
            starting_dst_port += 1

    def set_mode(self, mode: Literal["sync", "independent", "externallydriven"]):
        """
        Valid Modes: "Sync", "Independent", and "ExternallyDriven"

        Terminology:
            For the purposes of Solidago, "master" refers to a board that generates a clock sync signal,
            "slave" is a board that syncs to an external clock signal.

        If mode is SYNC:
          apply config for stream 1 to all streams (except for src/destination network config)
          set board 1 to MASTER. All other boards to slave
        If mode is Independent
          all boards set to master
        if mode is ExternallyDriven
          all boards set to slave
        """
        if mode == "sync":
            self.set_board_mode(1, "master")
            for i in range(2, self.num_boards + 1):
                self.set_board_mode(i, "slave")
        elif mode == "independent":
            for i in range(1, self.num_boards + 1):
                self.set_board_mode(i, "master")
        elif mode == "externallydriven":
            for i in range(1, self.num_boards + 1):
                self.set_board_mode(i, "slave")
        else:
            raise ValueError("Mode was not one of: 'sync', 'independent', or 'externallydriven'")

    def set_board_mode(self, board_id: int, mode: Literal["master", "slave"]):
        """
        Set a given board (1-indexed) to be either a "master" (generates a clock signal) or a "slave" (responds to an external clock signal)

        :param board_id: **1-indexed** id of a board
        :param mode: A choice between "master" and "slave" indicating whether it generates or accepts a clock-signal
        """
        decoded = {"master": 1, "slave": 0}[mode]
        url = self.__get_url(URL_LIST.SET_MASTER_URL)
        json = {"board": board_id, "data": decoded}
        resp = requests.post(url, json=json)

        json_resp = resp.json()
        if not json_resp["status"]:
            raise RuntimeError(
                f"Json response indicates failure! Board ID: {board_id} Response in Data: {json_resp['data']}"
            )

    def configure(self, boards: Union[int, Sequence[int]] = [1, 2, 3, 4]):
        """
        This function bulk configures boards passed in.

        :param boards: A **1-indexed** list of boards to configure, each board that is wanted for configuration is configured as a group, then waiting for all boards to finish configuring happens, in Solidago, there are four (4) boards.
        """
        if isinstance(boards, int):
            boards = [boards]
        # generate POST request based off of the configs for each stream
        # POST it to update the remote configuration
        url = self.__get_url(URL_LIST.SET_CONFIG_URL)
        batched = self.__batch_streams(self.streams)
        batched = [x for x in batched if (x[0].board_id in boards)]

        for streams in batched:
            json_package: Dict[str, Any] = {
                "board": streams[0].board_id,
                "data": {
                    "net_ifs": [x.get_netifs() for x in streams],
                },
            }
            resp = requests.post(url, json=json_package)
            json_resp = resp.json()
            if not json_resp["status"]:
                raise RuntimeError(
                    f"Json response indicates failure! Board ID: {streams[0].board_id} Response in Data: {json_resp['data']}"
                )
        for board in boards:
            self.__wait_until_state(
                board,
                BoardStates.CONFIGURED,
                timeout=20,
                poll_time_ms=500,
            )

    def pull_configs(self):
        """
        Get individually all board configurations and return them to the internal streams
        """
        for board in range(1, self.num_boards + 1):
            json_to_send: Dict[str, Any] = {"board": board, "data": ""}
            resp = requests.post(
                self.__get_url(URL_LIST.GET_CONFIG_URL),
                json=json_to_send,
            )
            json_resp = resp.json()
            if not json_resp["status"]:
                raise RuntimeError(
                    f"Json response indicates failure! Board ID: {board} Response in Data: {json_resp['data']}"
                )
            netifs = json_resp["data"]["net_ifs"]
            for i, value in enumerate(netifs):
                offset = (board - 1) * self.sfps_per_board + i
                stream = self.streams[offset]
                stream.apply_existing(**value)

    def __change_stream_status(self, stream: Union[Sequence[Stream], Stream], url: str):
        """
        Change the stream status of a particular stream, apply a particular url.
        """
        underlying_list: Union[List[Stream], Sequence[Stream]] = []
        if isinstance(stream, Stream):
            assert isinstance(underlying_list, list)
            underlying_list.append(stream)
        else:
            underlying_list = stream
        board_id = underlying_list[0].board_id
        json_data: Dict[str, Any] = {
            "board": board_id,
            "data": [x.sfp_id for x in underlying_list],
        }
        resp = requests.post(url, json=json_data)
        if resp.status_code >= 200 and resp.status_code <= 300:
            json_resp = resp.json()
            if not json_resp["status"]:
                raise RuntimeError(
                    f"Json response indicates failure! Board ID: {board_id} Response in Data: {json_resp['data']}"
                )
        else:
            raise RuntimeError("Server returned a non-OK status code!")

    def __batch_streams(self, streams: Sequence[Union[int, Stream]]) -> List[List[Stream]]:
        """
        Batch streams from the list into a list based on their board numbers

        :param streams: Streams to batch into groups of boards
        """
        stream_dict: Dict[int, List[Stream]] = {}
        for stream in streams:
            underlying_stream = stream
            if isinstance(stream, int):
                underlying_stream = self.streams[stream]
            assert isinstance(underlying_stream, Stream)
            if underlying_stream.board_id not in stream_dict:
                stream_dict[underlying_stream.board_id] = []
            stream_dict[underlying_stream.board_id].append(underlying_stream)
        listized = list(stream_dict.values())
        list_of_dict: List[List[Stream]] = []
        for item in listized:
            list_of_dict.append(item)
        return list_of_dict

    def enable_streams(self, streams: Sequence[Union[int, Stream]]):
        """
        enable streams to begin sending packets, for you to not get an error the listed streams must start from a CONFIGURED state

        :param streams: A **0-indexed** list of streams to begin streaming, or a Stream object to begin streaming
        """
        batched_streams = self.__batch_streams(streams)
        for stream_list in batched_streams:
            self.__change_stream_status(stream_list, self.__get_url(URL_LIST.START_STREAM_URL))
            self.__wait_until_state(stream_list[0].board_id, desired_state=BoardStates.STREAMING)
            for stream_instance in stream_list:
                stream_instance.enabled = True

    def disable_streams(self, streams: Sequence[Union[int, Stream]]):
        """
        disable streams to end streaming packets, for you to not get an error the listed streams must be in a streaming state

        :param streams: A 0-indexed list of streams to end streaming, or a Stream object to end streaming
        """
        batched_streams = self.__batch_streams(streams)
        for stream_list in batched_streams:
            self.__change_stream_status(stream_list, self.__get_url(URL_LIST.STOP_STREAM_URL))
            self.__wait_until_state(stream_list[0].board_id, desired_state=BoardStates.CONFIGURED)
            for stream_instance in stream_list:
                stream_instance.enabled = True

    def start(self, streams: Sequence[Union[int, Stream]] = []):
        """Enables all streams to begin streaming"""
        if len(streams) == 0:
            streams = self.streams
        self.enable_streams(streams)

    def stop(self, streams: Sequence[Union[int, Stream]] = []):
        """Disables all streams to end streaming"""
        if len(streams) == 0:
            streams = self.streams
        self.disable_streams(streams)

    def status(self, board: int) -> Any:
        """
        Get the raw json status of a given board, 1-indexed
        NOTE: this returns a raw json response from the 'data' section of a return

        :param board: The board to get the status of, **1-indexed**
        """
        url = self.__get_url(URL_LIST.GET_STATUS_URL)

        data = {"board": board}
        json_req = requests.post(url, data).json()

        if not json_req["status"]:
            raise RuntimeError(f"Unable to reach Alinx board {board}")
        return json_req["data"]

    def estimated_gbps(self) -> float:
        """
        returns: the estimated gbps of all enabled streams
        """
        return sum([x.estimated_gbps() for x in self.streams if x.enabled])

    def estimated_pps(self) -> float:
        """
        Calculates the estimated packets per second of all enabled streams
        """
        return sum([x.estimated_pps() for x in self.streams if x.enabled])

    def __getitem__(self, stream_number: int):
        return self.streams[stream_number]

    def __iter__(self) -> Generator[Stream, Any, None]:
        # iterate through all stream objects
        for s in self.streams:
            yield s
