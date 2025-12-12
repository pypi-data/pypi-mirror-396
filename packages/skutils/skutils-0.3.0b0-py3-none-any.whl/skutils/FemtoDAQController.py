import requests
import urllib.request
import os
import sys
from typing import Literal, Union, Optional, Sequence, Any, Dict, List, Tuple
import time
import socketio
import enum
import json
import urllib.parse
import socketio.exceptions
from .Loaders.BaseLoader import ChannelData, EventInfo, OurNumpyArrType
import numpy as np

from .constants import __min_femtodaq_version__


class BusyError(Exception):
    """
    An error representing that the FemtoDAQ device is busy.
    """

    pass


class CollectionNotRunningError(Exception):
    "An error representing that the FemtoDAQ device has not started data collection"

    pass


class FemtoDAQController:
    """
    A controller for FemtoDAQ devices, such as the FemtoDAQ Kingfisher or FemtoDAQ Vireo device.
    For full functionality, use the FemtoDAQController with a v6 DDC_APPs version for your FemtoDAQ device.
    """

    class __GUI_ENUMS(enum.Enum):
        DISCONNECTED = 0
        NOT_SETUP = 1
        READY_TO_RUN = 2
        RUNNING_WAVE = 3
        RUNNING_HIST = 4
        RECORDING_WAVE = 5

    def __init__(self, url: str, verbose: bool = False, skip_version_check: bool = False):
        """Initialize the FemtoDAQController to use a specified URL as its target FemtoDAQ device

        :param url: The local URL of the FemtoDAQ device.
        :param verbose: enable/disable verbose mode.
        :param skip_version_check: Skip compatability checking target device
        """
        assert isinstance(url, str), "url must be a string"
        if url.startswith("https://"):
            raise ValueError("Secure http not supported! (digitizer url must begin with 'http' not 'https')")
        # add http:// manually if not provided
        elif not url.startswith("http://"):
            url = f"http://{url}"

        if url[-1] == "/":
            url = url[:-1]
        self.url = url
        self.verbose = verbose
        self.fpga_data = self.__get_fpga_data()

        if not skip_version_check:
            # Verify that the target device has the minimum supported software version
            fdaq_version = tuple(int(x) for x in self.getSoftwareVersion().split(".")[0:2])
            supported_version = tuple(int(x) for x in __min_femtodaq_version__.split(".")[0:2])

            if fdaq_version < supported_version:
                raise RuntimeError(
                    "FemtoDAQController requires that your FemtoDAQ device to have software"
                    f" version {__min_femtodaq_version__} or above. It currently has {self.getSoftwareVersion()}.\n"
                    "use `skip_version_check=True` to ignore this or consult your manual for instruction or contact support@skutek.com."
                )

        if self.verbose:
            print(f"Connnected to {self}")
            print(self.summary())

    # _________________________________________________________________________
    def __get_fpga_data(self):
        route = self.url + "/rest/fpga_data"
        resp = requests.get(route, json={})
        if not resp.ok:
            print(f"unable to connect with FemtoDAQ device at {self.url}!")
            sys.exit()
        return resp.json()["data"]

    # _________________________________________________________________________
    def __config_url(self, channel: Union[str, int], setting: str):
        # ensure the channel is an acceptable range
        if channel == "global":
            pass
        elif channel not in self.channels:
            raise ValueError(
                f"Invalid Channel. Must be 'global' or integer between 0-{self.fpga_data['num_channels'] - 1}"
            )

        route = self.url + f"/rest/config/{channel}/{setting}"
        return route

    # _________________________________________________________________________
    def __runtime_url(self, command: str):
        route = self.url + f"/rest/runtime/{command}"
        return route

    # _________________________________________________________________________
    def __gui_url(self, command: str):
        route = self.url + f"/web_API/{command}"
        return route

    # _________________________________________________________________________
    def __download_url(self, filename: str):
        route = self.url + f"/DOWNLOAD_FILES_FROM_DIGITIZER/{filename}"
        return route

    # _________________________________________________________________________
    def __data_url(self, command: str):
        return f"{self.url}/rest/data/{command}"

    # _________________________________________________________________________
    def __get(self, route: str, data: Dict[str, Any] = {}) -> Dict[str, Any]:
        if self.verbose:
            print(f"sending GET to {route} with payload {data}")
        resp = requests.get(route, json=data, timeout=5)
        if not resp.ok:
            print(f"Request to {route} failed due to {resp.status_code}:{resp.reason}")

        resp_json = resp.json()
        status = resp_json.get("status", "").upper()

        if status == "SUCCESS":
            pass
        elif status == "ERROR":
            raise RuntimeError(f"FemtoDAQ device connection returned an error with message {resp_json['message']}")
        elif status == "NOT SUPPORTED":
            print(f"{str(self)} : {route.split('/')[-1]} not supported on this unit and has been ignored.")
        elif status == "WARNING":
            print(f"{str(self)} : FemtoDAQ device connection has sent back a warning! {resp_json['message']}")
        elif status == "CRITICAL":
            raise RuntimeError(
                f"{str(self)} : FemtoDAQ device connection has returned a CRITICAL ERROR: {resp_json['message']}"
            )
        elif status == "FAILURE":
            print(
                f"{str(self)} : FemtoDAQ device connection indicated FAILURE, this is an old error code for non-updated REST endpoints, so is treated as a warning"
                + f", this may be insufficient: {resp_json['message']}"
            )
        elif status == "BUSY":
            raise BusyError(f"FemtoDAQ device responded busy! {resp_json['message']}")
        return resp_json

    # _________________________________________________________________________
    def __post(self, route: str, data: Dict[str, Any] = {}, print_failure: bool = True):
        if self.verbose:
            print(f"sending POST to {route} with payload {data}")
        resp = requests.post(route, json=data, timeout=5)
        if not resp.ok:
            print(f"Request to {route} failed due to {resp.status_code}:{resp.reason}")
            raise requests.ConnectionError(f"Request to {route} failed due to {resp.status_code}:{resp.reason}")

        resp_json = resp.json()
        status = resp_json.get("status", "").upper()

        if status == "SUCCESS":
            pass
        elif status == "ERROR":
            raise RuntimeError(f"FemtoDAQ device connection returned an error with message {resp_json['message']}")
        elif status == "NOT SUPPORTED":
            print(f"{str(self)} : {route.split('/')[-1]} not supported on this unit and has been ignored.")
        elif status == "WARNING":
            print(f"{str(self)} : FemtoDAQ device connection has sent back a warning! {resp_json['message']}")
        elif status == "CRITICAL":
            raise RuntimeError(
                f"{str(self)} : FemtoDAQ device connection has returned a CRITICAL ERROR: {resp_json['message']}"
            )
        elif status == "FAILURE":
            print(
                f"{str(self)} : FemtoDAQ device connection indicated FAILURE, this is an old error code for non-updated REST endpoints, so is treated as a warning"
                + f", this may be insufficient: {resp_json['message']}"
            )
        elif status == "BUSY":
            raise BusyError(f"FemtoDAQ device responded busy! {resp_json['message']}")
        return resp_json

    # _________________________________________________________________________
    def __max_wait_until_socketio_state(self, state_list: List[__GUI_ENUMS], max_timeout: float = 1):
        with socketio.SimpleClient() as sio:
            sio.connect(self.url)
            try:
                event_list = sio.receive(max_timeout)
                event_name = event_list[0]
                if event_name == "state":
                    json_packet = json.loads(event_list[1])
                    if self.__GUI_ENUMS(json_packet["gui_state"]) in state_list:
                        return
            except socketio.exceptions.TimeoutError:
                pass

    # #########################################################################
    #                       Global Settings
    # #########################################################################

    # _________________________________________________________________________
    # TriggerXPosition
    def getTriggerXPosition(self):
        """
        Get the position of where the event trigger fired in the waveform buffer

        """
        route = self.__config_url("global", "TriggerXPosition")
        resp = self.__get(route)
        return resp["data"]

    def setTriggerXPosition(self, x_position: int, force: bool = False):
        """
        Set the position of where the event trigger in the waveform buffer

        :param x_position: The position of the trigger in the N-sample window.
        :param force: apply change even if data collection is ongoing.
        """
        route = self.__config_url("global", "TriggerXPosition")
        data: Dict[str, Any] = {"trigger_x_position": x_position, "force": force}
        self.__post(route, data)

    # _________________________________________________________________________
    # TriggerActiveWindow AKA Coincidence Window
    def getTriggerActiveWindow(self):
        """
        Gets the trigger active window in samples/clock cycles. AKA coincidence Window - the window in which
        triggers across multiple channels will be considered part of the same event.
        """
        route = self.__config_url("global", "TriggerActiveWindow")
        resp = self.__get(route)
        return resp["data"]

    def setTriggerActiveWindow(self, window_width: int, force: bool = False):
        """
        sets the trigger active window. AKA coincidence Window - the window in which
        triggers across multiple channels will be considered part of the same event. The window
        starts at the first trigger in an event and stays active for the number of samples specified

        :param window_width: number of samples to keep the trigger active.
        :param force: apply change even if data collection is ongoing.
        """
        route = self.__config_url("global", "TriggerActiveWindow")
        data: Dict[str, Any] = {
            "trigger_active_window_width": window_width,
            "force": force,
        }
        self.__post(route, data)

    def getCoincidenceWindow(self):
        """alias for :meth:`.getTriggerActiveWindow`"""
        return self.getTriggerActiveWindow()

    def setCoincidenceWindow(self, *args: Any, **kwargs: Any):
        """alias for :meth:`.setTriggerActiveWindow`"""
        return self.setTriggerActiveWindow(*args, **kwargs)

    # _________________________________________________________________________
    # PulseHeightWindow
    def getPulseHeightWindow(self) -> int:
        """
        Gets the pulse height window / filter window in samples (ie clock cycles)

        """
        route = self.__config_url("global", "PulseHeightWindow")
        resp = self.__get(route)
        return resp["data"]

    def setPulseHeightWindow(self, window_width: int, force: bool = False):
        """
        Set the number of samples after a trigger in which the firmware will calculate
        the DSP quantities: pulse height, trigger height, qdc_triangular, and qdc_rectangular


        .. Note:: Historical Naming

            The "Pulse Height Window" also defines size of the window for DSP
            quantities such as pulse height, trigger height, qdc_triangular, and
            qdc_rectangular are calculated. This includes all histogram quantities.

        .. Note:: Window for all Channels Starts at first trigger in event

            This window starts at the first trigger in the event regardless of where an
            individual channel triggers. SkuTek recommends setting the Pulse Height Window
            to the same value as the Trigger/Coincidence Window for most applications.

        :param window_width: Width of DSP calculation window following event trigger
        :param force: apply change even if data collection is ongoing.
        """
        route = self.__config_url("global", "PulseHeightWindow")
        data: Dict[str, Any] = {
            "pulse_height_window": window_width,
            "force": force,
        }
        self.__post(route, data)

    # _________________________________________________________________________
    # EnableBaselineRestoration
    def getEnableBaselineRestoration(self) -> bool:
        """
        Gets current active status of the automatic Baseline Restoration.
        Baseline Restoration is not supported on all products.
        Check with :attr:`.has_baseline_restoration`
        """
        route = self.__config_url("global", "EnableBaselineRestoration")
        resp = self.__get(route)
        return resp["data"]

    def setEnableBaselineRestoration(self, enable: bool, force: bool = False):
        """
        Enable (or disable) Baseline Restoration.
        Baseline Restoration is not supported on all products.
        Check with :attr:`.has_baseline_restoration`

        :param enable: True to enable baseline restoration. False to disable
        :param force: apply change even if data collection is ongoing.
        """
        route = self.__config_url("global", "EnableBaselineRestoration")
        data = {"baseline_restore_enable": enable, "force": force}
        self.__post(route, data)

    # _________________________________________________________________________
    # BaselineRestorationExclusion
    def getBaselineRestorationExclusion(self):
        """
        Get the area used in baseline restoration exclusion to excluse your triggered pulse.
        """
        route = self.__config_url("global", "BaselineRestorationExclusion")
        resp = self.__get(route)
        return resp["data"]

    def setBaselineRestorationExclusion(self, window_width: int, force: bool = False):
        """
        Sets the number of samples after an event trigger to exclude from the baseline
        calculation algorithm. This prevents pulsse data from corrupting the baseline
        calculation


        .. note::

            SkuTek recommends that the Baseline Restoration Window be greater than your
            (trigger_window + decay_period) of your signal pulse.

        .. warning::

            Baseline Restoration calculates the baseline on the fly so the calculated baseline can
            vary between events. If this poses a problem for your experiment, we recommend manually
            setting the baseline using a :meth:`.setDigitialOffset`.

        :param window_width: Number of samples to exclude after an event trigger.
        :param force: apply change even if data collection is ongoing.

        """
        route = self.__config_url("global", "BaselineRestorationExclusion")
        data: Dict[str, Any] = {
            "baseline_restore_exclusion": window_width,
            "force": force,
        }
        self.__post(route, data)

    # _________________________________________________________________________
    # PulseHeightAveragingWindow
    def getPulseHeightAveragingWindow(self) -> int:
        """
        Gets the size of the pulse height / DSP filter averaging window.

        """
        route = self.__config_url("global", "PulseHeightAveragingWindow")
        resp = self.__get(route)
        return resp["data"]

    def setPulseHeightAveragingWindow(self, window_width: int, force: bool = False):
        """
        Sets the width of the Pulse Height / DSP quantitiy smoothing filter.
        Must be a power of 2. See :attr:`.filter_window_width_values` for a list of valid
        sizes.

        .. Note:: Historical Naming

            The "Pulse Height Averaging Window" also defines size of the averaging window
            for DSP quantities such as pulse height, qdc_triangular, and
            qdc_rectangular. This includes all histogram quantities.
            However the *trigger_height* quantity averaging is set with :attr:`.setTriggerAveragingWindow`


        :param window_width: Number of filter quantity samples to average
        :param force: apply change even if data collection is ongoing.
        """
        route = self.__config_url("global", "PulseHeightAveragingWindow")
        data: Dict[str, Any] = {
            "pulse_height_averaging_window": window_width,
            "force": force,
        }
        self.__post(route, data)

    # _________________________________________________________________________
    # QuadQDCWindows
    def getQuadQDCWindows(self) -> Tuple[int, int, int, int]:
        """
        Get the quad QDC integration windows.
        Returns a tuple where the tuple values are:
        (base_width, fast_width, slow_width, tail_width)

        Returns Zeros
        """
        route = self.__config_url("global", "QuadQDCWindows")
        resp = self.__get(route)
        return (
            resp["data"]["base_width"],
            resp["data"]["fast_width"],
            resp["data"]["slow_width"],
            resp["data"]["tail_width"],
        )

    def setQuadQDCWindows(
        self,
        qdc_base_integration_window: int,
        qdc_fast_integration_window: int,
        qdc_slow_integration_window: int,
        qdc_tail_integration_window: int,
        force: bool = False,
    ):
        """
        Set the windows for FGPA-based 4-part integration of an event.

        QuadQDC Integration is composed of 4 integration windows on different sections of your pulse.
        There are windows for integrating BASELINE (pre-trigger),FAST (peak), SLOW (mid decay),
        TAIL (late decay). There is also a constant 8 sample gap between the FAST from the baseline
        in order to avoid contaminating the baseline with the pulse.

        The values of the sums are latched when the FAST sum is at maximum.

        Refer to the manual for figures describing this process

        .. warning:: Set Pulse Height Accordingly

            The Pulse Height Window should liberally encompass the duration of the FAST+SLOW+TAIL in order allow the maximum to be latched.
            Set Pulse Height Window with :meth:`.setPulseHeightWindow`

        .. note:: Note available on all models

            Check :attr:`has_quadqdc_integration` to see if this feature is supported on your unit

        :param qdc_base_integration_window: Width of Baseline calculation window in samples prior to the pulse. Followed by an 8 sample gap
        :param qdc_fast_integration_window: Width of the FAST window in samples. Starts 8 samples following the end of the BASELINE window.
        :param qdc_slow_integration_window: Width of the SLOW window in samples. Starts immediately after end of the FAST window.
        :param qdc_tail_integration_window: Width of the TAIL window in samples. Starts immediately after end of the SLOW window.
        :param force: apply change even if data collection is ongoing.


        """
        route = self.__config_url("global", "QuadQDCWindows")
        data: Dict[str, Any] = {
            "qdc_base_integration_window": qdc_base_integration_window,
            "qdc_fast_integration_window": qdc_fast_integration_window,
            "qdc_slow_integration_window": qdc_slow_integration_window,
            "qdc_tail_integration_window": qdc_tail_integration_window,
            "force": force,
        }
        self.__post(route, data)

    # _________________________________________________________________________
    # BiasVoltage
    def getBiasVoltage(self) -> float:
        """
        Read back the bias voltage used to drive the High Voltage (HV) output. If available
        """
        route = self.__config_url("global", "BiasVoltage")
        resp = self.__get(route)
        return resp["data"]

    def setBiasVoltage(self, voltage: float, force: bool = False):
        """
        Sets the bias voltage used to drive the High Voltage (HV) output.

        Some models may require you to switch between High and Low voltage ranges
        using a physical switch on the back of the unit. Refer you unit's manual
        for more information

        See :attr:`.bias_voltage_min` and :attr:`.bias_voltage_max`
        for your digitizer's available voltage range.

        :param voltage: Voltage to drive the HV output
        :param force: apply change even if data collection is ongoing.
        """
        route = self.__config_url("global", "BiasVoltage")
        data: Dict[str, Any] = {"bias_voltage_setting": voltage, "force": force}
        self.__post(route, data)

    # _________________________________________________________________________
    # BiasVoltageRaw
    def getBiasVoltageRaw(self) -> int:
        """
        Get the raw DAC value used to bias a detector
        """
        route = self.__config_url("global", "BiasVoltageRaw")
        resp = self.__get(route)
        return int(resp["data"])

    def setBiasVoltageRaw(self, voltage: int, force: bool = False):
        """
        Set the raw DAC value used to bias output for a detector. Steps of 1. Use for
        higher precision configuration of HV bias voltage.

        See :attr:`.bias_voltage_raw_min` and :attr:`.bias_voltage_raw_max`
        for your digitizer's available DAC range.

        :param voltage: DAC value to configure the HV voltage driver.
        :param force: apply change even if data collection is ongoing.
        """
        route = self.__config_url("global", "BiasVoltageRaw")
        data: Dict[str, Any] = {"dac_value": voltage, "force": force}
        self.__post(route, data)

    # _________________________________________________________________________
    # GlobalID (aka module_number)
    # _________________________________________________________________________
    def getGlobalId(self) -> int:
        """
        Gets the assigned global ID of this device for this experimental run.
        This is also known as "Module Number" in some documentation.
        """
        route = self.__config_url("global", "GlobalID")
        resp = self.__get(route)
        return int(resp["data"])

    def setGlobalId(self, global_id: int, force: bool = False):
        """
        Sets assigned global ID of this device for this experimental run.
        This is also known as "Module Number" in some documentation.

        :param global_id: Identifier for this unit in an experimental run
        :param force: apply change even if data collection is ongoing.
        """
        assert isinstance(global_id, int), "global id must be an integer between 0-255"
        route = self.__config_url("global", "GlobalID")
        data: Dict[str, Any] = {"global_id": global_id, "force": force}
        self.__post(route, data)

    # #########################################################################
    #                       Per-Channel Settings
    # #########################################################################

    # _________________________________________________________________________
    def setAnalogOffsetPercent(self, channel: int, offset_percent: int, force: bool = False):
        """
        Set the analog offset. 100% is maximum analog offset. -100% is minimum analog offset

        .. Note:: This value is unable to be read back.

        :param channel: Target Channel
        :param offset_percent: The percent offset for analog baseline offset ranging from -100% to 100% as an integer
        :param force: apply change even if data collection is ongoing.

        :raise ValueError: If the offset percentage is not in the valid range
        """
        offset_percent = int(offset_percent)
        if (offset_percent < -100) or (offset_percent > 100):
            raise ValueError("Offset percent not in valid range!")
        route = self.__config_url(channel, "AnalogOffsetPercent")
        data: Dict[str, Any] = {
            f"channel_{channel}_analog_offset": offset_percent,
            "force": force,
        }
        self.__post(route, data)

    def setAnalogOffsetRaw(self, channel: int, offset_val: int, force: bool = False):
        """
        Set the analog offset with the raw DAC value. Useful for precise non-linearity
        measurements. Use :attr:`.analog_offset_raw_min` and :attr:`analog_offset_raw_max`
        to determine what values you can set.

        .. Note:: This value is unable to be read back.

        :param channel: Target Channel
        :param offset_percent: The analog offset in raw dac values.
        :param force: apply change even if data collection is ongoing.
        """
        data: Dict[str, Any] = {f"channel_{channel}_analog_offset_val": offset_val, "force": force}
        self.__post(self.__config_url(channel, "AnalogOffsetVal"), data)

    # _________________________________________________________________________
    # DigitalOffset
    def getDigitalOffset(self, channel: int) -> int:
        """
        Gets the digital offset applied to this channel's waveform.

        :param channel: Target Channel
        """
        route = self.__config_url(channel, "DigitalOffset")
        resp = self.__get(route)
        return resp["data"]

    def setDigitalOffset(self, channel: int, offset: int):
        """
        Sets the digital offset applied to this channel's waveform. Offset occurs AFTER
        inversion if set.

        Refer to :attr:`.adc_max_val` and :attr:`.adc_min_val` to check your unit's
            available offset range

        :param channel: Target Channel
        :param offset: Offset in ADC counts
        """
        route = self.__config_url(channel, "DigitalOffset")
        data = {f"channel_{channel}_digital_offset": offset}
        self.__post(route, data)

    # _________________________________________________________________________
    # EnableTrigger
    def getEnableTrigger(self, channel: int) -> bool:
        """
        Checks whether a channel's trigger is enabled.

        :param channel: Target Channel
        """
        route = self.__config_url(channel, "EnableTrigger")
        resp = self.__get(route)
        return bool(resp["data"])

    def setEnableTrigger(self, channel: int, enable: bool, force: bool = False):
        """
        Enables or disables a channel's trigger.

        :param channel: Target Channel
        :param enable: True to enable trigger. False to disable.
        :param force: apply change even if data collection is ongoing.
        """
        route = self.__config_url(channel, "EnableTrigger")
        data = {f"channel_{channel}_trigger_enabled": enable, "force": force}
        self.__post(route, data)

    # _________________________________________________________________________
    # TriggerEdge
    def getTriggerEdge(self, channel: int) -> str:
        """
        Get what edge a trigger happens for a specified channel.
        :param channel: channel to get the trigger edge data from.
        """
        route = self.__config_url(channel, "TriggerEdge")
        resp = self.__get(route)
        return str(resp["data"])

    def setTriggerEdge(
        self,
        channel: int,
        direction: Union[Union[Literal["rising"], Literal["falling"]], int],
        force: bool = False,
    ):
        """
        Set a rising or falling edge trigger mode

        :param channel: Target Channel
        :param direction: "rising" for Rising Edge Trigger. "falling" for falling edge trigger
        :param force: apply change even if data collection is ongoing.
        """
        route = self.__config_url(channel, "TriggerEdge")
        data: Dict[str, Any] = {
            f"channel_{channel}_trigger_edge": direction,
            "force": force,
        }
        self.__post(route, data)

    # _________________________________________________________________________
    # TriggerSensitivity
    def getTriggerSensitivity(self, channel: int) -> int:
        """
        Gets the differential trigger threshold for the target channel.

        :param channel: channel to obtain the trigger threshold of.
        """
        route = self.__config_url(channel, "TriggerSensitivity")
        resp = self.__get(route)
        return int(resp["data"])

    def setTriggerSensitivity(self, channel: int, sensitivity: int, force: bool = False):
        """
        Sets the differential trigger threshold. When the difference between
        samples exceeds this value, the channel will trigger will fire (if enabled)

        Refer to :attr:`.trigger_sensitivity_min` and :attr:`.trigger_sensitivity_max`
            your unit's available range of trigger sensitivity values.

        .. Note:: Differential Trigger is subject to averaging.

            see :meth:`.setTriggerAveragingWindow`

        :param channel: Target Channel
        :param sensitivity: Differential threshold of the trigger in ADC counts.
        :param force: apply change even if data collection is ongoing.
        """
        route = self.__config_url(channel, "TriggerSensitivity")
        data: Dict[str, Any] = {
            f"channel_{channel}_trigger_sensitivity": sensitivity,
            "force": force,
        }
        self.__post(route, data)

    # _________________________________________________________________________
    # TriggerAveraging
    def getTriggerAveragingWindow(self, channel: int) -> int:
        """
        Get the duration of the leading and trailing summation windows in ADC samples.
        :param channel: channel to get the trigger averaging window of.
        """
        route = self.__config_url(channel, "TriggerAveragingWindow")
        resp = self.__get(route)
        return int(resp["data"])

    def setTriggerAveragingWindow(self, channel: int, window_width: int, force: bool = False):
        """
        Sets the width of the Differential Trigger's smoothing filter.
        Must be a power of 2. See :attr:`.filter_window_width_values` for a list of valid
        sizes.

        :param channel: Target Channel
        :param window_width: Number of trigger differentials (B-A) to average before checking
            against the trigger sensitivity.
        :param force: apply change even if data collection is ongoing.
        """
        route = self.__config_url(channel, "TriggerAveragingWindow")
        if window_width % 2 != 0 and window_width != 1:
            raise ValueError("Window width must be a power of two!")
        data: Dict[str, Any] = {
            f"channel_{channel}_trigger_averaging_window": window_width,
            "force": force,
        }
        self.__post(route, data)

    # _________________________________________________________________________
    # HistogramScaling
    def getHistogramScaling(self, channel: int) -> int:
        """
        Get the state of the histogram scaling for a specified channel

        :param channel: Target Channel
        """
        route = self.__config_url(channel, "HistogramScaling")
        resp = self.__get(route)
        return resp["data"]

    def setHistogramScaling(self, channel: int, state: int):
        """
        Set the histogram scaling for a specified channel, if state is 1, this bins histogram quantities by 2
        otherwise for 0, do not bin. To cover the whole positive ADC range state must 1

        :param channel: Target Channel
        :param state: 1 to scale histograms by factor of two, 0 for no scaling
        """
        route = self.__config_url(channel, "HistogramScaling")
        data = {f"channel_{channel}_histogram_scaling": state}
        self.__post(route, data)

    # _________________________________________________________________________
    # HistogramQuantity
    def getHistogramQuantity(self, channel: int) -> str:
        """
        Get the quantity histogrammed at each event, check setHistogramQuantity for the meanings of values

        .. Note:: Histogram Quantities must be greater than 0.

            Quantities less than or equal to zero will be placed in the underflow bin (bin0).

        :param channel: Target Channel
        """
        route = self.__config_url(channel, "HistogramQuantity")
        resp = self.__get(route)
        return str(resp["data"])

    def setHistogramQuantity(
        self,
        channel: int,
        quantity: Literal["pulse_height", "qdc_rect", "qdc_tri", "trigger_height"],
    ):
        """
        Set the quantity histogrammed at each event. See the FemtoDAQ Operations manual
        for in depth information about quantity calculation

        Possibile quantities are:
            - "pulse_height": The maximum pulse height as found in the pulse height window after averaging
            - "trigger_height": the maximum value of the trigger after averaging
            - "qdc_rect": Running sum over PH window without averaging.
            - "qdc_tri": Running average of PH window sum (average of qdc_rect).

        :param channel: Target Channel
        :param quantity: desired quantity to histogram
        """
        route = self.__config_url(channel, "HistogramQuantity")
        data = {f"channel_{channel}_histogram_quantity": quantity}
        self.__post(route, data)

    # Helper function to get the maximum/minimum values that can be histogrammed in firmware
    def getHistogramValueRange(self, channel: int) -> Tuple[int, int]:
        """
        Returns a tuple of the minimum/maximum quantity values that can be histogrammed
        for this channel

        :param channel: Target Channel

        :return: a tuple (min_val, max_val) of quantity values that can be histogrammed
            with the current scaling configuration. Quantity values outside of this range
            will be either be placed into the underflow bin (0) or overflow bin (the final bin)
        """
        # Adding 1 turns a boolean into scale factor. This is also future proof if we allow more
        # scaling in the future
        scale_factor = self.getHistogramScaling(channel) + 1
        return (self.fpga_data["hist_min_val"], (scale_factor * self.fpga_data["hist_max_val"]))

    # _________________________________________________________________________
    # InvertADCSignal
    def setInvertADCSignal(self, channel: int, invert: bool, force: bool = False):
        """
        Enable or disable ADC signal inversion. This occurs before all other offsets or averaging

        :param channel: Target Channel
        :param invert: A boolean representing whether to invert or not invert the ADC channel
        :param force: apply change even if data collection is ongoing.
        """
        self.__post(
            self.__config_url(channel, "InvertADCSignal"),
            {f"channel_{channel}_invert_adc_signal": invert, "force": force},
        )

    def getInvertADCSignal(self, channel: int) -> bool:
        """
        Get the ADC inversion status of a channel

        :param channel: Target Channel
        """
        return bool(self.__get(self.__config_url(channel, "InvertADCSignal"))["data"])

    # _________________________________________________________________________
    def zeroHistogram(self, channel: int):
        """Reset the histogram for a given channel"""
        self.__post(self.url + f"/rest/config/{channel}/ZeroHistogramCounts")

    ###########################################################################
    #           High Level Configuration of GUI/Web Server operations
    ###########################################################################
    # _________________________________________________________________________
    def configureCoincidence(
        self,
        coincidence_mode: Literal["hit_pattern", "multiplicity"],
        trigger_multiplicity: Optional[int] = None,
        trigger_hit_pattern: Optional[Dict[str, str]] = None,
        force: bool = False,
    ):
        """
        Configures coincidence prior to an experimental run.

        :param mode: the coincidence mode for triggering. Must be one of two options.
            - "multiplicity" : global trigger requires at least the specified number of individual channels to trigger
            - "hit_pattern"  : global trigger requires specific channels to trigger or not trigger. AKA coincidence/anti-coincidence/ignore hit pattern

        :param multiplicity: Required if mode = "multiplicity".
            The minimum number of individual channel triggers required to define an Event. This arugment is ignored if mode is "hit_pattern"

        :param hit_pattern: Required if mode = "hit_pattern". This argument must be a dictionary. Keys are "channel_{channel}_trigger_hit_pattern",
            and value is one of:

                * 'COINCIDENCE'     : If a trigger is required on this channel
                * 'ANTICOINCIDENCE' : If a trigger is not allowed on this channel
                * 'IGNORE'          : If triggers on this channel have no impact on Event

            All channels must be present when presented to configureCoincidence. A simple builder
            for configureCoincidence is helpers.HitPatternCoincidenceBuilder which will fill in unspecified items with "IGNORE" exists.
            This arugment is ignored if mode is "multiplicity"

        :param force: apply change even if data collection is ongoing.

        Hit Pattern Example
        -------------------

        .. code-block:: python
            :linenos:

            hit_pattern = {"channel_0_trigger_hit_pattern" : "COINCIDENCE", "channel_1_trigger_hit_pattern" : "ANTICOINCIDENCE"}
            digitizer.configureCoincidence("hit_pattern", hit_pattern=hit_pattern)


        Multiplicity Example
        --------------------

        .. code-block:: python
            :linenos:

            multiplicity = 3
            digitizer.configureCoincidence("multiplicity", multiplicity=multiplicity)

        """
        t: Dict[str, Any] = {"coincidence_mode": coincidence_mode, "force": force}
        if coincidence_mode not in ["multiplicity", "hit_pattern"]:
            raise ValueError("Invalid mode pattern!")
        if coincidence_mode == "multiplicity":
            if trigger_multiplicity is None:
                raise ValueError("If mode is multiplicity, the multiplicity must be defined!")
            t["trigger_multiplicity"] = trigger_multiplicity

        if coincidence_mode == "hit_pattern":
            if trigger_hit_pattern is None:
                raise ValueError("If mode is hit_pattern, the hit pattern must be defined!")

            for channel in self.channels:
                if f"channel_{channel}_trigger_hit_pattern" not in trigger_hit_pattern:
                    raise ValueError("A channel has been unspecified for behavior!")
            for item in trigger_hit_pattern:
                t[item] = trigger_hit_pattern[item]

        self.__post(self.__config_url("global", "Coincidence"), t, print_failure=False)

    # _________________________________________________________________________
    def getCoincidenceSettings(self) -> Dict[str, Any]:
        """
        Obtain the current Coincidence settings.

        """
        orig_dict = self.__get(self.__config_url("global", "Coincidence"))["data"]
        tack_on_dict = {}
        for channel in self.channels:
            tack_on_dict[f"channel_{channel}_trigger_hit_pattern"] = orig_dict[f"channel_{channel}_trigger_hit_pattern"]
            del orig_dict[f"channel_{channel}_trigger_hit_pattern"]
        orig_dict["trigger_hit_pattern"] = tack_on_dict
        return orig_dict

    # _________________________________________________________________________
    def configureRecording(
        self,
        channels_to_record: Sequence[int],
        number_of_samples_to_capture: int = 512,
        file_recording_name_prefix: str = "API_Recording",
        file_recording_format: str = "gretina",
        file_recording_data_output: Literal["waveforms", "both", "pulse_summaries", "all_possible"] = "all_possible",
        recording_directory: Optional[str] = None,
        seq_file_size_MB: int = 100,
        only_record_triggered: bool = False,
        file_recording_enabled: bool = True,
        waveform_display_enabled: bool = False,
        display_channels: Sequence[int] = [],
        events_to_capture: int = 1000,
    ):
        """
        Configures file recording prior to an experimental run.

        :param channels_to_record: channels to record
        :param number_of_samples_to_capture: The number of samples each channel will record. Must be a multiple of 64.
        :param file_recording_name_prefix: The prefix for files being generated by the FemtoDAQ device
        :param file_recording_format: The format the file is stored in, check :meth:`.getRecordingFormatInfo` for available formats.
        :param file_recording_data_output: The data products to record.
                 "waveforms" for just waveforms,
                 "pulse_summaries" for just pulse summaries,
                 "both" for both,
                 "all_possible" to automatically save all possible data products,
        :param recording_directory: The directory to record the files to on the target device, either `/data/` or `/mnt/` or derived paths
        :param seq_file_size_MB: Size of the sequence file in megabytes
        :param only_record_triggered: Set to True to only record triggered channels, not all formats support this.
        :param file_recording_enabled: Enable recording to file, presumably you want this.
        :param waveform_display_enabled: Enable or disable waveform display, it is faster to not display the waveform.
        :param display_channels: Enable channels for GUI display, performance hit to have on, do not use this unless required.
        :param events_to_capture: Optional - primarily used for making configuration files. Number of events to capture by default for the next run.
            Overwritten by the "how_many" argument in the `start` function

        :raise ValueError: if an invalid file format is specified
        """
        if file_recording_data_output.lower() == "all_possible":
            rec_format_info = self.getRecordingFormatInfo()

            if file_recording_format not in rec_format_info:
                raise ValueError(
                    f"invalid file_recording_format '{file_recording_format}' specified. Possible options are: {sorted(rec_format_info.keys())}"
                )

            info = rec_format_info[file_recording_format]
            if info["supports_trace"] and info["supports_pulse_summary"]:
                file_recording_data_output = "both"
            elif info["supports_trace"]:
                file_recording_data_output = "waveforms"
            elif info["supports_pulse_summary"]:
                file_recording_data_output = "pulse_summaries"

        extra_dict: Dict[str, bool] = {}
        for channel in self.channels:
            extra_dict[f"channel_{channel}_file_recording_enabled"] = channel in channels_to_record
            extra_dict[f"channel_{channel}_waveform_display_enabled"] = channel in display_channels

        t: Dict[str, Any] = {
            "file_recording_name_prefix": file_recording_name_prefix,
            "file_recording_format": file_recording_format.lower(),
            "file_recording_data_output": file_recording_data_output,
            "recording_directory": recording_directory,
            "seq_file_size_MB": seq_file_size_MB,
            "only_record_triggered": only_record_triggered,
            "number_of_samples_to_capture": number_of_samples_to_capture,
            "file_recording_enabled": file_recording_enabled,
            "waveform_display_enabled": waveform_display_enabled,
            "events_to_capture": events_to_capture,
        }
        for key in extra_dict:
            t[key] = extra_dict[key]

        self.__post(self.__config_url("global", "RecordingSettings"), t)

    def getRecordingSettings(self) -> Dict[str, Any]:
        """
        Get the current recording settings, this will return a dictionary of values exactly the same as the parameters used for configureRecording.
        """
        settings_to_transformed = self.__get(self.__config_url("global", "RecordingSettings"))["data"]

        channel_add_array: List[int] = []
        waveform_display_array: List[int] = []
        for channel in self.channels:
            if settings_to_transformed[f"channel_{channel}_file_recording_enabled"]:
                channel_add_array.append(channel)
            if settings_to_transformed[f"channel_{channel}_waveform_display_enabled"]:
                waveform_display_array.append(channel)

        transformed_settings = {}
        transformed_settings = dict(settings_to_transformed)
        for channel in self.channels:
            del transformed_settings[f"channel_{channel}_file_recording_enabled"]
            del transformed_settings[f"channel_{channel}_waveform_display_enabled"]
        transformed_settings["channels_to_record"] = channel_add_array
        transformed_settings["display_channels"] = waveform_display_array
        return transformed_settings

    def configureSoftwareStreaming(
        self,
        channels: Sequence[int],
        format: str,
        target_ip: str,
        target_port: Union[int, str],
        only_stream_triggered_channels: bool = False,
        enabled: bool = False,
        force: bool = False,
    ):
        """
        Configures streaming readout from software prior to an experimental run.

        :param channels: list of channels to stream during this experimental run
        :param target_ip: The IP address to stream to.
        :param target_port: The network port at the specified IP address to stream to.
        :param only_stream_triggered_channels: If True, then only record the channels
            in the `channels` list that triggered in the event. This is more efficient
            and reduces the liklihood of noise waveforms ending up in your data files.
            If left as False, the default, then all specified channels will be written
            to disk even if no trigger was detected. This is less efficient, but ensures
            that the same channels will be in each event.
        :param force: apply change even if data collection is ongoing.

        """

        ENDPOINT = self.__config_url("global", "SoftwareStreamSettings")
        self.__post(
            ENDPOINT,
            {
                "udp_streaming_enabled": enabled,
                "soft_stream_channels": channels,
                "soft_stream_dest_ip": target_ip,
                "soft_stream_dest_port": target_port,
                "soft_stream_format": format,
                "only_stream_triggered": only_stream_triggered_channels,
            },
        )

    def getSoftwareStreamSettings(self) -> Dict[str, Any]:
        """
        Retrieve the stream settings currently made for the FemtoDAQ device.
        :returns: Dict of a json packet
        The JSON packet should look like this:

        .. code-block::

            {
                "soft_stream_channels": channels,
                "soft_stream_dest_ip": target_ip,
                "soft_stream_dest_port": int | str,
                "soft_stream_format": string,
                "only_stream_triggered": bool
            }

        """
        return self.__get(self.__config_url("global", "SoftwareStreamSettings"))["data"]

    def getRunStatistics(self) -> Dict[str, Any]:
        """returns a dictionary which contains at least the following keys

        .. code-block::

            {
                "fpga_events" : int,
                "fpga_run_time" : float,
                "fpga_active_time" : float,
                "fpga_dead_time" : float,
                "recorded_events" : int,
                "recorded_bytes" : int,
                "recording_files" : int,
                "recording_duration_sec" : float,
                "is_currently_recording" : bool,
            }

        """
        url = self.__runtime_url("runStatistics")
        resp = self.__get(url)
        return resp["data"]

    def getHistogramDuration(self) -> int:
        """Gets the number of seconds the histogram is configured to run for"""
        route = self.__config_url("global", "HistogramDuration")
        resp = self.__get(route)
        return resp["data"]

    def setHistogramDuration(self, histogram_duration: int, force: bool = False):
        """
        Set the duration that a histogram run will run for

        :param histogram_duration: Time in seconds to histogram
        :param force: apply change even if data collection is ongoing.
        """
        route = self.__config_url("global", "HistogramDuration")
        self.__post(route, {"histogram_duration": histogram_duration, "force": force})

    # #########################################################################
    #        Runtime / Readout related functions
    # #########################################################################
    # _________________________________________________________________________
    # Reservations
    def isReserved(self) -> bool:
        """
        Determine if the FemtoDAQ is reserved
        """
        return self.__post(
            self.__gui_url("LOAD_JSON_FROM_FILE"),
            {"filepath": "/var/www/data/config/reserve_info.json"},
        )["data"]["reserved"]

    def getReservedInfo(self) -> Dict[str, Union[str, bool]]:
        """
        Get the reservation information of a FemtoDAQ device
        """
        return self.__post(
            self.__gui_url("LOAD_JSON_FROM_FILE"),
            {"filepath": "/var/www/data/config/reserve_info.json"},
        )["data"]

    def reserve(
        self,
        reserver_name: str,
        reserve_contact: Optional[str] = None,
        reserve_message: Optional[str] = None,
    ):
        """
        Set the reservation status of a FemtoDAQ device.
        Note: This is not strictly enforced
        """
        self.__post(
            self.__gui_url("SAVE_JSON_TO_FILE"),
            {
                "data": {
                    "reserved": True,
                    "reserve_name": reserver_name,
                    "reserve_contact": reserve_contact,
                    "reserve_message": reserve_message,
                },
                "filepath": "/var/www/data/config/reserve_info.json",
            },
        )

    def unreserve(self):
        """
        Release reservation of a FemtoDAQ device
        Note: This technically does not do anything other than say "Hey, please don't use this while I am!"
        """
        self.__post(
            self.__gui_url("SAVE_JSON_TO_FILE"),
            {
                "data": {
                    "reserved": False,
                    "reserve_name": None,
                    "reserve_contact": None,
                    "reserve_message": None,
                },
                "filepath": "/var/www/data/config/reserve_info.json",
            },
        )

    # _________________________________________________________________________
    def start(
        self,
        how_many: Union[int, Literal["continuous", "single"], None] = None,
    ) -> None:
        """
        Starts data collection for the specified number of events

        :param how_many: number of events to capture for this run. Use'continuous'
            to capture until told to stop separately.or 'single' for a single event
            (equivalent to 1). Leave as None to use the number of events defined
            previously in a configuration file or the `configureRecording` function
        """
        if isinstance(how_many, str):
            if how_many.lower() == "continuous":
                data = {"events_to_capture": 2**64 - 1}
            elif how_many.lower() == "single":
                data = {"events_to_capture": 1}
            else:
                raise ValueError("Invalid string value for how_many")
        elif isinstance(how_many, int):
            data = {"events_to_capture": how_many}
        else:
            # explicitly don't populate 'events_to_capture' which indicates
            # the Femtodaq should use the previous value
            data = {}

        self.__post(self.__gui_url("START_WAVEFORM_CAPTURE"), data)
        self.__max_wait_until_socketio_state(
            [
                self.__GUI_ENUMS.RECORDING_WAVE,
                self.__GUI_ENUMS.RUNNING_HIST,
                self.__GUI_ENUMS.RUNNING_WAVE,
            ]
        )

    # _________________________________________________________________________
    def waitUntil(
        self,
        nevents: Optional[int] = None,
        timeout_time: Optional[float] = None,
        time_to_expect_start: Optional[float] = None,
        print_status: Optional[bool] = False,
    ) -> bool:
        """
        Wait until either the number of events as received by the Digitizer has been received, or wait timeout_time seconds for a timeout.
        If both are specified, whichever completes first will be performed.
        If the recording is stopped both either condition is fulfilled or both are None, returns.

        Return a boolean indicating if waiting timed out.

        :param timeout_time: A float representing a time (in seconds) to wait for until completion until return.
        :param nevents: The minimum number of samples/events to wait for.
        :param time_to_expect_start: A time (in seconds) to wait until throwing a CollectionNotRunningError if used, it will delay timeout_time until that starts,
        :param print_status: Whether or not to print the status at the end of a wait cycle

        :return: True if waiting timed out. False if the number of events was successfully reached before timeout

        """
        NUM_STATUS_PRINTS = 10

        event_num = 0
        if timeout_time is not None:
            next_print_time = time.monotonic() + (timeout_time / NUM_STATUS_PRINTS)
        else:
            next_print_time = float("inf")

        if nevents is not None:
            next_print_event_num = event_num + int(NUM_STATUS_PRINTS / 10)
        else:
            next_print_event_num = float("inf")

        continue_waiting = True
        timed_out = False
        known_started = False
        if time_to_expect_start is not None:
            expected_start_time = time.monotonic() + time_to_expect_start
        else:
            expected_start_time = None

        with socketio.SimpleClient() as sio:
            sio.connect(self.url)
            start_time = time.monotonic()
            while continue_waiting:
                if not known_started:
                    start_time = time.monotonic()
                current_time = time.monotonic()
                if timeout_time is not None and current_time > (start_time + timeout_time):
                    continue_waiting = False
                    timed_out = True
                try:
                    event_list = sio.receive(1)
                    event_name = event_list[0]
                    if event_name == "state":
                        json_packet = json.loads(event_list[1])
                        if self.__GUI_ENUMS(json_packet["gui_state"]) in [
                            self.__GUI_ENUMS.DISCONNECTED,
                            self.__GUI_ENUMS.NOT_SETUP,
                            self.__GUI_ENUMS.READY_TO_RUN,
                        ]:
                            # NOTE: OR CONDITION, not NONE.
                            # This works by abusing short-circuiting, if expected_start_time is *NOT* none it survives!
                            if (expected_start_time is None) or (expected_start_time < current_time):
                                raise CollectionNotRunningError(
                                    f"Data collection for Vireo {self.url} is either disconnected or not running"
                                )
                        else:
                            known_started = True

                    if event_name == "data":
                        json_packet = json.loads(event_list[1])["data"]
                        event_num = json_packet["event_number"]
                        if self.verbose:
                            print(f"{self}: Collected {event_num} events.. ")
                        if nevents is not None and event_num >= nevents:
                            break

                except TimeoutError:
                    if not known_started:
                        if (expected_start_time is None) or (expected_start_time < current_time):
                            raise CollectionNotRunningError(
                                f"Data collection for Vireo {self.url} is either disconnected or not running"
                            )
                except socketio.exceptions.TimeoutError:
                    if not known_started:
                        if (expected_start_time is None) or (expected_start_time < current_time):
                            raise CollectionNotRunningError(
                                f"Data collection for Vireo {self.url} is either disconnected or not running"
                            )

                if (current_time >= next_print_time) or (event_num > next_print_event_num):
                    if timeout_time:
                        next_print_time += timeout_time / NUM_STATUS_PRINTS

                    if nevents:
                        next_print_event_num += int(nevents / 10)

                    if self.verbose or print_status:
                        print(
                            f"{self}: collected {event_num} {f'out of {nevents} events ({100 * event_num / nevents:.1f}% complete)' if nevents else ''} events. running time: {current_time - start_time:.1f}sec"
                        )
        if self.verbose or print_status:
            print(f"{self}: Data Collection Complete")
        return timed_out

    # _________________________________________________________________________
    def stop(self) -> None:
        """Stop waveform capture"""
        self.__post(self.__gui_url("STOP_WAVEFORM_CAPTURE"))
        self.__max_wait_until_socketio_state(
            [
                self.__GUI_ENUMS.DISCONNECTED,
                self.__GUI_ENUMS.READY_TO_RUN,
                self.__GUI_ENUMS.NOT_SETUP,
            ]
        )

    # _________________________________________________________________________
    # Timestamps
    # _________________________________________________________________________
    def zeroTimestamp(self, force: bool = False):
        """
        Zero the FPGA timestamp. Future timestamps will start incrementing at 0.

        :param force: apply change even if data collection is ongoing.
        """
        route = self.__runtime_url("ClearTimestamp")
        data = {"clear_timestamp": True, "force": force}
        self.__post(route, data)

    # _________________________________________________________________________
    def getLastEventTimestamp(self) -> int:
        """
        Get the timestamp for last FPGA event.

        .. attention::

            This timestamp is calculated in firmware and does not account for coincidence
            conditions. It is not guarenteed to match the most recent timestamp saved to disk.
        """
        route = self.__runtime_url("GetTimestamp")
        return self.__get(route)["data"]

    # #########################################################################
    # Debugging readout
    # #########################################################################
    def forceTrigger(self) -> None:
        """Forces a trigger regardless of coincidence conditions"""
        self.__post(self.__gui_url("FORCE_TRIGGER"))

    # _________________________________________________________________________
    def inspectNextEvent(
        self, channels_to_inspect: Optional[Sequence[int]] = None, max_timeout: Optional[float] = 10
    ) -> EventInfo:
        """
        Returns the next event that meets coincidence conditions as specified by
        the `configureCoincidence` and `configureRecording` functions

        Data Collection must ongoing (ie. :meth:`.start` has been run), or this operation will hang until timeout.

        .. Attention::

            This function is intended for debugging or inspection work, it is NOT intended to readout during data collection.
            Readout via this method will be orders of magnitude slower than using your FemtoDAQ's recording or streaming systems

        See `configureRecording` for information about configuring recording
        See `configureSoftwareStreaming` for information about configuring streaming

        :param channels_to_inspect: The channels to inspect, a default of "None" means "all"
        :param max_timeout: Timeout for receiving the inspected waveform in seconds. This parameter is defaulted to 10 seconds.
        """
        if channels_to_inspect is None:
            channels_to_inspect = self.channels
        inspect_url = self.__gui_url("INSPECT_WAVEFORM")
        return_val: List[ChannelData] = []
        received_data = False
        try:
            with socketio.SimpleClient() as sio:
                sio.connect(self.url)
                self.__post(inspect_url, data={"channels_to_inspect": channels_to_inspect})
                current_time = time.time()
                # This works based on short-circuit logic, python implements short-circuit logic
                # if max_timeout is None the latter condition never runs
                while max_timeout is None or (current_time + max_timeout) > time.time():
                    try:
                        temp_timeout = None
                        if max_timeout is not None:
                            temp_timeout = max_timeout / 10
                        event_list = sio.receive(temp_timeout)
                        event_name = event_list[0]
                        if event_name == "inspect_data":
                            json_packet = json.loads(event_list[1])["data"]
                            for channel in self.channels:
                                channel_name = f"plot_data_channel_{channel}"
                                if channel_name in json_packet:
                                    summary = json_packet[f"pulse_summary_channel_{channel}"]
                                    channel_data = json_packet[channel_name]
                                    if len(channel_data) != 0:
                                        channel_data = np.asarray(channel_data)
                                    return_val.append(
                                        ChannelData(
                                            channel,
                                            event_timestamp=summary["timestamp"],
                                            pulse_summary=summary,
                                            wave=channel_data,
                                        )
                                    )
                            received_data = True
                            break
                    except socketio.exceptions.TimeoutError:
                        pass
                if not received_data:
                    raise TimeoutError("maximum timeout was reached")
        finally:
            self.clearInspectEvent()
        return EventInfo(return_val)

    def getInspectionArmed(self) -> bool:
        """
        Get whether an inspection was armed with inspectNextEvent but was uncleared.
        """
        return self.__get(self.__config_url("global", "InspectNextEventArmed"))["data"]

    def clearInspectEvent(self):
        """
        Clear inspection event arming.
        This is used internally to clear an armed inspectNextEvent after a timeout, as the architecture requires this.
        This also allows you to clear an armed inspection before attempting another inspection
        """
        self.__post(self.__gui_url("CLEAR_INSPECT_WAVEFORM"))

    # _________________________________________________________________________
    def getHistogramData(self, channel_or_all: Union[int, Literal["all"]]) -> OurNumpyArrType:
        """ """
        if channel_or_all not in self.channels and channel_or_all not in [
            "global",
            "all",
        ]:
            raise ValueError(
                "The value for channel_or_all must be an integer that is a channel in the unit or in 'global' or 'all'"
            )

        raw_hists = self.__get(self.url + f"/rest/{channel_or_all}/HistogramData")["data"]

        return np.asarray(raw_hists).transpose()

    # #########################################################################
    # Data Files
    # #########################################################################
    def getListOfDataFiles(self, last_run_only: bool = False) -> Sequence[str]:
        """
        Get the list of all remote data files.

        :param last_run_only: If true, only gets the data files recorded in the last run.
        """
        json_data = {"file_extension": "ALL"}
        route = self.__gui_url("GET_LIST_OF_FILES")
        resp = self.__post(route, json_data)
        files: List[str] = []
        for filedata in resp["data"]:
            if last_run_only:
                if filedata.get("collected_during_last_run", False):
                    files.append(filedata["filename"])
            else:
                files.append(filedata["filename"])
        return files

    # _________________________________________________________________________
    def downloadFile(
        self, filename: str, save_to: Optional[str] = None, silent: bool = False, delete_file: bool = False
    ) -> str:
        """
        Download a file from a given path, save to a location on disk, and optionally print out values

        :param filename: Remote file to download
        :param save_to: location to save that file to, or the local destionation
        :param silent: Don't print values out
        :param delete_file: Whether to delete the file found in the FemtoDAQ device. This is expected to only function with the /data/ directory of the FemtoDAQ device.

        :returns: The full path of the downloaded file
        """
        # default to the current working directory
        save_to = os.getcwd() if (save_to is None) else save_to
        # make sure we have write permissions to the directory
        assert os.access(save_to, os.W_OK), f"Unable to write files to directory '{save_to}'"
        # Download the file
        download_url = self.__download_url(filename)
        dest_path = os.path.join(save_to, filename)
        try:
            urllib.request.urlretrieve(download_url, dest_path)
        except Exception:
            if not silent:
                print(f"unable to download data file '{filename}' at url '{download_url}'")
            raise

        if not silent:
            print(f"{str(self)} Controller : downloaded `{filename}` to '{dest_path}'")

        self.deleteDataFile(filename)
        return dest_path

    # _________________________________________________________________________
    def deleteDataFile(self, filename: str) -> None:
        """
        Delete a file with a specified name from the /data/ directory.
        :param filename: A filename to delete from /data/ on the FemtoDAQ device
        """
        try:
            self.__get(f"{self.url}/DELETE_FILES_FROM_DIGITIZER/{urllib.parse.quote_plus(filename)}")["data"]
        except RuntimeError:
            raise FileNotFoundError(f"Could not find {filename} on digitizer, sometimes a race can delete")

    # _________________________________________________________________________
    def downloadLastRunDataFiles(self, save_to: Optional[str] = None, delete_downloaded: bool = False) -> List[str]:
        # iterate through all run files and download them one by one
        """
        Iterate through all data files from the last run and download them.

        :param save_to: an optional parameter specifying where to save the data.
        :param delete_downloaded: When true, delete files downloaded from the FemtoDAQ device on said device.
            This is currently untested on NFS mounts and is expected not to function.
        """
        val: List[str] = []
        for filename in self.getListOfDataFiles(True):
            val.append(self.downloadFile(filename, save_to, delete_file=delete_downloaded))
        return val

    # _________________________________________________________________________
    def downloadCurrentConfig(self) -> Dict[str, Any]:
        """
        Download the current configuration as a json dictionary suitable for loading in with applyConfig
        """
        channel_formatted_ones_map: Dict[str, Union[Tuple[bool, Any], Any]] = {
            "channel_{0}_trigger_averaging_window": self.getTriggerAveragingWindow,
            "channel_{0}_trigger_sensitivity": self.getTriggerSensitivity,
            "channel_{0}_trigger_edge": self.getTriggerEdge,
            "channel_{0}_trigger_enabled": self.getEnableTrigger,
            "channel_{0}_digital_offset": self.getDigitalOffset,
            "channel_{0}_histogram_scaling": (
                self.has_histogram,
                self.getHistogramScaling,
            ),
            "channel_{0}_histogram_quantity": (
                self.has_histogram,
                self.getHistogramQuantity,
            ),
        }
        global_values_map: Dict[str, Union[Tuple[bool, Any], Any]] = {
            "trigger_x_position": self.getTriggerXPosition,
            "trigger_active_window_width": self.getTriggerActiveWindow,
            "pulse_height_window": (self.has_waveforms, self.getPulseHeightWindow),
            "baseline_restore_enable": (
                self.has_baseline_restoration,
                self.getEnableBaselineRestoration,
            ),
            "baseline_restore_exclusion": (
                self.has_baseline_restoration,
                self.getBaselineRestorationExclusion,
            ),
            "pulse_height_averaging_window": (
                self.has_histogram,
                self.getPulseHeightAveragingWindow,
            ),
            "global_id": self.getGlobalId,
            "bias_voltage_setting": (self.has_high_voltage_output, self.getBiasVoltage),
            "histogram_duration": (self.has_histogram, self.getHistogramDuration),
        }

        def reflatten_item(flatten_pattern: str, list_of_channels_enabled: List[int]) -> Dict[str, bool]:
            """
            This function takes in values and "flattens" them because we have a "flat" data structure for saving items.
            """
            reflattened_dict: Dict[str, bool] = {}
            for channel in self.channels:
                reflattened_dict[flatten_pattern.format(channel)] = channel in list_of_channels_enabled
            return reflattened_dict

        orig_dict = self.getRecordingSettings()
        orig_dict_secondary = reflatten_item("channel_{0}_file_recording_enabled", orig_dict["channels_to_record"])
        for item in orig_dict_secondary:
            orig_dict[item] = orig_dict_secondary[item]
        del orig_dict["channels_to_record"]
        orig_dict_secondary = reflatten_item("channel_{0}_waveform_display_enabled", orig_dict["display_channels"])
        del orig_dict["display_channels"]
        for item in orig_dict_secondary:
            orig_dict[item] = orig_dict_secondary[item]

        new_dict = self.getCoincidenceSettings()
        orig_dict_secondary = reflatten_item("channel_{0}_trigger_hit_pattern", new_dict["trigger_hit_pattern"])
        del new_dict["trigger_hit_pattern"]
        for key in orig_dict_secondary:
            new_dict[key] = orig_dict_secondary[key]

        for key in new_dict:
            orig_dict[key] = new_dict[key]

        if self.has_quadqdc_integration:
            base, fast, slow, tail = self.getQuadQDCWindows()
            orig_dict["qdc_tail_integration_window"] = tail
            orig_dict["qdc_fast_integration_window"] = fast
            orig_dict["qdc_base_integration_window"] = base
            orig_dict["qdc_slow_integration_window"] = slow

        for key in channel_formatted_ones_map:
            for channel in self.channels:
                map_out = channel_formatted_ones_map[key]
                if isinstance(map_out, tuple):
                    orig_dict[key.format(channel)] = map_out[1](channel)
                else:
                    orig_dict[key.format(channel)] = map_out(channel)

        for key in global_values_map:
            map_out = global_values_map[key]
            if isinstance(map_out, tuple):
                if map_out[0]:
                    orig_dict[key] = map_out[1]()
            else:
                orig_dict[key] = map_out()

        return orig_dict

    # _________________________________________________________________________
    def applyConfig(self, config_dict: Dict[str, Any]):
        """
        Apply a configuration from the dictionary!
        This is a companion function to downloadConfig, allowing you to replay a downloaded configuration on-top of a file.
        Not every item will be configured by this function! Notably items for which there are not `get` functions for will not be applied by this function!

        :param config_dict: A dictionary representing the configuration
        """
        # RULES FOR THIS LIST:
        # WE DECODE BY DOING CHECKS AGAINST {item}_{channel}_{number}_{item we are decoding as for the json input}
        channel_formatted_ones_map: Dict[str, Union[Tuple[bool, Any], Any]] = {
            "channel_{0}_trigger_averaging_window": self.setTriggerAveragingWindow,
            "channel_{0}_trigger_sensitivity": self.setTriggerSensitivity,
            "channel_{0}_trigger_edge": self.setTriggerEdge,
            "channel_{0}_trigger_enabled": self.setEnableTrigger,
            "channel_{0}_digital_offset": self.setDigitalOffset,
            "channel_{0}_analog_offset": self.setAnalogOffsetPercent,
            "channel_{0}_histogram_scaling": (
                self.has_histogram,
                self.setHistogramScaling,
            ),
            "channel_{0}_histogram_quantity": (
                self.has_histogram,
                self.setHistogramQuantity,
            ),
        }
        global_values_map: Dict[str, Any] = {
            "trigger_x_position": self.setTriggerXPosition,
            "trigger_active_window_width": self.setTriggerActiveWindow,
            "pulse_height_window": self.setPulseHeightWindow,
            "baseline_restore_enable": (
                self.has_baseline_restoration,
                self.setEnableBaselineRestoration,
            ),
            "baseline_restore_exclusion": (
                self.has_baseline_restoration,
                self.setBaselineRestorationExclusion,
            ),
            "pulse_height_averaging_window": self.setPulseHeightAveragingWindow,
            "global_id": self.setGlobalId,
            "bias_voltage_setting": (self.has_high_voltage_output, self.setBiasVoltage),
            "histogram_duration": (self.has_histogram, self.setHistogramDuration),
        }

        def decode_and_call_chans(
            json_value: Dict[str, Any],
            channel_to_func_map: Dict[str, Any],
        ):
            # Yes I know this is M*N, you do this better if you want to complain about the complexity of a settings
            # initialization function while not changing the interface
            for key in channel_to_func_map:
                for channel in self.channels:
                    formatted_key = key.format(channel)
                    if formatted_key in json_value:
                        # This *DOES* mean that invalid values where it throws a runtime error will not be caught, sadly.
                        try:
                            mapped_val = channel_to_func_map[key]
                            if isinstance(mapped_val, tuple):
                                if mapped_val[0]:
                                    mapped_val[1](channel, json_value[formatted_key])
                            else:
                                mapped_val(channel, json_value[formatted_key])
                        except RuntimeError:
                            pass

        # Clone the dictionary
        my_json = dict(config_dict)
        coincidence_params = [
            "coincidence_mode",
            "trigger_multiplicity",
            "trigger_hit_pattern",
        ]
        recording_params = [
            "channels_to_record",
            "number_of_samples_to_capture",
            "file_recording_name_prefix",
            "file_recording_format",
            "file_recording_data_output",
            "recording_directory",
            "seq_file_size_MB",
            "only_record_triggered",
            "file_recording_enabled",
            "waveform_display_enabled",
            "display_channels",
            "events_to_capture",
        ]

        def unflatten_item(format_string: str, dict_to_check: Dict[str, Any]) -> List[int]:
            returned_list: List[int] = []
            for channel in self.channels:
                if format_string.format(channel) in dict_to_check and dict_to_check[format_string.format(channel)]:
                    del dict_to_check[format_string.format(channel)]
                    returned_list.append(channel)
            return returned_list

        my_json["channels_to_record"] = unflatten_item("channel_{0}_recording_enabled", my_json)
        my_json["display_channels"] = unflatten_item("channel_{0}_waveform_display_enabled", my_json)
        my_json["trigger_hit_pattern"] = unflatten_item("channel_{0}_trigger_hit_pattern", my_json)
        calling_thing = {}
        for item in coincidence_params:
            calling_thing[item] = my_json[item]

        self.configureCoincidence(**calling_thing)  # type: ignore
        calling_thing = {}
        for item in recording_params:
            calling_thing[item] = my_json[item]
        self.configureRecording(**calling_thing)  # type: ignore

        if "dac_value" in my_json and "voltage" in my_json:
            raise ValueError("A raw bias voltage and bias voltage have both been specified!")
        try:
            self.__post(self.__config_url("global", "QuadQDCWindows"), my_json)
            self.__post(self.__config_url("global", "BiasVoltage"), my_json)
            for key in global_values_map:
                map_value = global_values_map[key]
                if isinstance(map_value, tuple):
                    if map_value[0]:
                        map_value[1](my_json[key])
                else:
                    map_value(my_json[key])
        except RuntimeError:
            pass
        decode_and_call_chans(my_json, channel_formatted_ones_map)

    # ____________________________________________________________________________
    def saveCurrentConfig(self, setting_name: str):
        """pulls settings dictionary and then saves it to a JSON file in /var/www/data
        --> Identical to Save Configuration Button in GUI
        """
        my_current_config = self.downloadCurrentConfig()
        data: Dict[str, Any] = {
            "data": my_current_config,
            "filepath": f"/var/www/data/setup/{setting_name}.json",
        }
        self.__post(self.__gui_url("SAVE_JSON_TO_FILE"), data)

    # ____________________________________________________________________________
    def loadandApplyExistingConfig(self, setting_name: str):
        """loads a JSON file from /var/www/data loads and apply settings dictionary from JSON
        --> Identical to Load Configuration Button in GUI
        """
        my_json = self.__post(
            self.__gui_url("LOAD_JSON_FROM_FILE"),
            {"filepath": f"/var/www/data/setup/{setting_name}.json"},
        )["data"]
        self.applyConfig(my_json)

    # ____________________________________________________________________________
    def loadDefaultConfig(self):
        """Load and apply the default configuration (default.json) of the digitizer"""
        self.loadandApplyExistingConfig("default")

    # #########################################################################
    #                       Version and Status
    # #########################################################################
    def getSoftwareVersion(self):
        """Returns the FemtoDAQ device Software version"""
        return self.__get(self.url + "/rest/data/SoftwareVersion")["data"]["software_version"].strip()

    # _________________________________________________________________________
    def getFirmwareVersion(self):
        """Returns the FemtoDAQ device Firmware version"""
        return self.__get(self.url + "/rest/data/FirmwareVersion")["data"]["firmware_version"].strip()

    # _________________________________________________________________________
    def getImageVersion(self):
        """Returns the image version of the FemtoDAQ device"""
        return self.__get(self.url + "/rest/data/ImageVersion")["data"]["image_version"].strip()

    # _________________________________________________________________________
    def getStreamFormatInfo(self):
        """Returns the supported software streaming formats and their capabilities"""
        return self.__get(self.url + "/rest/data/SoftwareStreamingFormats")["data"]

    # _________________________________________________________________________
    def getRecordingFormatInfo(self) -> Dict[str, Any]:
        """Returns the supported recording formats and their capabilities"""
        raw_list = self.__get(self.url + "/rest/data/RecordingFormats")["data"]["format_list"]
        output: Dict[str, str] = {}
        for rec_format_info in raw_list:
            output[rec_format_info["name"]] = rec_format_info

        return output

    # _________________________________________________________________________
    def summary(self) -> str:
        """Obtain a string summary of the FemtoDAQ device"""
        summary = (
            f"{self}"
            f"\nProduct Revision    : {self.fpga_data['product']}"
            f"\nNumber of Channels  : {self.num_channels}"
            f"\nSampling Frequency  : {self.frequency} MHz"
            f"\nADC Bitdepth        : {self.bitdepth} bits"
            f"\nMaximum Wave Length : {self.wave_duration_us:.2f}us"
            f"\nFirmware Version    : {self.getFirmwareVersion()}"
            f"\nSoftware Version    : {self.getSoftwareVersion()}"
            f"\nLinux Image Version : {self.getImageVersion()}"
        )
        return summary

    # #########################################################################
    #        General User Properties and Magic
    # #########################################################################

    # _________________________________________________________________________
    @property
    def product_name(self) -> str:
        """Get the short name of the FemtoDAQ product"""
        return self.fpga_data["product_short"]

    # _________________________________________________________________________
    @property
    def serial_number(self) -> str:
        """Get the serial name of the product"""
        return self.fpga_data["serial_num_str"]

    # _________________________________________________________________________
    @property
    def clk_period_ns(self) -> int:
        """period of each clock cycle in nanoseconds"""
        return int(self.fpga_data["clk_period_ns"])

    # _________________________________________________________________________
    @property
    def frequency(self):
        """The ADC sampling rate in MHz"""
        freq = 1e9 / self.clk_period_ns / 1e6  # MHz
        return freq

    # _________________________________________________________________________
    @property
    def bitdepth(self) -> int:
        """The number of bits in the ADC"""
        return int(self.fpga_data["bitdepth_wave"])

    # _________________________________________________________________________
    @property
    def name(self) -> str:
        """Get the whole name of the product, being product-serial number"""
        return f"{self.product_name}-{self.serial_number}"

    # _________________________________________________________________________
    @property
    def num_channels(self) -> int:
        """The number of channels in the product"""
        return int(self.fpga_data["num_channels"])

    # _________________________________________________________________________
    @property
    def channels(self) -> Sequence[int]:
        """A list of all channels in the product"""
        return list(range(0, self.num_channels))

    # _________________________________________________________________________
    @property
    def num_wave_samples(self) -> int:
        """Number of samples in a max-size waveform"""
        return int(self.fpga_data["num_wave_samples"])

    # _________________________________________________________________________
    @property
    def wave_duration_us(self) -> float:
        """Returns the maximum duration of a waveform in microseconds"""
        return round(self.num_wave_samples * self.clk_period_ns / 1000, 2)

    # _________________________________________________________________________
    @property
    def wave_max_val(self) -> int:
        """Maximum value in the wave"""
        return int(self.fpga_data["constraints"]["wave_max_val"])

    # _________________________________________________________________________
    @property
    def wave_min_val(self) -> int:
        """Minimum value in the wave"""
        return int(self.fpga_data["constraints"]["wave_min_val"])

    # _________________________________________________________________________
    @property
    def num_hist_bins(self) -> int:
        """Number of bins in a histogram"""
        return int(self.fpga_data["num_hist_samples"])

    # _________________________________________________________________________
    @property
    def quadqdc_window_min(self) -> int:
        return int(self.fpga_data["constraints"]["quadqdc_window_min"])

    # _________________________________________________________________________
    @property
    def quadqdc_window_max(self) -> int:
        return int(self.fpga_data["constraints"]["quadqdc_window_max"])

    # _________________________________________________________________________
    @property
    def adc_max_val(self) -> int:
        """Maximum ADC value of the product"""
        return int(self.fpga_data["constraints"]["adc_max_val"])

    # _________________________________________________________________________
    @property
    def adc_min_val(self) -> int:
        """Minimum ADC value of the product"""
        return int(self.fpga_data["constraints"]["adc_min_val"])

    # _________________________________________________________________________
    @property
    def bias_voltage_raw_max(self) -> int:
        """Maximum raw DAC value allowed by the Bias Voltage system"""
        return int(self.fpga_data["constraints"]["hv_max_val"])

    # _________________________________________________________________________
    @property
    def bias_voltage_raw_min(self) -> int:
        """Minimum raw DAC value allowed by the Bias Voltage system"""
        return int(self.fpga_data["constraints"]["hv_min_val"])

    # _________________________________________________________________________
    @property
    def bias_voltage_max(self) -> int:
        """Maximum voltage that can be generated by the Bias Voltage system"""
        return int(self.fpga_data["constraints"]["hv_max_voltage"])

    # _________________________________________________________________________
    @property
    def bias_voltage_min(self) -> int:
        """Minimum raw DAC value allowed by the Bias Voltage system"""
        return int(self.fpga_data["constraints"]["hv_min_voltage"])

    # _________________________________________________________________________
    @property
    def global_id_min(self) -> int:
        """Minimum allows global ID value"""
        return int(self.fpga_data["constraints"]["min_global_id"])

    # _________________________________________________________________________
    @property
    def global_id_max(self) -> int:
        """Maximum allows global ID value"""
        return int(self.fpga_data["constraints"]["max_global_id"])

    # _________________________________________________________________________
    @property
    def filter_window_width_values(self) -> Sequence[int]:
        """a list of allowed values for the Pulse Height Averaging and Trigger Averaging window width"""
        min_bit = int(self.fpga_data["constraints"]["filter_window_min_bit"])
        max_bit = int(self.fpga_data["constraints"]["filter_window_max_bit"])
        return [1 << bit for bit in range(min_bit, max_bit + 1)]

    # _________________________________________________________________________
    @property
    def trigger_sensitivity_max(self) -> int:
        """Maximum trigger sensitivity"""
        return self.adc_max_val - self.adc_min_val

    # _________________________________________________________________________
    @property
    def trigger_sensitivity_min(self) -> int:
        """Minimum trigger sensitivity"""
        return 1

    # _________________________________________________________________________
    @property
    def analog_offset_raw_min(self) -> int:
        """Minimum analog offset DAC value for each channel"""
        return int(self.fpga_data["constraints"]["offset_dac_min"])

    # _________________________________________________________________________
    @property
    def analog_offset_raw_max(self) -> int:
        """Maximum analog offset DAC value for each channel"""
        return int(self.fpga_data["constraints"]["offset_dac_max"])

    # _________________________________________________________________________
    @property
    def has_baseline_restoration(self):
        """Whether or not this unit has the automatic baseline resoration feature"""
        return bool(self.fpga_data["has_blr"])

    # _________________________________________________________________________
    @property
    def has_histogram(self):
        """Whether or not this unit has in firmware histogramming"""
        return bool(self.fpga_data["has_hist"])

    # _________________________________________________________________________
    @property
    def has_high_voltage_output(self):
        """Whether or not this unit has a high voltage bias output"""
        return bool(self.fpga_data["has_hv"])

    # _________________________________________________________________________
    @property
    def has_quadqdc_integration(self):
        """Whether or not this unit has the QuadQDC firmware module"""
        return bool(self.fpga_data["has_quadqdc"])

    # _________________________________________________________________________
    @property
    def has_spy_output(self):
        """Whether or not this unit has the SPY filter inspection module"""
        return bool(self.fpga_data["has_spy"])

    # _________________________________________________________________________
    @property
    def has_waveforms(self):
        """Whether or not this unit has waveform readout"""
        return bool(self.fpga_data["has_wave"])

    # _________________________________________________________________________
    @property
    def has_channel_timestamps(self):
        """Whether or not this unit has per-channel timestamping"""
        if "has_channel_timestamps" not in self.fpga_data:
            return False
        return bool(self.fpga_data["has_channel_timestamps"])

    # _________________________________________________________________________
    def __str__(self):
        return f"{self.name} ({self.url})"

    # _________________________________________________________________________
    def __repr__(self):
        return self.summary()


# Image Version
# Software Version
# Firmware Version
