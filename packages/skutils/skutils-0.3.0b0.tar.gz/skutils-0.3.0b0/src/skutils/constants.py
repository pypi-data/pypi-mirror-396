from collections import namedtuple
from struct import Struct
import bitstruct

__min_femtodaq_version__ = "6.0.0"

FEMTODAQ_USB = "192.168.7.2"


GEB_HEADER_SIZE = 16  # Bytes
SKUTEK_WORD_SIZE = 4  # Bytes
FULL_PULSE_SUMMARY0_HEADER_SIZE = GEB_HEADER_SIZE + (1 * SKUTEK_WORD_SIZE)  # Bytes
FULL_PACKET0_HEADER_SIZE = GEB_HEADER_SIZE + (2 * SKUTEK_WORD_SIZE)  # Bytes
FULL_PACKET1_HEADER_SIZE = GEB_HEADER_SIZE + (3 * SKUTEK_WORD_SIZE)  # Bytes
SAMPLE_SIZE = 2  # Bytes
SKUTEK_WORDS_LENGTH = 2 * SKUTEK_WORD_SIZE

ASCII_VERSION_PREFIX = 0
ENDIAN_INDICATOR_TIMESTAMP = 0x0102030405060708
GEB_HEADER_BE = Struct(">llq")  # big endian
GEB_HEADER_LE = Struct("<llq")
GEB_HEADER_NATIVE = Struct("=llq")


# skutek words are always big endian, but with each element having the LSB last...???

SKUTEK_WORD1 = bitstruct.compile("u8u8u1u15>")
SKUTEK_WORD2 = bitstruct.compile("u4u28>")
SKUTEK_WORD3 = bitstruct.compile("u16u16>")
FULL_PACKET_HEADER = bitstruct.compile("s32s32s64u8u8u1u15u4u28")

__ps_raw_format = "hhB?h4l"
PULSE_SUMMARY0_BE = Struct(">" + __ps_raw_format)  # big endian
PULSE_SUMMARY0_LE = Struct("<" + __ps_raw_format)
PULSE_SUMMARY0_NATIVE = Struct("=" + __ps_raw_format)
PulseSummary0 = namedtuple(
    "PulseSummary0",
    [
        "pulse_height",  # 2 Bytes
        "trig_height",  # 2 Bytes
        "trig_count",  # 1 Bytes
        "triggered",  # 1 Bytes
        "relative_channel_timestamp",  # 2 Bytes
        "qdc_base_sum",  # 4 Bytes
        "qdc_fast_sum",  # 4 Bytes
        "qdc_slow_sum",  # 4 Bytes
        "qdc_tail_sum",  # 4 Bytes
    ],
)


# SKUTEK_WORD1_BE = bitstruct.compile('u8u8u1u15')
# SKUTEK_WORD1_NATIVE = SKUTEK_WORD1_LE if (sys.byteorder == 'little') else SKUTEK_WORD1_BE

# SKUTEK_WORD2_LE = bitstruct.compile('>u4>u28>')
# SKUTEK_WORD2_BE = bitstruct.compile('u4u28<')
# SKUTEK_WORD2_NATIVE = SKUTEK_WORD2_LE if (sys.byteorder == 'little') else SKUTEK_WORD2_BE

# FULL_PACKET_HEADER_LE = bitstruct.compile('u32u32u64u8u8u1u15u4u28>')
# FULL_PACKET_HEADER_NATIVE  = FULL_PACKET_HEADER_LE if (sys.byteorder == 'little') else FULL_PACKET_HEADER_BE


GebPacketHeader = namedtuple("GebPacketHeader", ["type", "length", "timestamp"])
SkutekWord1 = namedtuple("SkutekWord1", ["version", "module", "signed", "channel"])
SkutekWord2 = namedtuple("SkutekWord2", ["bitdepth", "number_samples"])
SkutekWord3 = namedtuple("SkutekWord3", ["sample_offset", "relative_channel_timestamp"])

# all packet sized are divisible by this number
BYTE_ALIGNMENT_SIZE = 4


################################################################################
class GebTypes:
    skutek_type_prefix = 0x50000000
    endian_indicator = skutek_type_prefix + 0x00102050
    endian_indicator_nonnative = skutek_type_prefix + 0x00201050
    # endian_indicator_be = skutek_type_prefix + 0x00201050
    general_ascii = skutek_type_prefix + 0xA0
    version_info_ascii = general_ascii + 0x1
    raw_histogram = skutek_type_prefix + 0x00
    raw_waveform = skutek_type_prefix + 0x10
    raw_pulse_summary = skutek_type_prefix + 0x20

    WAVE_TYPE_STRINGS = {raw_waveform: "waveform", raw_histogram: "histogram", raw_pulse_summary: "pulse_summary"}

    # @classmethod
    # def endian_indicator_native(cls):
    #     # return self.e
    # if sys.byteorder == 'big':
    #     return cls.endian_indicator_be
    # else:
    #     return cls.endian_indicator_le

    @classmethod
    def get_wavetype_from_string(cls, wave_str):
        return {v: k for k, v in cls.WAVE_TYPE_STRINGS.items()}.get(wave_str, "unknown")
