from __future__ import annotations

from numpy import (
    ndarray,
    empty, zeros
)

from ..Components.Component import Component
from ..Components import Clock

from .PhotonDetector import SinglePhotonDetector

#from collections import namedtuple

from .SimpleDevices import PhaseSample
from .SimpleDevices import BeamSplitter

from ..Photon import Photon, Empty_Photon, Photon_dtype

from ..utils import display_class_instances_data

# TODO multiport
# Handling multiport SinglePhotonDetector

class AsymmetricMachZehnderInterferometer(Component):
    """
    AsymmetricMachZehnderInterferometer class
    """
    def __init__(self, clock:Clock, time_delay:float, 
                splitting_ratio_ti:float = 0.5, splitting_ratio_tf:float = 0.5,
                name: str = "default_asymmetric_machzehnder_interferometer"):
        super().__init__(name)

        # AMZI parameters
        self._time_delay = time_delay
        self._input_beam_splitter = BeamSplitter(splitting_ratio_ti, name="input_beam_splitter")
        self._output_beam_joiner = BeamSplitter(splitting_ratio_tf, name="output_beam_joiner")

        # Phase controls
        self._short_arm_phase_sample = PhaseSample(name="short_arm_phase_sample")
        self._long_arm_phase_sample = PhaseSample(name="long_arm_phase_sample")

        # Measure ports
        self._SPD0 = SinglePhotonDetector(name="SPD_0")
        self._SPD1 = SinglePhotonDetector(name="SPD_π")

        self._photon: Photon = Empty_Photon
        """photon data for AsymmetricMachZehnderInterferometer"""

        self._photon_port2: Photon = Empty_Photon
        """photon_port2 data for AsymmetricMachZehnderInterferometer"""

        # Delay buffer
        self._buffer_size: int = max(1, int(time_delay / clock.dt))
        self._buffer_idx: int = 0
        self._field_buffer: ndarray = zeros(self._buffer_size, dtype=Photon_dtype)
                
        # Populate the default record
        default_record = empty(1, dtype=Photon_dtype)[0]
        default_record['field'] = Empty_Photon.field
        default_record['frequency'] = Empty_Photon.frequency
        default_record['photon_number'] = Empty_Photon.photon_number
        default_record['source_phase'] = Empty_Photon.source_phase
        default_record['polarization'] = Empty_Photon.polarization
        default_record['polarization_basis'] = Empty_Photon.polarization_basis
        
        # Fill the entire buffer with this stored default record
        self._default_record = default_record
        self._field_buffer[:] = self._default_record

    def _handle_SPD_data(self):
        """AsymmetricMachZehnderInterferometer _handle_SPD_data method"""
        if(not self._save_simulation):
            print(f"{self.name} did not save simulation data")
            return True
        elif(self._SPD0._handle_get_data() or self._SPD1._handle_get_data()):
            print(f"{self.name} cannot get SPD data")
            return True
        return False

    def store_data(self):
        """AsymmetricMachZehnderInterferometer store_data method"""
        self._SPD0.store_data()
        self._SPD1.store_data()

    def reset_data(self):
        """AsymmetricMachZehnderInterferometer reset_data method"""
        #return super().reset_data()
        self._field_buffer[:] = self._default_record

        self._SPD0.reset_data()
        self._SPD1.reset_data()

    def reset(self, save_simulation:bool = False):
        """AsymmetricMachZehnderInterferometer reset method"""
        #return super().reset(args)
        self._save_simulation = save_simulation
        self._SPD0.reset(save_simulation)
        self._SPD1.reset(save_simulation)

    def set_beam_splitters(self, splitting_ratio_ti: float = 0.5, splitting_ratio_tf: float = 0.5):
        """AsymmetricMachZehnderInterferometer set beam splitters method"""
        #return super().set()

        # Beam splitters
        self._input_beam_splitter.set(splitting_ratio_ti)
        self._output_beam_joiner.set(splitting_ratio_tf)


    def set_phases(self, short_arm_phase:  float|None = None, long_arm_phase:  float|None = None, 
                short_arm_phase_interval: float|None = None, long_arm_phase_interval: float|None = None):
        """AsymmetricMachZehnderInterferometer set phases method"""
        if(short_arm_phase):
            self._short_arm_phase_sample.set(short_arm_phase, 
                                        phase_interval= short_arm_phase_interval)
        if(long_arm_phase):
            self._long_arm_phase_sample.set(long_arm_phase, 
                                        phase_interval= long_arm_phase_interval)

    def simulate(self, photon: Photon):
        """AsymmetricMachZehnderInterferometer simulate method"""
        #return super().simulate(clock)

        # input field
        photon_short, photon_long = self._input_beam_splitter.simulate(photon)

        # long arm
        photon_long = self._long_arm_phase_sample.simulate(photon_long)

        # Handle buffer
        outgoing_photon = self._field_buffer[self._buffer_idx].copy()

        # Update buffer
        self._field_buffer[self._buffer_idx]['field'] = photon_long.field
        self._field_buffer[self._buffer_idx]['frequency'] = photon_long.frequency
        self._field_buffer[self._buffer_idx]['photon_number'] = photon_long.photon_number
        self._field_buffer[self._buffer_idx]['source_phase'] = photon_long.source_phase
        self._field_buffer[self._buffer_idx]['polarization'] = photon_long.polarization
        self._field_buffer[self._buffer_idx]['polarization_basis'] = photon_long.polarization_basis
        
        # Stored Photon
        photon_long = Photon(
            field=outgoing_photon['field'].item(),
            frequency=outgoing_photon['frequency'].item(),
            photon_number=outgoing_photon['photon_number'].item(),
            source_phase=outgoing_photon['source_phase'].item(),
            polarization=outgoing_photon['polarization'],            # (complex, 2) should be stored/retrieved intact
            polarization_basis=outgoing_photon['polarization_basis'] # Enum objects should be stored/retrieved intact
        )

        self._buffer_idx = (self._buffer_idx + 1) % self._buffer_size

        # short arm
        photon_short = self._short_arm_phase_sample.simulate(photon_short)

        # Recombine
        self._photon, self._photon_port2 = self._output_beam_joiner.simulate(photon_short, photon_long)

        # Photon Detection
        self._SPD0.simulate(self._photon)
        self._SPD1.simulate(self._photon_port2)

    def input_port(self):
        """AsymmetricMachZehnderInterferometer input port method"""
        #return super().input_port()
        kwargs = {'photon':None}
        return kwargs
    
    def output_port(self, kwargs: dict = {}):
        """AsymmetricMachZehnderInterferometer output port method"""
        #return super().output_port(kwargs)
        kwargs['photon'] = self._photon
        kwargs['photon_port2'] = self._photon_port2
        return kwargs
    
    def display_SPD_data(self, time_data: ndarray, simulation_keys:tuple[str,...]|None=None):
        """AsymmetricMachZehnderInterferometer display_SPD_data method"""        
        
        # Handle cases
        if(self._handle_SPD_data()):
            return

        display_class_instances_data((self._SPD0, self._SPD1), time_data, simulation_keys)

    def get_SPD_data(self):
        """AsymmetricMachZehnderInterferometer get_SPD_data method"""

        # Handle cases
        if(self._handle_SPD_data()):
            return

        # Store SPD data
        _SPD_data = {'SPD0':self._SPD0.get_data(), 'SPD1':self._SPD1.get_data()}
        return _SPD_data