

from enum import Enum
from dataclasses import dataclass


import time
import pyvisa

import numpy as np


from datetime import datetime, timedelta



class Function(Enum):
    VOLTAGE_DC = 'voltage:dc'
    CURRENT_DC = 'current:dc'
    RESISTANCE_2W = 'resistance'
    RESISTANCE_4W = 'fresistance'
    VOLTAGE_DIGITIZE = 'voltage'
    CURRENT_DIGITIZE = 'current'
    
class InputImpedance(Enum):
    # Only for VOLTAGE_DC and VOLTAGE_DIGITIZE functions
    MOHM10 = 'MOHM10'   # 10 MOhm for all ranges
    AUTO = 'AUTO'       # 10 GOhm for <100V and 10MOhm for >100V 
    
class RangeVoltageDC(Enum):
    RANGE_AUTO = ':auto on'
    RANGE_100mV = ' 100e-3'
    RANGE_1V = ' 1'
    RANGE_10V = ' 10'
    RANGE_100V = ' 100'
    RANGE_1000V = ' 1000'
    
class RangeCurrentDC(Enum):
    RANGE_AUTO = ':auto on'
    RANGE_1uA = ' 1e-6'
    RANGE_10uA = ' 10e-6'
    RANGE_100uA = ' 100e-6'
    RANGE_1mA = ' 1e-3'
    RANGE_10mA = ' 10e-3'
    RANGE_100mA = ' 100e-3'
    RANGE_1A = ' 1'
    
class ResistanceRange2W(Enum):
    RANGE_AUTO = ':auto on'
    RANGE_10OHM = ' 10'
    RANGE_100OHM = ' 100'
    RANGE_1kOHM = ' 1e3'
    RANGE_10kOHM = ' 10e3'
    RANGE_100kOHM = ' 100e3'
    RANGE_1MOHM = ' 1e6'
    RANGE_10MOHM = ' 10e6'
    RANGE_100MOHM = ' 100e6'
    
class ResistanceRange4W(Enum):
    RANGE_AUTO = ':auto on'
    RANGE_1OHM = ' 1'  
    RANGE_10OHM = ' 10'
    RANGE_100OHM = ' 100'
    RANGE_1kOHM = ' 1e3'
    RANGE_10kOHM = ' 10e3'
    RANGE_100kOHM = ' 100e3'
    RANGE_1MOHM = ' 1e6'
    RANGE_10MOHM = ' 10e6'
    RANGE_100MOHM = ' 100e6'
    
RangeType = RangeVoltageDC | RangeCurrentDC | ResistanceRange2W | ResistanceRange4W
    
class Screen(Enum):
    HOME = 'home'
    GRAPH = 'graph'
    HISTOGRAM = 'histogram'
    READINGS = 'reading_table'
    SWIPE_GRAPH = 'swipe_graph'
    SWIPE_SETTINGS = 'swipe_settings'
    SWIPE_STATISTICS = 'swipe_statistics'
    SWIPE_USER = 'swipe_user'

@dataclass
class Options:
    name: str
    ip: str
    reset: bool
    debug: bool



