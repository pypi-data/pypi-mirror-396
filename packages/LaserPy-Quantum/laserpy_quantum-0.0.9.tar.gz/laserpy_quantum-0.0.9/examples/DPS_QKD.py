from LaserPy_Quantum import Clock
from LaserPy_Quantum import Connection, Simulator
from LaserPy_Quantum import (
    ArbitaryWave,
    StaticWave, PulseWave, AlternatingPulseWave,
    ArbitaryWaveGenerator
)
from LaserPy_Quantum import CurrentDriver
from LaserPy_Quantum import Laser

from LaserPy_Quantum import VariableOpticalAttenuator

from LaserPy_Quantum import AsymmetricMachZehnderInterferometer
from LaserPy_Quantum import (
    display_class_instances_data, 
    get_time_delay_phase_correction
)

# Control Constants (all in SI units)
modulation_bits = [0] * 20
dt = 1e-12
t_unit = 1e-9
t_final = t_unit * len(modulation_bits) / 2
sampling_rate = 2

RESET_MODE = True

# Current Constants
I_th = 0.0178
MASTER_BASE_DC = 1.4 * I_th

# Time duration are in fration of t_unit
MASTER_AC_DURATION = 0.4
MASTER_AC = 0.3 * I_th

# Time duration are in fration of t_unit
SLAVE_DC_DURATION = 0.6
SLAVE_DC = 0.85 * I_th

SLAVE_PULSE = 1.15 * I_th

# Steady above lasing current
mBase = StaticWave("mBase", MASTER_BASE_DC)

# Modulation current
mModulation = AlternatingPulseWave("mModulation", 0, MASTER_AC, t_unit, total_spread=MASTER_AC_DURATION)

# Gain Switch mode for slave laser
sBase = PulseWave("sBase", SLAVE_PULSE, SLAVE_DC, t_unit, total_spread=SLAVE_DC_DURATION) 

AWG = ArbitaryWaveGenerator()
AWG.set((mBase, mModulation))
AWG.set(sBase)

class ModulationFunction(ArbitaryWave):
    def __init__(self, signal_name: str, t_unit: float, total_spread: float = 1):
        super().__init__(signal_name, t_unit, total_spread)
        self.idx = 0
        self.modulation_bit = 1

    def WaveSignal(self, t):
        if(t <= dt):
            self.idx = (self.idx + 1) % len(modulation_bits)
        return modulation_bits[self.idx] == self.modulation_bit

mod_func = ModulationFunction("modulation_function", t_unit)

############################################################################

current_driver1 = CurrentDriver(AWG)
current_driver1.set(mBase)

current_driver2 = CurrentDriver(AWG)
current_driver2.set(sBase)

master_laser = Laser(name= "master_laser")
slave_laser = Laser(name= "slave_laser")

simulator_clock = Clock(dt, sampling_rate)
simulator_clock.set(t_final)

simulator = Simulator(simulator_clock)

VOA = VariableOpticalAttenuator(5)
AMZI = AsymmetricMachZehnderInterferometer(simulator_clock, time_delay= t_unit)

simulator.set((
    Connection(simulator_clock, (current_driver1, current_driver2)),
    Connection(current_driver1, master_laser),
    Connection(current_driver2, slave_laser),
))

simulator.reset(True)

simulator.simulate()
time_data = simulator.get_data()

#display_class_instances_data((master_laser, slave_laser), time_data)

#exit(code= 0)
############################################################################
if(RESET_MODE):
    simulator.reset_data()
else:
    t_final = 2 * t_final
    simulator_clock.set(t_final)

slave_laser.set_slave_Laser()

simulator.set((
    Connection(simulator_clock, (current_driver1, current_driver2)),
    Connection(current_driver1, master_laser),
    Connection(master_laser, VOA),
    Connection((current_driver2, VOA), slave_laser),
))

simulator.reset(True)

simulator.simulate()
time_data = simulator.get_data()

#display_class_instances_data((master_laser, slave_laser), time_data)

#exit(code= 0)
############################################################################

modulation_bits = [0,0] + [1,0,1,0,1,1,1,0,0,1]

if(RESET_MODE):
    simulator.reset_data()
    t_final = t_unit * (len(modulation_bits) - 1)
    simulator_clock.set(t_final)
else:
    t_final += t_unit * (len(modulation_bits) - 1)
    simulator_clock.set(t_final)

current_driver1.set(mBase, (mBase, mModulation), mod_func)

simulator.set((
    Connection(simulator_clock, (current_driver1, current_driver2)),
    Connection(current_driver1, master_laser),
    Connection(master_laser, VOA),
    Connection((current_driver2, VOA), slave_laser),
    Connection(slave_laser, AMZI)
))

simulator.reset(True)

AMZI.set_phases(short_arm_phase= get_time_delay_phase_correction(slave_laser, time_delay= t_unit))

simulator.simulate()
time_data = simulator.get_data()

display_class_instances_data((master_laser, slave_laser), time_data)
AMZI.display_SPD_data(time_data)