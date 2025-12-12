import socket
from .GretinaFileWriter import GretinaFileWriter


################################################################################
class UdpFileMimic:
    def __init__(self, target_ip, target_port):
        self.target_ip = target_ip
        self.target_port = target_port

        # udp socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # --------------------------------------------------------------------------
    def write(self, data):
        """write data to UDP socket"""
        self.sock.sendto(data, (self.target_ip, self.target_port))

    # --------------------------------------------------------------------------
    def close(self):
        """close UDP socket"""
        self.sock.close()


################################################################################
class GretinaUdpWriter(GretinaFileWriter):
    """Writes Skutek formatted Gretina data to a UDP socket - the same format
    as the ".bin" files saved natively by our digitizer.
    """

    # --------------------------------------------------------------------------
    def __init__(self, target_ip, target_port, ascii_version_header=[]):
        self.target_ip = target_ip
        self.target_port = target_port

        super().__init__(None, ascii_version_header)

    # --------------------------------------------------------------------------
    def _create_file(self):
        """creates udp file mimic"""
        fp = UdpFileMimic(self.target_ip, self.target_port)
        return fp