class DMM6500:
                     
    def __init__(self, options: Options):
        
        self.name = options.name
        self._ip = options.ip
        self._reset = options.reset
        self._debug = options.debug
        
        # Create PyVISA resource manager and connect to the DMM6500
        rm = pyvisa.ResourceManager()
        self._dmm = rm.open_resource(f"TCPIP::{self._ip}::INSTR")
        
        idn = self._dmm.query('*IDN?').strip('\n')
        self._debug_print(f"{idn} found at {self._ip}")
        
        # Parameters
        self._function: Function = None
        self._range: RangeType = None
        self._nplc: int | float = None
        self._count: int = None
        
        # Input impedance
        self._input_impedance: InputImpedance = InputImpedance.AUTO
        
        # Digitize functions parameters
        self._aperture: float = None
        self._sample_rate: int = None
        
        # Reset the instrument settings to their default values and clear the reading buffers
        if self._reset:
            self._scpi_write(f'*rst')
            self._scpi_write(f'*cls')
       
    def _debug_print(self, msg):
        if self._debug:
            print(f"[DMM6500] ({self.name} - {self._ip}): {msg}")
       
    def _scpi_write(self, cmd, sleep=10e-3):
        self._debug_print(f'write: {cmd}')
        result = self._dmm.write(cmd)
        time.sleep(sleep)
        return result
    
    def _scpi_query(self, cmd, sleep=10e-3):
        self._debug_print(f'query: {cmd}')
        result = self._dmm.query(cmd)
        time.sleep(sleep)
        return result
    
    def _scpi_query_acsii(self, cmd, sleep=10e-3):
        self._debug_print(f'ascii query: {cmd}')
        result = self._dmm.query_ascii_values(cmd)
        time.sleep(sleep)
        return result
       
    def _assert_attr_defined(self, value):
        assert value is not None, f"Attribute error: attribute must be defined before use."

    def _assert_type(self, value, expected):
        assert isinstance(value, expected), f"Type error: expected {expected}, got {type(value)}."
        
    def _assert_range(self, value, minimum, maximum):
        assert minimum <= value <= maximum, f"Value error: '{value}' is out of bounds [{minimum}, {maximum}]"
        
    ### Measurement function
    @property 
    def function(self) -> Function:
        """ Configure the active measure function. Must be an element of DMM6500.Function. """
        return self._function
    
    @function.setter
    def function(self, value: Function):
        self._assert_type(value, Function)
        self._function = value
            
    ### Measurement range
    @property
    def range(self):
        """ Configure the positive full-scale measure range. """
        return self._range
    
    @range.setter
    def range(self, value):
        self._assert_attr_defined(self.function)
        if   self.function == Function.VOLTAGE_DC:          self._assert_type(value, RangeVoltageDC)
        elif self.function == Function.CURRENT_DC:          self._assert_type(value, RangeCurrentDC)
        elif self.function == Function.RESISTANCE_2W:       self._assert_type(value, ResistanceRange2W)
        elif self.function == Function.RESISTANCE_4W:       self._assert_type(value, ResistanceRange4W)
        elif self.function == Function.VOLTAGE_DIGITIZE:    self._assert_type(value, RangeVoltageDC)
        elif self.function == Function.CURRENT_DIGITIZE:    self._assert_type(value, RangeCurrentDC)
        else: raise NotImplementedError(f"Range setting not implemented for function {self.function}.")
        self._range = value
        
    ### Input impedance for voltage measurement
    @property
    def input_impedance(self) -> InputImpedance:
        """ Configure the input impedance when measure function is voltage. Must be an element of DMM6500.InputImpedance. """
        return self._input_impedance
    
    @input_impedance.setter
    def input_impedance(self, value: InputImpedance):
        self._assert_attr_defined(self.function)
        assert self.function in [Function.VOLTAGE_DC, Function.VOLTAGE_DIGITIZE], f"Input impedance is only available for function 'VOLTAGE' and 'VOLTAGE_DIGITIZE'."
        self._assert_type(value, InputImpedance)
        self._input_impedance = value
        
    ### Number of Power Line Cycles
    @property
    def nplc(self) -> int | float:
        """ Configure the time that the input signal is measured. Must be a number between 0.0005 and 12. """
        return self._nplc
    
    @nplc.setter
    def nplc(self, value: int | float):
        self._assert_type(value, (int, float))
        self._assert_range(value, 0.0005, 12)
        self._nplc = value
        
    ### Digitize functions
    @property
    def sample_rate(self) -> int:
        """ Configure the sampling rate [readings/s] of the digitize functions. Must be an integer between 1000 and 1000000. """
        return self._sample_rate
    
    @sample_rate.setter
    def sample_rate(self, value: int):
        self._assert_attr_defined(self.function)
        assert self.function in [Function.VOLTAGE_DIGITIZE, Function.CURRENT_DIGITIZE], f"Sample rate is only available for digitize functions."
        self._assert_type(value, int)
        self._assert_range(value, 1000, 1000000)
        self._sample_rate = value
    
    @property
    def aperture(self) -> float:
        """ Configure the aperture time [s] of the digitize functions. Sampling rate must be defined before the aperture. Must be a float between 1 us and 1/(sampling rate). """
        return self._aperture
    
    @aperture.setter
    def aperture(self, value: float):
        self._assert_attr_defined(self.function)
        self._assert_attr_defined(self.sample_rate)
        assert self.function in [Function.VOLTAGE_DIGITIZE, Function.CURRENT_DIGITIZE], f"Aperture is only available for digitize functions."
        self._assert_type(value, float)
        self._assert_range(value, 1e-6, 1/self.sample_rate)
        self._aperture = value
        
    @property
    def count(self) -> int:
        """ Configure the number of measurements to make when a measurement is requested. Must be an integer between 1 and 1e6. """
        return self._count
    
    @count.setter
    def count(self, value: int):
        self._assert_type(value, int)
        self._assert_range(value, 1, 1e6)
        self._count = value
        
    ### Apply configuration
    def configure(self):
        """ Apply the configuration to the instrument. """

        digitize = ':digitize' if self.function in [Function.VOLTAGE_DIGITIZE, Function.CURRENT_DIGITIZE] else ''

        self._scpi_write(f':sense{digitize}:function "{self.function.value}"')
        self._scpi_write(f':sense{digitize}:{self.function.value}:range{self.range.value}') # White space is intentionaly removed to allow seamless usage of auto and manual mode
        self._scpi_write(f':sense{digitize}:count {self.count}')

        if digitize:
            self._scpi_write(f':sense:digitize:{self.function.value}:srate {self.sample_rate}')
            self._scpi_write(f':sense:digitize:{self.function.value}:aperture {self.aperture}')
        else:
            self._scpi_write(f':sense:{self.function.value}:nplc {self.nplc}')
            
        if (self.function == Function.VOLTAGE_DC) or (self.function == Function.VOLTAGE_DIGITIZE):
            self._scpi_write(f':sense{digitize}:{self.function.value}:inputimpedance {self.input_impedance.value}')
                        
        time.sleep(100e-3)
        
    ### Measurements
    def measure(self, count=None, buffername='defbuffer1'):
        """ Return the average of `count` measurements. Place the measurements in the buffer specified by `buffername`. If `count` is not specified, use the configured `count` attribute. """
        # The 'MEASURE?' command makes `count` measurement and store them in the specified buffer
        # But it blocks until all measurements are done, so for large `count`, the communication may time out.
        # Therefore, the measure command is here replace by a trigger model to fill the buffer.
        # And the average of the buffer is returned.
        _count = count if count is not None else self.count
        self.start_measurement(_count, buffername)
        self.wait_measurement()
        average = self.retrieve_measurements_average(buffername)
        return average
        
    def clear_measurements(self, buffername='defbuffer1'):
        """ Clear all readings and statistics of the buffer specified by `buffername`. """
        self._scpi_write(f':trace:clear "{buffername}"')
        
    def retrieve_measurements(self, buffername='defbuffer1'):
        """ Retrieve the buffer specified by `buffername`. Return a list [timestamps, values]. """
        # TODO Should retrieve the data in binary format for large buffers
        start_index = self._scpi_query_acsii(f':trace:actual:start?')[0]
        end_index = self._scpi_query_acsii(f':trace:actual:end?')[0]
        buffer = self._scpi_query_acsii(f':trace:data? {start_index}, {end_index}, "{buffername}", seconds, fractional, reading')
        timestamps = [s + f for s, f in zip(buffer[0::3], buffer[1::3])]
        values = buffer[2::3]
        return [timestamps, values]
    
    def retrieve_measurements_average(self, buffername='defbuffer1'):
        """ Retrieve the average of the buffer specified by `buffername`. """
        return self._scpi_query_acsii(f':trace:statistics:average? "{buffername}"')[0]
    
    def retrieve_measurements_stddev(self, buffername='defbuffer1'):
        """ Retrieve the standard deviation of the buffer specified by `buffername`. """
        return self._scpi_query_acsii(f':trace:statistics:stddev? "{buffername}"')[0]
    
    def start_measurement(self, count=None, buffername='defbuffer1'):
        """ Start filling the buffer specified by `buffername` with `count` measurements. """
        self._scpi_write(f':abort')
        self._scpi_write(f':trigger:load "Empty"')
        self._scpi_write(f':trigger:block:buffer:clear 1, "{buffername}"')
        _count = count if count is not None else self.count
        self._scpi_write(f':trigger:block:mdigitize 2, "{buffername}", {_count}')
        self._scpi_write(f':initiate')
        
    def wait_measurement(self): 
        """ Wait for the buffer fill trigger model to complete. """
        while self._scpi_query(':trigger:state?').split(';')[0] == 'RUNNING':
            time.sleep(self.nplc/2)
        
    def stop_measurement(self):
        """ Stop filling current buffer. """
        self._scpi_write(f':abort')
    
    def create_measurements_buffer(self, name, size, style='standard'):
        """ Create a buffer named `buffername` and of size `size`. """
        self._scpi_write(f':trace:make "{name}", {size}, {style}')
        
    def remove_measurements_buffer(self, name):
        """ Remove the buffer named `buffername`. """
        self._scpi_write(f':trace:delete "{name}"')
        
    ### Display
    def show_screen(self, screen):
        """ Change front-panel screen to `screen`. """
        self._assert_type(screen, self.Screen)
        self._scpi_write(f':display:screen {screen.value}')
        
    def clear_user_screen(self):
        """ Clear the text from the user screen. """
        self._scpi_write(':display:clear')
        
    def show_user_screen(self, line1='', line2=''):
        """ Show text on user screen. """
        self._scpi_write(f':display:user1:text "{line1}"')
        self._scpi_write(f':display:user2:text "{line2}"')
        self._scpi_write(f':display:screen swipe_user')
                
    ### System-related
    def set_absolute_time(self):
        """ Set the absolute time of the instrument (best accuracy is second). """
        raise NotImplementedError
        
    def beep(self, frequency=1e3, duration=100e-3):
        """ Generate an audible tone. """
        self._scpi_write(f':system:beeper {frequency}, {duration}', sleep=0)
        
    def beep_triad(self, frequency=1e3, duration=100e-3):
        """ Generate an musical triad. """
        self.beep(frequency, duration)
        time.sleep(duration)
        self.beep(frequency * 5.0 / 4.0, duration)
        time.sleep(duration)
        self.beep(frequency * 6.0 / 4.0, duration)
        
    def close(self, restore=False):
        """ Close the connection with the instruments and restore the initial setup if `restore` is asserted. """
        raise NotImplementedError
        
        


    