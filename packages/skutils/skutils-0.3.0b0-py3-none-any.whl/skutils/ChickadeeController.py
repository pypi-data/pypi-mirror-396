from typing import Dict, Any, Generator, Tuple, Optional, Union, List,Sequence,Literal
from collections.abc import Iterable
import json
import pprint
import base64
import pickle
from argparse import Namespace

import requests
import numpy as np

from .helpers.parallel import run_functions_in_parallel

###############################################################################
def extract_byte(value: int, byte_index: int) -> int:
    """Extracts the specified byte from the integer"""
    shift = 8*byte_index
    byte_mask = 0xFF << shift
    return (value & byte_mask) >> shift

###############################################################################
def clear_byte(value: int, byte_index: int) -> int:
    """Zeros the specified byte from the integer"""
    shift = 8*byte_index
    byte_mask = 0xFF << shift
    all_ones = (1 << 64) - 1
    clear_mask = (all_ones & ~byte_mask)
    return (clear_mask & value)

###############################################################################
def set_byte(existing: int, byte_index: int, byte_value: int) -> int:
    """Sets the specified byte of the integer to the given value"""
    cleared_existing = clear_byte(existing, byte_index)
    shift = 8*byte_index
    write_mask = (byte_value & 0xFF) << shift # truncate to 8bit range and shift to proper location
    return (cleared_existing | write_mask)      

###############################################################################
class FpgaSignalMimic():
    """Mimics register reading/writing operations used in the Chickadee's Hardware 
    Abstraction Library. Unlike the HAL, changes are made to an internal integer
    which temporarily stores the register value until it's written to the FPGA over
    a POST request. 
    """
    # _________________________________________________________________________
    def __init__(self, value:int):
        """Initializes the FpgaSignalMimic.

        :param value: The current value of the specified register.
        """
        #: private variable representing signal value. Edit by using it's
        # property :py:attr:`~.value`
        self.__value : int  = value 
        #: True if this signal has been edited in any way. Used to indicate if
        # a new value needs to be transmitted back to the digitizer
        self.has_been_updated : bool = False  
    
    # _________________________________________________________________________
    @property
    def value(self):
        """Value of the FPGA signal. May be out of date with actual register values
        on the remote digitizer. Call :py:meth:`ChickadeeDspRemote.write_to_registers`
        to update the remote values.
        
        Any changes to this variable will cause the :py:attr:`~.has_been_updated`
        boolean to be set to True
        """
        return self.__value
    
    # _________________________________________________________________________
    @value.setter
    def value(self, new_value:int):
        self.has_been_updated = True
        self.__value = new_value

    # _________________________________________________________________________
    def read(self):
        """returns the current value of this signal. 
        May be out of date with actual register values. Call :py:meth:`ChickadeeDspRemote.readback_registers`
        to get signals with the most recent register values.
        """
        return self.value

    # _________________________________________________________________________
    def write(self, value:int):
        """sets the local copy of this signal to the given value
        
        :param value: the new value for this fpga signal
        """
        self.value = value

    # _________________________________________________________________________
    def read_byte(self, byte_index:int):
        """Returns the the specified byte in the signal.

        :param byte_index: index of the byte to extract. 
            0 is least significant byte. 
        """
        return extract_byte( self.read(), byte_index )

    # _________________________________________________________________________
    def write_byte(self, byte_index:int, byte_value:int):
        """sets the the specified byte in the signal.

        :param byte_index: index of the byte to set. 
            0 is least significant byte. 
        :param byte_value: 8 bit value to set the specified byte to.
        """
        self.value = set_byte(self.value, byte_index, byte_value)

    # _________________________________________________________________________
    def set_bit(self, bit_index:int):
        """sets the specified bit to HIGH (ie. 1) in the FPGA signal

        :param bit_index: bit to set HIGH. 0 is LSB.
        """
        self.value = self.value | (1 << bit_index)
        
    # _________________________________________________________________________
    def test_bit(self, bit_index:int):
        """returns True if the specified bit is HIGH (ie. 1) in the FPGA signal

        :param bit_index: bit to set HIGH. 0 is LSB.
        """
        return (self.value & (1 << bit_index)) != 0

    # _________________________________________________________________________
    def clear_bit(self, bit_index:int):
        """sets the specified bit to LOW (ie. 0) in the FPGA signal

        :param bit_index: bit to set LOW. 0 is LSB.
        """
        all_ones = (1 << 64) - 1
        clear_mask = all_ones & ~(1<<bit_index)
        self.value = self.value & clear_mask

    # _________________________________________________________________________
    def pulse_bit(self, bit_index):
        raise NotImplementedError("pulse_bit cannot be performed remotely.")

    # _________________________________________________________________________
    def set_many_bits(self, *bit_indices:int):
        """sets the specified bit indices to HIGH (ie. 1) in the FPGA signal

        :param bit_indices: bit to set HIGH. 0 is LSB.
        """
        for bit_index in bit_indices:
            self.set_bit(bit_index)
        
    # _________________________________________________________________________
    def clear_many_bits(self, *bit_indices:int):
        """sets the specified bit indices to LOW (ie. 0) in the FPGA signal

        :param bit_indices: bit to set LOW. 0 is LSB.
        """
        for bit_index in bit_indices:
            self.clear_bit(bit_index)

