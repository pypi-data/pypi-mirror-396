from typing import NamedTuple

import matplotlib.pyplot as plt
from numpy import (
    ndarray,
    array, mod,
    pi
)
from .Components import DataComponent

from .Constants import FIG_WIDTH, FIG_HEIGHT

def display_class_instances_data(class_instances: tuple[DataComponent,...], time_data: ndarray, simulation_keys:tuple[str,...]|None=None):
    """display merged graph for comparision of same class members data"""
    class_type = type(class_instances[0])
    
    # Data storage
    _class_data = {}
    _class_data_units = class_instances[0].get_data_units()

    # Handle Error cases
    for instance in class_instances:
        if(isinstance(instance, class_type) == False):
            other_class= type(instance)
            print(f"{str(instance)} is of type {other_class.__name__} not of type {class_type.__name__}")
            return
        _class_data[str(instance)] = instance.get_data()

    plt.figure(figsize=(FIG_WIDTH, FIG_HEIGHT))

    key_tuple = tuple(_class_data_units)
    
    # Display fixed tuple of data
    if(simulation_keys):
        key_list = []
        for key in simulation_keys:
            if(key in _class_data_units):
                key_list.append(key)
        key_tuple = tuple(key_list)

    max_hf_plots = 1 + (len(key_tuple) >> 1)
    sub_plot_idx = 1

    # Time adjustment
    time_data = time_data[-len(_class_data[str(class_instances[0])][key_tuple[0]]):]

    # Key plot
    for key in key_tuple:
        plt.subplot(max_hf_plots, 2, sub_plot_idx)

        # Component plot
        for instance in _class_data:
            plt.plot(time_data, array(_class_data[instance][key]), label=str(instance))
        plt.xlabel(r"Time $(s)$")
        plt.ylabel(key.capitalize() + _class_data_units[key])
        
        plt.grid()
        plt.legend()
        sub_plot_idx += 1

    plt.suptitle(f"data of {class_type.__name__}s")
    plt.tight_layout()
    plt.show()
        
########## Circulator Dependency Resolved ##########
from .SpecializedComponents.ComponentDriver import CurrentDriver
from .SpecializedComponents.Laser import Laser

class LaserRunnerComponents(NamedTuple):
    """
    LaserRunnerComponents class\n
    A compact class for {'current_driver', 'laser'}.
    """
    current_driver: CurrentDriver
    laser: Laser

def get_time_delay_phase_correction(laser: Laser, time_delay: float):
    """
    Calculate the phase correction for a given time delay.

    Parameters
    ----------
    laser : Laser
        Laser instance for which we want the phase correction
    time_delay : float

    Returns
    -------
    float
        Phase correction in radians in the range [-pi, pi)
    """
    phase_correction:float = mod(laser._free_running_freq * time_delay, 2 * pi) - pi
    return phase_correction