from LaserPy_Quantum import Clock
from LaserPy_Quantum import Connection, Simulator
from LaserPy_Quantum import (
    StaticWave,
    ArbitaryWaveGenerator
)
from LaserPy_Quantum import CurrentDriver, Laser
from LaserPy_Quantum.SpecializedComponents import SinglePhotonDetector

# Control Constants (all in SI units)
modulation_bits = [0] * 20
dt = 1e-12
t_unit = 1e-9
t_final = t_unit * len(modulation_bits) / 2
sampling_rate = 2

simulator_clock = Clock(dt=dt, sampling_rate= sampling_rate)
simulator_clock.set(t_final= 5 * t_unit)

simulator = Simulator(simulator_clock)

# Current Constants
I_th = 0.0178
MASTER_BASE_DC = 1.4 * I_th

# Steady above lasing current
mBase = StaticWave("mBase", MASTER_BASE_DC)

AWG = ArbitaryWaveGenerator()
AWG.set(mBase)

current_driver = CurrentDriver(AWG)
current_driver.set(mBase)

laser = Laser()
SPD = SinglePhotonDetector()

simulator.set((
    Connection(simulator_clock, current_driver),
    Connection(current_driver, laser),
    Connection(laser, SPD)
))

simulator.reset(True)
simulator.simulate()
time_data = simulator.get_data()

laser.display_data(time_data)
SPD.display_data(time_data)