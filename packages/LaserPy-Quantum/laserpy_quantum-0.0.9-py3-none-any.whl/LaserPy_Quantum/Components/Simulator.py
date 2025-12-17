import matplotlib.pyplot as plt

from numpy import (
    array
)

from ..Constants import FIG_WIDTH, FIG_HEIGHT

from .Component import Component
from .Component import Clock
from .Component import TimeComponent
from .Component import DataComponent

class Connection(TimeComponent):
    """
    Connection class
    """
    _input_components: tuple[Component,...] | None
    _output_components: tuple[Component,...]

    def __init__(self, input_components:Component|tuple[Component,...]|None, output_components:Component|tuple[Component,...], name:str="default_connection"):
        super().__init__(name)
        if(isinstance(input_components, Component)):
            input_components = (input_components,)
        self._input_components = input_components

        if(isinstance(output_components, Component)):
            output_components = (output_components,)
        self._output_components = output_components

    def reset_data(self):
        """Connection reset_data method"""
        # Output devices reset
        for component in self._output_components:
            component.reset_data()

        # Input devices reset
        if(self._input_components):
            for component in self._input_components:
                component.reset_data()

    def reset(self, save_simulation: bool):
        """Connection reset method"""
        #return super().reset()
        for component in self._output_components:
            component.reset(save_simulation)

        # Input devices reset
        if(self._input_components):
            for component in self._input_components:
                component.reset(save_simulation)

    def simulate(self, clock: Clock):
        """Connection simulate method"""
        #return super().simulate(clock)
        
        # Input-Output device ports
        component_kwargs = []
        for idx, component in enumerate(self._output_components):
            component_kwargs.append(component.input_port())
            if('clock' in component_kwargs[idx]):
                component_kwargs[idx]['clock'] = clock

        # Input devices required
        if(self._input_components):
            for idx in range(len(component_kwargs)):
                for component in self._input_components:
                    component_kwargs[idx] = component.output_port(component_kwargs[idx])

        # Output device simulations
        for idx, component in enumerate(self._output_components):
            component.simulate(**component_kwargs[idx])

            if(component._save_simulation and clock._should_sample()):
                component.store_data()

class Simulator(DataComponent):
    """
    Simulator class
    """
    def __init__(self, simulation_clock:Clock, name:str="default_simulator"):
        super().__init__(name)
        self.simulation_clock:Clock = simulation_clock

        # Data storage
        self._simulation_data: list[float] = []
        self._simulation_data_units = r" $(s)$"

    def store_data(self):
        """Simulator store_data method"""
        #return super().store_data()
        self._simulation_data.append(self.simulation_clock.t)

    def reset_data(self):
        """Simulator reset_data method"""
        #return super().reset_data()
        # Clock reset
        self.simulation_clock.running = True
        self.simulation_clock.t = 0.0

        # Data reset
        self._simulation_data.clear()
        # Propagate the changes
        for connection in self._connections:
            connection.reset_data()

    def display_data(self):
        """Simulator display_data method"""
        #return super().display_data()

        # Handle cases
        if(self._handle_get_data()):
            print(f"{self.name} id:{self.class_id} cannot display data")
            return

        plt.figure(figsize=(FIG_WIDTH, FIG_HEIGHT))

        time_data = array(self._simulation_data)

        plt.plot(time_data, time_data, label="Time")
        plt.xlabel(self._simulation_data_units)
        plt.ylabel(self._simulation_data_units)
        plt.grid()

        plt.legend()
        plt.tight_layout()
        plt.show()

    def get_data(self):
        """Simulator get_data method"""
        #return super().get_data()

        # Handle cases
        if(self._handle_get_data()):
            print(f"{self.name} id:{self.class_id} returning single zero-element np array")
            return array([0.0])
        return array(self._simulation_data)

    def reset(self, save_simulation: bool = False):
        """Simulator reset method"""
        # Propagate the changes
        for connection in self._connections:
            connection.reset(save_simulation)

        return super().reset(save_simulation)

    def set(self, connections:Connection|tuple[Connection,...]):
        """Simulator set method"""
        #return super().set()
        if(isinstance(connections, Connection)):
            connections = (connections,)
        self._connections = connections

    def simulate(self):
        """Simulator simulate method"""
        #return super().simulate(args)
        while(self.simulation_clock.running):
            try:
                for connection in self._connections:
                        connection.simulate(self.simulation_clock)

                if(self._save_simulation and self.simulation_clock._should_sample()):
                    self.store_data()
            except Exception as e:
                # Handle any unexpected exceptions
                print(f"DEBUG:: An unexpected error occurred: {e}")
                return
            self.simulation_clock.update()
        print(f"Simulations Complete: {len(self._simulation_data)} samples")