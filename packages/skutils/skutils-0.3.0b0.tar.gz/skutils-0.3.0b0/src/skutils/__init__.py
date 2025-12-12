
from .constants import FEMTODAQ_USB, __min_femtodaq_version__
from .FemtoDAQController import FemtoDAQController, BusyError, CollectionNotRunningError
from .ChickadeeController import (
    ChickadeeController,
    ChickadeeDspRemote,
    FpgaSignalMimic,
    dsp_dict_to_dsp_namespace,
    dsp_namespace_to_dsp_dict,
)

from .Loaders import ChannelData, EventInfo
from .Loaders import (
    LegacyGretinaLoader,
    BaseLoader,
    EventCSVLoader,
    IGORPulseHeightLoader,
    IGORWaveLoader,
    GretinaLoader,
    GretaLoader,
    quickLoad,
    )
    

from .SolidagoController import Stream, SolidagoController
from .CollectorNodeController import CollectorNodeController
from .quickPlotEvent import quickPlotEvent
import importlib.metadata

__version__ = importlib.metadata.version(__package__) # type: ignore

print("Skutils is in beta, please contact support@skutek.com with bugs, issues, and questions")
__all__ = [
    "LegacyGretinaLoader",
    "FemtoDAQController",
    "ChickadeeController",
    "ChickadeeDspRemote",
    "FpgaSignalMimic",
    "dsp_dict_to_dsp_namespace",
    "dsp_namespace_to_dsp_dict",
    "ChannelData",
    "EventInfo",
    "EventCSVLoader",
    "GretinaLoader",
    "IGORPulseHeightLoader",
    "IGORWaveLoader",
    "BaseLoader",
    "GretaLoader",
    "quickLoad",
    "BusyError",
    "CollectionNotRunningError",
    "Stream",
    "SolidagoController",
    "CollectorNodeController",
    "quickPlotEvent",
    "FEMTODAQ_USB",
    "__version__",
    "__min_femtodaq_version__",
]