###############################################################################
def dsp_dict_to_dsp_namespace(dsp_dict):
    """Converts a nested dictionary of DSP values into a nested namespace

    ie. dict['outer_key']['inner_key'] --> namespace.outer_key.inner_key
    """
    dsp_namespace = Namespace()
    for key,val in dsp_dict.items():
        if key == "CHANNELS":
            dsp_namespace.CHANNELS = {}
            for channel_id,channel_values in dsp_dict[key].items():
                dsp_namespace.CHANNELS[int(channel_id)] = dsp_dict_to_dsp_namespace(channel_values)
        # handle nested dictionaries via recursion
        elif isinstance(val, dict):
            nested_dsp_namespace = dsp_dict_to_dsp_namespace(val)
            setattr(dsp_namespace, key, nested_dsp_namespace)
        # all other numerical values should be converted into FPGA Signal mimics
        elif isinstance(val, (float,int)):
            setattr(dsp_namespace, key, FpgaSignalMimic( int(val) ))

    return dsp_namespace

###############################################################################
def dsp_namespace_to_dsp_dict(dsp_namespace, only_updated_values=True):
    """Converts a nested namespace DSP values into a nested dictionary

    ie. namespace.outer_key.inner_key --> dict['outer_key']['inner_key'] 
    """
    dsp_dict = {}
    for key,val in vars(dsp_namespace).items():
        if key == "CHANNELS":
            dsp_dict['CHANNELS'] = {}
            for channel_id,channel_values in val.items():
                dsp_dict["CHANNELS"][int(channel_id)] = dsp_namespace_to_dsp_dict(channel_values, only_updated_values)
        # handle nested dictionaries via recursion
        elif isinstance(val, Namespace):
            nested_dict = dsp_namespace_to_dsp_dict(val, only_updated_values)
            dsp_dict[key] = nested_dict
        # all other FpgaSignal mimics should be converted to numerical values with read()
        elif isinstance(val, FpgaSignalMimic):
            if (only_updated_values and val.has_been_updated):
                # only update the value if the value has been edited in any way
                dsp_dict[key] = val.read()    
            else:
                dsp_dict[key] = val.read()

    return dsp_dict

###############################################################################
def update_dsps_simultaneously(*dsps, timeout=3):
    """Updates all remote DSPS as fast as possible simultanesously."""
    transmit_funcs = [dsp.write_to_registers for dsp in dsps]
    kwargs_list = [{'timeout':timeout}] * len(transmit_funcs)

    time_taken_ns, responses = run_functions_in_parallel(transmit_funcs, kwargs_list=kwargs_list)

    for i,resp in enumerate(responses):
        if not resp.ok:
            print(f"Failed to set DSP values for {dsps[i]}: {resp.reason}")

    return time_taken_ns
    
