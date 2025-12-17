from __future__ import annotations

from ..Components import Clock
from ..Components import TimeComponent

from ..Components import ArbitaryWave
from ..Components import ArbitaryWaveGenerator

# TODO optimise dt and t_unit into a global config singleton
# class ModulationFunction(ArbitaryWave):
#     """ 
#     ModulationFunction class
#     """
#     def __init__(self, name: str, t_unit: float, dt: float, modulation_bits= []):
#         super().__init__(name, t_unit)
#         self.idx = 0
#         self.modulation_bits = modulation_bits
#         self.modulation_bit = 1
#         self.dt = dt

#     def WaveSignal(self, t):
#         if(t <= self.dt):
#             self.idx = (self.idx + 1) % len(self.modulation_bits)
#         return self.modulation_bits[self.idx] == self.modulation_bit

class CurrentDriver(TimeComponent):
    """ 
    CurrentDriver class
    """
    def __init__(self, AWG:ArbitaryWaveGenerator, name:str="default_current_driver"):
        super().__init__(name)

        self._data: float = 0.0
        """current data for CurrentDriver"""

        self._AWG = AWG
        """ArbitaryWaveGenerator for CurrentDriver"""

        self._modulation_OFF:tuple[str,...] = ()
        """Modulation_OFF ArbitaryWaves Tuple for CurrentDriver"""

        self._modulation_ON:tuple[str,...] = ()
        """Modulation_ON ArbitaryWaves Tuple for CurrentDriver"""

        self._modulation_function = None
        """Modulation_function for CurrentDriver"""

    def set(self, modulation_OFF:ArbitaryWave|tuple[ArbitaryWave,...], modulation_ON:ArbitaryWave|tuple[ArbitaryWave,...]|None=None, modulation_function: ArbitaryWave|None=None):
        """CurrentDriver set method"""
        #return super().set()
        modulation = []
        # For direct instance to tuple
        if(isinstance(modulation_OFF, ArbitaryWave)):
            modulation_OFF = (modulation_OFF,)
        
        # Add signal to AWG
        for arbitarywaves in modulation_OFF:
            if(arbitarywaves.name not in self._AWG.signals):
                print(f"{arbitarywaves.name} not in AWG, Signal skipped.")
                continue
            modulation.append(arbitarywaves.name)

        self._modulation_OFF = tuple(modulation)
        #print(self._modulation_OFF)

        if(modulation_ON):
            modulation = []
            # For direct instance to tuple
            if(isinstance(modulation_ON, ArbitaryWave)):
                modulation_ON = (modulation_ON,)
            
            # Add signal to AWG
            for arbitarywaves in modulation_ON:
                if(arbitarywaves.name not in self._AWG.signals):
                    print(f"{arbitarywaves.name} not in AWG, Signal skipped.")
                    continue
                modulation.append(arbitarywaves.name)

            self._modulation_ON = tuple(modulation)
            #print(self._modulation_ON)

        self._modulation_function = modulation_function

    def simulate(self, clock: Clock):
        """CurrentDriver simulate method"""
        #return super().simulate(clock)
        if(self._modulation_function and self._modulation_function(clock.t)):
            # Modulation function is set and Modulation_ON
            self._data = self._AWG.simulate(clock, self._modulation_ON)
            return self._data
        self._data = self._AWG.simulate(clock, self._modulation_OFF)
        return self._data

    def output_port(self, kwargs: dict = {}):
        """CurrentDriver output port method"""
        #return super().output_port(kwargs)
        kwargs['current'] = self._data
        return kwargs