import struct
import time
import socket
from typing import Any, List, Optional
import platform

is_windows = False
if platform.system() != "Windows":
    import fcntl
else:
    is_windows = True


class Timer:
    def __init__(self) -> None:
        self.reset()

    # __________________________________________________________________________
    def time(self, round_to: int = 3):
        return round(time.time() - self.start, round_to)

    # __________________________________________________________________________
    def set_countdown(self, cntdwn: float):
        self.cntdwn_start = time.monotonic()
        self.cntdwn = cntdwn
        return self

    # __________________________________________________________________________
    def countdown_remaining(self):
        assert self.cntdwn_start is not None
        assert self.cntdwn is not None
        t_remaining = self.cntdwn - (time.monotonic() - self.cntdwn_start)
        return max(t_remaining, 0)

    # __________________________________________________________________________
    def has_countdown_ended(self):
        if self.countdown_remaining():
            return False
        return True

    # __________________________________________________________________________
    def reset(self):
        self.start = time.monotonic()
        self.start_datetime = time.strftime("%b%d %I-%M-%S%p", time.localtime(time.time()))
        self.cntdwn: Optional[float] = None
        self.cntdwn_start: Optional[float] = None
        self.last_lap = None


###############################################################################
# From: https://stackoverflow.com/questions/24196932/how-can-i-get-the-ip-address-from-a-nic-network-interface-controller-in-python
def get_ip_address_of_interface(ifname: str) -> str:
    """
    Get the an ip address of the named interface, does not work on Windows.
    """
    if is_windows:
        raise RuntimeError("Cannot get IP address of an interface via this function on windows")
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(
            fcntl.ioctl(
                s.fileno(),
                0x8915,  # SIOCGIFADDR
                struct.pack("256s", bytes(ifname[:15], "utf-8")),
            )[20:24]
        )
    except OSError:
        print(f"Interface {ifname} not assigned an IP address")
        print(f"May need to be set manually. e.g. 'ifconfig {ifname} X.X.X.X netmask Y.Y.Y.Y'")
        raise


###############################################################################
def get_mac_address_of_interface(ifname: str) -> str:
    """
    Get the MAC address of a named interface, does not work on windows.
    """
    if is_windows:
        raise RuntimeError("Cannot get mac address of an interface via this function on windows")
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    info = fcntl.ioctl(s.fileno(), 0x8927, struct.pack("256s", bytes(ifname, "utf-8")[:15]))
    return "".join("%02x" % b for b in info[18:24])


###############################################################################
def num_to_ipv4(ipaddr_num: int) -> str:
    """
    Convert a 32-bit number to an ipv4 string
    """
    places: List[str] = []
    for x in reversed(range(4)):
        place = ipaddr_num // 256**x
        ipaddr_num = ipaddr_num - (place * (256**x))
        places.append(str(place))
    res = ".".join(places)
    return res


###############################################################################
def ipv4_to_num(ipaddr: str) -> int:
    """
    Convert an ipv4 string to a 32-bit number
    """
    places = [int(x) for x in ipaddr.split(".")]
    ipaddr_num = (places[0] * 256**3) + (places[1] * 256**2) + (places[2] * 256**1) + (places[3] * 256**0)
    return ipaddr_num


###############################################################################
def incremenet_ipv4_address_by(ipaddr: str, increment: int) -> str:
    """
    Add X to an ipv4 number, so you get the Xth "greater" IPV4 number as-if it were a 32-bit integer
    """
    ipaddr_num = ipv4_to_num(ipaddr) + increment
    return num_to_ipv4(ipaddr_num)


###############################################################################
def int_to_hex(number: int, length: int) -> str:
    """
    Get a hex string for an integer with certain length
    """
    hex_num = "{0:0{1}x}".format(number, length).upper()
    return hex_num


def clamp(minimum: Any, x: Any, maximum: Any):
    """
    Clamp a value between two values
    """
    return max(minimum, min(x, maximum))


def calculate_pps(
    ipp_min: int,
    ipp_range: int,
    ibp_min: int,
    ibp_range: int,
    nbp_min: int,
    nbp_range: int,
    t_data: int,
):
    ROUTING_HEADER_SIZE = 14
    IPV4_HEADER_SIZE = 20
    UDP_HEADER_SIZE = 8
    t_header = ROUTING_HEADER_SIZE + IPV4_HEADER_SIZE + UDP_HEADER_SIZE
    ipp_bar = ipp_min + ((ipp_range - 1) / 2)
    ibp_bar = ibp_min + ((ibp_range - 1) / 2)
    nbp_bar = nbp_min + ((nbp_range - 1) / 2)
    t_packet = t_data + t_header
    time_between_packets = t_packet + (ibp_bar / nbp_bar) + ipp_bar
    total_time_sec = 1 / time_between_packets
    return total_time_sec


def mac_to_num(mac: str) -> int:
    """
    Translate a MAC address string to a number
    """
    # https://stackoverflow.com/a/36883363
    return int(mac.translate({":": None, ".": None, "-": None, " ": None}), 16)  # type: ignore


def num_to_mac(mac: int) -> str:
    """Translate a number to a MAC address string"""
    # https://stackoverflow.com/a/36883363
    mac_hex = "{:012x}".format(mac)
    return ":".join(mac_hex[i : i + 2] for i in range(0, len(mac_hex), 2))