###############################################################################
class ChickadeeDspRemote(Namespace):
    """Represents the Digital Signal Processing subsystem on the remote digitizer.
    
    Attributes on this object mimic the progamming style of the Hardware Abstraction Library
    of the Chickadee. This object contains namespaces representing blocks of registers
    within the DSP subsystem. For documentation on register blocks and signals, see your 
    Chickadee manual.

    .. code-block:: Psuedo code to write to individual DSP values:
        
        dsp = ChickadeeDspRemote(url)
        dsp.REGISTER_BLOCK.signal_name.write(value)

        dsp.write_to_registers()
        dsp.readback_registers()
        dsp.pretty_dump()
        
    """
    # _________________________________________________________________________
    def __init__(self, hostname_or_ip:str, auto_write_on_close:bool=True):
        """initializes the remote DSP for the Chickadee digitizer specified by the
        url or hostname. Edits made to FPGA signals will be local until 
        :py:meth:`.write_to_registers` is called. 
        
        :param hostname_or_ip: network address of the remote digitizer
        :param auto_write_on_close: whether or not to automatically write FPGA 
            signals to remote digitizer when this object is closed. Default is True
            to for ease of use in python context managers (use of **with** statement). 
        """
        #: url for setting/reading DSP signals
        self.control_url = hostname_or_ip + '/dsp/control'
        #: url for grabbing waveforms
        self.wave_url    = hostname_or_ip + '/dsp/wavedata'
        #: whether or not to automatically write to registers when 
        # :py:meth:`.close` is callsed
        self.auto_write_on_close = auto_write_on_close

        #: number of ADC chips on remote digitizer
        self.num_adcs             = None # defined in readback_registers()
        #: bitdepth of ADCs on remote digitizer
        self.adc_bitdepth         = None # defined in readback_registers()
        #: number of channels on remote digitizer
        self.num_channels         = None # defined in readback_registers()
        #: number of waveform samples for each channel
        self.num_waveform_samples = None # defined in readback_registers()

        self.readback_registers()

    # _________________________________________________________________________
    def __enter__(self):
        return self
    
    # _________________________________________________________________________
    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.close()
    
    # _________________________________________________________________________
    def get_transmit_info(self):
        """gets POST request transmission info for updating DSP signals"""
        url      = self.control_url
        dsp_dict = self.as_dict()
        return (url, dsp_dict)

    # _________________________________________________________________________
    def readback_registers(self):
        """Updates this object with most recent values of signals from remote digitizer.
        This will overwrite locally changed values.
        """
        all_dsp_signals = requests.get(self.control_url).json()
        self.update_from_dict(all_dsp_signals)

        self.num_adcs                  = self.FIRMWARE_DISCOVERY_REG.adc_chips_and_bits.read_byte(0) # number of ADC chips. 
        self.adc_bitdepth              = self.FIRMWARE_DISCOVERY_REG.adc_chips_and_bits.read_byte(1) # bitdepth of ADCs
        self.num_channels              = self.FIRMWARE_DISCOVERY_REG.nr_channels.read_byte(0) # number of logical channels
        self.num_waveform_samples      = self.FIRMWARE_DISCOVERY_REG.num_bram_samples.read()  # Number of waveform samples

    # _________________________________________________________________________
    def write_to_registers(self, timeout:float=3):
        """Writes changes to FPGA signals to the remote digitizer

        :param timeout: time before post request times out and write operation
            is declared a failure
        """
        url,dsp_dict = self.get_transmit_info()
        resp = requests.post(url, json=dsp_dict, timeout=timeout)
        return resp
        
    # _________________________________________________________________________
    def read_wave(self, channel:Union[int,Literal['all']], num_waveform_samples:Optional[int]=None, as_binary=True):
        """Reads the waveform for the specified channel as a numpy array
        
        This returns the waveform "as is" currently in the FPGA buffer. User
        is responsible for checking if event capture is ongoing. Check your Chickadee
        manual for details.

        :param channel: desired channel waveform
        :param num_waveform_samples: number of samples to read out for waveform. 
            use None for maximum possible number of samples
        :param as_binary: True to read the wavedata as b64 encoded string, False to use a json list
        """
        url = self.wave_url + f'/{channel}'        
        payload = {'num_waveform_samples':num_waveform_samples,
                    'waveform_as_base64':as_binary}
        resp = requests.get(url, json=payload)
        resp_data = resp.json()
        if resp_data['waveform_as_base64']:
            wavedata = pickle.loads( base64.standard_b64decode(resp_data['wavedata'].encode('utf-8')) )
        else:
            wavedata = np.asarray(resp_data['wavedata'])
        return wavedata

    # _________________________________________________________________________
    def read_all_waves(self, num_waveform_samples:Optional[int]=None, as_binary=True):
        """Reads the waveforms for all channels as 2D numpy array. 
            Shape will be (num_samples, num_channels)
        
        This returns the waveform "as is" currently in the FPGA buffer. User
        is responsible for checking if event capture is ongoing. Check your Chickadee
        manual for details.

        :param num_waveform_samples: number of samples to read out for waveform. 
            use None for maximum possible number of samples
        :param as_binary: True to read the wavedata as b64 encoded string, False to use a json list
        """
        return self.read_wave('all', num_waveform_samples, as_binary)

    # _________________________________________________________________________
    def close(self):
        """Called at the end of the context manager. Will automatically update 
        remote registers is :py:attr:`.auto_write_on_close` is set"""
        if self.auto_write_on_close:
            self.write_to_registers()

    # _________________________________________________________________________
    def dump(self):
        """prints all FPGA signals and their values"""
        pprint.pprint( self.as_dict() )

    # _________________________________________________________________________
    def pretty_dump(self):
        """prints all FPGA signals and their values"""
        self.dump()

    # _________________________________________________________________________
    def as_dict(self):
        """returns this dsp namespace as a dictionary"""
        return dsp_namespace_to_dsp_dict(self, only_updated_values=False)

    # _________________________________________________________________________
    def update_from_dict(self, dsp_dict):
        """updates this DSP namespace from a dictionary"""
        self.__dict__.update( vars(dsp_dict_to_dsp_namespace(dsp_dict)) )

    # _________________________________________________________________________
    def to_json(self):
        """converts saves all current DSP settings to a JSON string for archiving"""
        dsp_dict = self.as_dict()
        return json.dumps(dsp_dict)
    
    # _________________________________________________________________________
    def from_json(self, json_string):
        """loads DSP settings from a JSON representation. see :py:meth:`.to_json`"""
        dsp_dict = json.loads(json_string)
        self.update_from_dict(dsp_dict)
    
    # _________________________________________________________________________
    def __str__(self):
        return f"ChickadeeRemoteDSP ({self.control_url})"


