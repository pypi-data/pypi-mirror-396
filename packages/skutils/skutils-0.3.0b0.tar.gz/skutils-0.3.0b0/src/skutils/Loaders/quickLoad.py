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

import pathlib
from .BaseLoader import EventInfo,ChannelData

from .EventCSVLoader import EventCSVLoader
from .IGORPulseHeightLoader import IGORPulseHeightLoader
from .IGORWaveLoader import IGORWaveLoader
from .GretaLoader import GretaLoader
from .GretinaLoader import GretinaLoader

###############################################################################
def quickLoad(file_list: Union[Sequence[str],str]) -> Generator[EventInfo, Any, None]:
    """generator which loads events from the list of files provided.
    This function determines which `Loader` object to use for each file
    depending on the file extension and content. If you need to rebuild events or
    utilize other loader features, you will need to use `Loader` Objects directly.

    :param file_list: a list of files to load events from. Files will be
        loaded in the order they are passed in. 

    :yields: EventInfo object for each event in all files.
    """
    allowed_file_extensions = ('.ecsv', # Event CSV
                                '.itx', # IGOR
                                '.geb','.gretina', # Gretina
                                '.greta' # GRETA
                                )

    if isinstance(file_list,str):
        file_list = [file_list]

    for fname in file_list:
        extension = pathlib.Path(fname).suffix.lower()

        if extension not in allowed_file_extensions:
            raise ValueError(f"Can't load file with extension '{extension}'")

        # .....................................................................
        # Event CSV
        if extension == ".ecsv":
            loader = EventCSVLoader(fname)
        # .....................................................................
        # IGOR
        elif extension == ".itx":
            # grab the first lines of the file to determine if this is an
            # Igor Pulse Height of IGOR wave format
            with open(fname, "r") as f:
                f.readline()  # discard first line
                raw_format_line = f.readline().strip().replace("X // ", "")
                format_type = raw_format_line.split("=")[1].strip().replace('"', "").upper()

            if format_type == "IGOR PULSE HEIGHTS":
                loader = IGORPulseHeightLoader(fname)
            elif format_type == "IGOR WAVES":
                loader = IGORWaveLoader(fname)
            else:
                print(f"Can't determine IGOR file type for {fname}. Attending to decode it as a Waveform file")
                loader = IGORWaveLoader(fname)
        # .....................................................................
        # GRETINA
        elif extension in (".geb", ".gretina"):
            loader = GretinaLoader(fname)
        # .....................................................................
        # GRETA
        elif extension == ".greta":
            loader = GretaLoader(fname)

        else: 
            raise ValueError(f"Can't load file with extension '{extension}'")


        for event in loader:
            yield event