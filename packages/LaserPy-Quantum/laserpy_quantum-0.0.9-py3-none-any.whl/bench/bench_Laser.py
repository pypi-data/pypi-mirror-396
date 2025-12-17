from .benchmark import benchmark

############################################################################
from LaserPy_Quantum import Clock
from LaserPy_Quantum import Connection, Simulator
from LaserPy_Quantum import StaticWave, ArbitaryWaveGenerator
from LaserPy_Quantum import CurrentDriver
from LaserPy_Quantum import Laser

############################################################################
dt = 1e-12
t_unit = 1e-9
t_final = 100 * t_unit
#sampling_rate = 2 * dt

# Current Constants
I_th = 0.0178
MASTER_BASE_DC = 1.4 * I_th

mBase = StaticWave("mBase", MASTER_BASE_DC)

AWG = ArbitaryWaveGenerator()
AWG.set(mBase)

############################################################################

current_driver1 = CurrentDriver(AWG)
current_driver1.set(mBase)

master_laser = Laser(name= "master_laser")

simulator_clock = Clock(dt)
simulator_clock.set(t_final)

simulator = Simulator(simulator_clock)

simulator.set((
    Connection(simulator_clock, current_driver1),
    Connection(current_driver1, master_laser),
))

simulator.reset(True)

# ------------------------------------------------------------------

@benchmark(number=1, repeat=10)
def benchmarked_simulate():
    """Wrapper function to benchmark the instance's simulate method."""
    simulator.simulation_clock.set(t_final)
    simulator.simulate()
    simulator.reset_data()
    return 

# ------------------------------------------------------------------

print("Starting the benchmarked simulation...")
benchmarked_simulate()
print("Benchmarked simulation complete.")