###############################################################################
class ChickadeeDspBitsRemote(Namespace):
    # _________________________________________________________________________
    def __init__(self, hostname_or_ip:str):
        """Represents the control bit and name indices of the Chickadee's DSP
        
        :param hostname_or_ip: network address of the remote digitizer
        """
        dsp_bits_dict = requests.get(hostname_or_ip + "/dsp/get_control_and_status_bits").json()
        for key,value in dsp_bits_dict.items():
            setattr(self, key, value)

    # _________________________________________________________________________
    def dump(self):
        pprint.pprint( vars(self) )



###############################################################################
class ChickadeeController:
    def __init__(self, hostname_or_ip: str):
        """Initializes the controller for the chickadee associated with the specified URL
        
        :param hostname_or_ip: url or IP address for the chickadee digitizer
        """
                
        if hostname_or_ip.startswith("https://"):
            raise ValueError("Secure http not supported! (digitizer url must begin with 'http' not 'https')")
        # add http:// manually if not provided
        elif not hostname_or_ip.startswith("http://"):
            hostname_or_ip = f"http://{hostname_or_ip}"
        self.__address = hostname_or_ip

        versions = requests.get(self.address + "/sw_api/versions").json()
        # breakpoint()
        # self.__software_version: str = versions["software_version"]
        # self.__firmware_version: str = versions["firmware_version"]
        # self.__board_revision  : str = versions["board_revision"]
        # self.__board_string    : str = versions["board_string"]

        information = requests.get(self.address + "/sw_api/basic_information").json()
        # self.__num_chans       : int = information["num_channels"]
        # self.__num_adcs        : int = information["num_adcs"]
        # self.__num_samples     : int = information["num_samples"]
        # self.__num_sdac_bits   : int = information["num_sdac_bits"]

    # _________________________________________________________________________
    def remote_dsp(self,  auto_write_on_close:bool=True):
        """returns a :py:class:`ChickadeeDspRemote` object for controlling the Chickadee's
        digitial signal processing (DSP) subsystem.
        """
        return ChickadeeDspRemote(self.address, auto_write_on_close)
    
    # _________________________________________________________________________
    def dsp_bits(self):
        return ChickadeeDspBitsRemote(self.address)

    # _________________________________________________________________________
    def get_host_udp_information(self) -> Dict[str, Union[int, str]]:
        json_val: Dict[str, Union[int, str]] = requests.get(self.address + "/sw_api/host_information").json()
        return json_val

    # _________________________________________________________________________
    def set_host_udp_information(
        self,
        host_mac: Optional[Union[int, str]] = None,
        host_ip: Optional[Union[int, str]] = None,
        host_port: Optional[Union[int, str]] = None,
    ) -> None:
        req = requests.post(
            self.address + "/sw_api/host_information",
            json={"host_mac": host_mac, "host_ip": host_ip, "host_port": host_port},
        )
        self.__report_json_error(req)

    # _________________________________________________________________________
    def get_dest_udp_information(self) -> Dict[str, Union[str, int]]:
        json_val: Dict[str, Union[int, str]] = requests.get(self.address + "/sw_api/dest_information").json()
        return json_val

    # _________________________________________________________________________
    def __report_json_error(self, req: requests.Response) -> None:
        """
        Cover every base for raising an error out of the server, this function is *WHY WE NEED TO ALSO RETURN STATUS CODES AS CODES*
        """
        try:
            req.raise_for_status()
        except requests.HTTPError as e:
            try:
                val = req.json()
            except json.JSONDecodeError:
                raise RuntimeError(f"Request raised an error {e}, {req.content.decode()}")
            try:
                raise RuntimeError(f"Request returned error code: {val['code']}, description: {val['error']}")
            except KeyError as e2:
                new_err = RuntimeError(
                    f"Error: error response from the server is malformed compared to expected, expected a 'code' and 'error' field, actual: {val}"
                )
                new_err.__traceback__ = e2.__traceback__
                raise new_err

    # _________________________________________________________________________
    def set_dest_udp_information(
        self,
        dest_mac: Optional[Union[int, str]] = None,
        dest_ip: Optional[Union[int, str]] = None,
        dest_port: Optional[Union[int, str]] = None,
    ) -> None:
        req = requests.post(
            self.address + "/sw_api/dest_information",
            json={"dest_mac": dest_mac, "dest_ip": dest_ip, "dest_port": dest_port},
        )
        self.__report_json_error(req)

    # _________________________________________________________________________
    def calibrate_adc_serdes(self) -> bool:
        req = requests.post(self.address + "/sw_api/calibrate_adcs")
        self.__report_json_error(req)
        bool_val = req.json()["calibration_is_active"]
        assert isinstance(bool_val, bool)
        return bool_val

    # _________________________________________________________________________
    def get_adc_serdes_calibrating(self) -> bool:
        req = requests.get(self.address + "/sw_api/calibrate_adcs")
        self.__report_json_error(req)
        bool_val = req.json()["calibration_is_active"]
        assert isinstance(bool_val, bool)
        return bool_val

    # _________________________________________________________________________
    def get_spy_waveform(self, samples: int = 2048, channel: Optional[int] = None) -> List[int]:
        req = requests.get(self.address + "/sw_api/spy_waveform", json={"samples": samples, "channel": channel})
        self.__report_json_error(req)
        wave_arr: List[int] = req.json()["wave_arr"]
        assert isinstance(wave_arr, list)
        return wave_arr

    # _________________________________________________________________________
    def set_spy_enablement(self, enable: bool) -> None:
        req = requests.post(self.address + "/sw_api/enable_spy", json={"enable_spy": enable})
        self.__report_json_error(req)

    # _________________________________________________________________________
    def get_spy_enablement(self) -> bool:
        req = requests.get(self.address + "/sw_api/enable_spy")
        self.__report_json_error(req)
        wave_spy_enabled = req.json()["wave_spy_enabled"]
        assert isinstance(wave_spy_enabled, bool)
        return wave_spy_enabled

    # _________________________________________________________________________
    def set_sdac_offset(self, channel: Optional[int], dac_val: int) -> None:
        req = requests.post(self.address + "/sw_api/sdac_offset", json={"channel": channel, "dac_val": dac_val})
        self.__report_json_error(req)

    # _________________________________________________________________________
    def set_sdac_powerdown(self, channel: int) -> None:
        req = requests.post(self.address + "/sw_api/disable_sdac_channel", json={"channel": channel})
        self.__report_json_error(req)

    # _________________________________________________________________________
    def set_adc_firmware_inversion(self, invert: bool) -> None:
        req = requests.post(self.address + "/sw_api/invert_adc_firmware", json={"adc_firmware_invert": invert})
        self.__report_json_error(req)

    # _________________________________________________________________________
    def get_adc_firmware_inversion(self) -> bool:
        req = requests.get(self.address + "/sw_api/invert_adc_firmware")
        self.__report_json_error(req)
        json_block = req.json()
        bool_val = json_block["adc_firmware_invert"]
        if not isinstance(bool_val, bool):
            raise RuntimeError("The server failed to return a bool for adc_firmware_invert!")
        return bool_val

    # _________________________________________________________________________
    @property
    def address(self) -> str:
        return self.__address

    # # _________________________________________________________________________
    # @property
    # def software_version(self) -> str:
    #     return self.__software_version

    # # _________________________________________________________________________
    # @property
    # def firmware_version(self) -> str:
    #     return self.__firmware_version

    # # _________________________________________________________________________
    # @property
    # def board_revision(self) -> str:
    #     return self.__board_revision

    # # _________________________________________________________________________
    # @property
    # def board_string(self) -> str:
    #     return self.__board_string

    # # _________________________________________________________________________
    # @property
    # def num_channels(self) -> int:
    #     return self.__num_chans

    # # _________________________________________________________________________
    # @property
    # def num_adcs(self) -> int:
    #     return self.__num_adcs

    # # _________________________________________________________________________
    # @property
    # def num_samples(self) -> int:
    #     return self.__num_samples

    # # _________________________________________________________________________
    # @property
    # def num_sdac_bits(self) -> int:
    #     return self.__num_sdac_bits


if __name__ == "__main__":
    chickadee = ChickadeeController("http://chickadee-32-hd-1.tek:5001")
    with chickadee.remote_dsp() as dsp:
        dsp.CHANNELS[0].CONTROL_REG.digital_offset.write(10)

    # for each digitizer in an array, prepare dsp, then transmit 
    # to all digitizers simultanesously


    