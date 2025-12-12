import mmap
from .GretinaFileWriter import GretinaFileWriter


################################################################################
class MemmapBuffer:
    def __init__(self, fp, preallocate):
        self.fp = fp
        self.preallocate = int(preallocate)
        self.loc = 0
        self.buf = bytearray(self.preallocate)

    def write(self, data):
        length = len(data)
        end = self.loc + length
        if end <= self.preallocate:
            self.buf[self.loc : end] = data
        else:
            self.save()
            # print("extending buffer")
            # breakpoint()
            self.write(data)
        self.loc += length

    def save(self):
        self.fp.write(self.buf[: self.loc])
        self.__init__(self.fp, self.preallocate)

    def close(self):
        del self.buf
        self.fp.close()


################################################################################
class GretinaMmapWriter(GretinaFileWriter):
    """Writes Skutek formatted Gretina data to a UDP socket - the same format
    as the ".bin" files saved natively by our digitizer.
    """

    def __init__(self, *args, preallocate=2**30, **kwargs):
        self.preallocate = preallocate
        super().__init__(*args, **kwargs)

    # --------------------------------------------------------------------------
    def _create_file(self):
        """creates udp file mimic"""
        fp = super()._create_file()
        fp = MemmapBuffer(fp, self.preallocate)
        return fp

    def save(self):
        self.fp.save()
