from __future__ import annotations

from numpy import (
    random,
    ndarray,
    square
)

from ..Components import DataComponent

from ..Constants import LaserPyConstants

from ..Photon import Photon

class SinglePhotonDetector(DataComponent):
    """
    SinglePhotonDetector class
    """

    # Class variables for SinglePhotonDetector
    _Eta = LaserPyConstants.get("Eta")

    def __init__(self, name: str = "default_single_photon_detector"):
        super().__init__(name)

        self.intensity = 0
        """intensity data for SinglePhotonDetector"""

        self.photon_count = 0
        """photon count data for SinglePhotonDetector"""

        # Data storage
        self._simulation_data = {'intensity': []}#, 'photon_count': []}
        self._simulation_data_units = {'intensity': r" $(W/m^2)$"}#, 'photon_count': r" $(counts)$"}

    def display_data(self, time_data: ndarray, simulation_keys: tuple[str, ...] | None = None):
        """SinglePhotonDetector simulate method"""
        # Time adjustment
        time_data = time_data[-len(self._simulation_data['intensity']):]
        super().display_data(time_data, simulation_keys)

    def simulate(self, photon: Photon):
        """SinglePhotonDetector simulate method"""
        #return super().simulate(args)
        
        self.intensity = square(photon.amplitude)

        # TODO: Total photon count
        # incident_photons = random.poisson(self.intensity)
        # self.photon_count = random.binomial(photon.photon_number, self._Eta)

    def input_port(self):
        """SinglePhotonDetector input port method"""
        #return super().input_port()
        kwargs = {'photon': None}
        return kwargs

# class PhaseSensitiveSPD(SinglePhotonDetector):
#     """
#     PhaseSensitiveSPD class
#     """
#     def __init__(self, target_phase: float = 0.0, save_simulation: bool = False, name: str = "default_phase_sensitive_spd"):
#         super().__init__(save_simulation, name)

#         self._target_phase = target_phase
#         """target phase data for PhaseSensitiveSPD"""

#     def simulate(self, photon: Photon):
#         """PhaseSensitiveSPD simulate method"""
#         #return super().simulate(photon)

#         # phase shift due to target phase
#         target_phase_norm = mod(self._target_phase, 2 * pi) - pi
#         phase_shift = exp(-1j * target_phase_norm)

#         # Apply target phase to check interference
#         effective_field = photon * phase_shift
        
#         super().simulate(effective_field)
