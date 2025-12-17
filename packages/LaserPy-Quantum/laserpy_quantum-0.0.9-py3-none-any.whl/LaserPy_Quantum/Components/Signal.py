from typing import Self

from numpy import (
    random,
    mod
)

from .Component import Clock

from ..Constants import ERR_TOLERANCE

from uuid import uuid4

class SignalID:
    def __init__(self, name:str) -> None:
        self.name = name
        self.uid = uuid4()

    def __repr__(self) -> str:
        """SignalID __repr__ method"""
        return f"{self.name} id:{self.uid}"

class NoNoise(SignalID):
    """
    NoNoise class
    """
    def __init__(self, name:str="default_no_noise"):
        super().__init__(name)

    def __call__(self):
        """NoNoise __call__ method to override"""
        return 0

class LangevinNoise(NoNoise):
    """
    LangevinNoise class
    """
    def __init__(self, Mu: int, Std_dev: int, name: str = "default_langevin_noise"):
        super().__init__(name)

        self._Mu = Mu
        self._Std_dev = Std_dev

    def __call__(self):
        """LangevinNoise __call__ method"""
        return random.normal(loc=self._Mu, scale=self._Std_dev)

########################################################
# Wave definitions

class ArbitaryWave(SignalID):
    """
    ArbitaryWave class
    """
    def __init__(self, name:str, 
                t_unit:float= -1, total_spread:float=1.0):
        super().__init__(name)
        self._t_unit = t_unit
        self._signal_spread = 0.5 * total_spread 

    def __call__(self, t: float):
        """ArbitaryWave __call__ method"""
        if(self._t_unit > 0):
            t = mod(t, self._t_unit)
        return self.WaveSignal(t)
    
    def WaveSignal(self, t: float):
        """ArbitaryWave WaveSignal method to override"""
        return 0

class StaticWave(ArbitaryWave):
    """
    StaticWave class
    """
    def __init__(self, name: str, static_val: float):
        super().__init__(name)
        self.static_val = static_val

    def WaveSignal(self, t: float):
        """StaticWave WaveSignal method"""
        #return super().WaveSignal(t)
        return self.static_val

class PulseWave(ArbitaryWave):
    """
    PulseWave class
    """
    def __init__(self, name: str, pulse_low: float, pulse_high: float, 
                t_unit: float, total_spread: float = 1):
        super().__init__(name, t_unit, total_spread)
        self.pulse_low = pulse_low
        self.pulse_high = pulse_high

    def WaveSignal(self, t: float):
        """PulseWave WaveSignal method"""
        #return super().WaveSignal(t)
        if(t > self._t_unit * (0.5 - self._signal_spread) and   
           t < self._t_unit * (0.5 + self._signal_spread)):   
            return self.pulse_high
        return self.pulse_low

class AlternatingPulseWave(ArbitaryWave):
    """
    AlternatingPulseWave class
    """
    def __init__(self, name: str, static_val: float, pulse_val: float,
                t_unit: float, total_spread: float = 1):
        super().__init__(name, t_unit, total_spread)
        self.sign = -1
        self.static_val = static_val
        self.pulse_val = pulse_val

    def WaveSignal(self, t: float):
        """AlternatingPulseWave WaveSignal method"""
        #return super().WaveSignal(t)
        if(t <= ERR_TOLERANCE):
            self.sign *= -1
        if(t > self._t_unit * (0.5 - self._signal_spread) and   
           t < self._t_unit * (0.5 + self._signal_spread)):   
            return self.static_val + self.pulse_val * self.sign
        return self.static_val
    
########################################################

class ArbitaryWaveGenerator:
    """
    ArbitaryWaveGenerator Singleton class
    """
    _SELF = None
    _SINGLETON = False

    def __new__(cls, *arg, **kwargs) -> Self:
        if(cls._SELF is None):
            cls._SELF = super().__new__(cls)
        return cls._SELF

    def __init__(self, name:str="awg_component"):
        # Only one object exists
        if(self._SINGLETON): return None
        self._SINGLETON = True

        self.name = name
        self.signals:dict[str, ArbitaryWave] = {}
        """Signals dictionary for ArbitaryWaves"""

    def set(self, arbitarywaves:ArbitaryWave|tuple[ArbitaryWave,...]):
        """ArbitaryWaveGenerator set method"""
        if(isinstance(arbitarywaves, ArbitaryWave)):
            arbitarywaves = (arbitarywaves,)

        for arbitarywave in arbitarywaves:
            self.signals[arbitarywave.name] = arbitarywave

    def simulate(self, clock:Clock, signal_keys:str|tuple[str,...]) -> float:
        """ArbitaryWaveGenerator simulate method"""
        if(isinstance(signal_keys, str)):
            return self.signals[signal_keys](clock.t)
        else:
            superimposed_signal = 0
            for signal_key in signal_keys:
                superimposed_signal += self.signals[signal_key](clock.t)
            return superimposed_signal