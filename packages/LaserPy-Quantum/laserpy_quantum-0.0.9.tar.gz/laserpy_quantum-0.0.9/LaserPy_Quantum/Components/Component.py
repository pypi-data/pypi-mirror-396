from __future__ import annotations

import matplotlib.pyplot as plt

from numpy import (
    ndarray,
    array, zeros
)

from ..Constants import FIG_WIDTH, FIG_HEIGHT

class CLASSID:
    """
    This is a private class.
    
    This class manages its child classes' ids and stores references.

    Attributes
    ----------
    class_id : int
        Id of the child class, based on that particular classes' instance sequence
    """
    ######  Special Component Registry  #######
    _Component_registry = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._instances: list[Component] = []
        cls._Component_registry[cls.__name__] = cls._instances

    def __init__(self):
        ## Added class_id
        self.class_id = len(self._instances)
        self.__class__._instances.append(self) # type: ignore

    # @classmethod
    # def get_all_Component_registry(cls):
    #     """get_all_Component_registry method"""
    #     return dict(CLASSID._Component_registry)
    ######  ##########################  #######

class Component(CLASSID):
    """
    Represents the base component class.

    This class manages name and simulation boolean.

    It provides methods which are to be overriden by its child classes.

    Parameters
    ----------
    name : str = `"default_component"`
        Name of the component

    Attributes
    ----------
    name : str
        Name of the component
    _save_simulation: bool = `False`
        Boolean for storing simulation data of the component
    """
    def __init__(self, name:str="default_component"):
        super().__init__()
        self.name = name
        """Component name data"""

        self._save_simulation: bool = False
        """Component save simulation data"""

    def __repr__(self) -> str:
        """
        Component __repr__ method (to override)

        Returns
        -------
        str
            Component: {self.name} id:{self.class_id}
        """
        return f"Component: {self.name} id:{self.class_id}"

    def store_data(self):
        """
        Component store_data method (to override)

        Empty method
        ------------
        """
        pass

    def reset_data(self):
        """
        Component reset_data method (to override)
        
        Empty method
        ------------
        """
        pass

    def reset(self, args=None):
        """
        Component reset method (to override)

        Parameters
        ----------
        args : any = `None`
            
        Empty method
        ------------
        """
        pass

    def set(self):
        """
        Component set method (to override)

        Empty method
        ------------
        """
        pass

    def simulate(self, args=None):
        """
        Component simulate method (to override)

        Parameters
        ----------
        args : any = `None`
            
        Empty method
        ------------
        """
        pass

    def input_port(self):
        """
        Component input port method (to override)

        Returns
        -------
        kwargs : dict = `{}`
            Empty dictionary as no requirements for simulate()
        """  
        kwargs = {}
        return kwargs

    def output_port(self, kwargs:dict={}):
        """
        Component output port method (to override)

        Parameters
        ----------
        kwargs : dict = `{}`

        Returns
        -------
        kwargs : dict
            Unmodified dictionary as no data to send
        """ 
        return kwargs

class Clock(Component):
    """
    Represents the clock class.

    This class manages the time counter and all operations on it.

    Parameters
    ----------
    dt: float
        Time step variable for the simulation
    sampling_rate: int = `1`
        Integral postive multiple of **dt**, simulation data are stored on these time steps
    name : str = `"default_clock"`
        Name of the component
        
    Attributes
    ----------
    dt: float
        Time step variable for the simulation
    _sampling_rate: float
        Integral postive multiple of **dt**, simulation data are stored on these time steps
    t : float = `0.0`
        Time counter variable for simulation
    _t_sample : float = `0.0`
        Helper for sampling rate
    running : bool = `True`
        Clock status for time updates
    _t_final : float = `0.0`
        Time at which to stop simulation and set **running** to `False`
    """
    def __init__(self, dt:float, sampling_rate:int = -1, name:str="default_clock"):
        super().__init__(name)
        self.dt = dt
        """Clock Delta time data"""

        self._sampling_rate = dt * (sampling_rate if(sampling_rate > 0) else 1)
        """Clock sampling rate data"""

        self.t = 0.0
        """Clock time data"""

        self._t_sample = 0.0
        """Clock sample time data"""

        self.running = True
        """Clock running state data"""

        self._t_final = 0.0
        """Clock final time data"""

    def set(self, t_final:float, t:float|None=None):
        """
        Clock set method

        Sets **t_final** and **t**.
        Also sets **running** to `True`.
        
        Parameters
        ----------
        t_final : float
        t : float = `None`
        """
        #return super().set()
        self._t_final = t_final
        if(t): 
            self.t = t
            self._t_sample = 0.0
        self.running = True

    def update(self):
        """
        Clock update method

        Checks if **t** exceeded **_t_final**, then sets **running** to `False` and returns.
        Else it updates both **t** and **_t_sample** by one time step, ie **dt**.
        If **_t_sample** exceeds **_sampling_rate** then sets **_t_sample** to `0.0`
        """
        #return super().update()
        if(self.t >= self._t_final):
            self.running = False
            return
        self.t += self.dt
        self._t_sample += self.dt
        if(self._t_sample >= self._sampling_rate): self._t_sample = 0.0

    def _should_sample(self) -> bool:
        """
        Clock _should_sample method
        
        Returns
        -------
        bool
            Returns `True` only when **_t_sample** is `0.0`
        """
        return (self._t_sample == 0.0)

    def output_port(self, kwargs: dict = {}):
        """
        Clock output port method

        Parameters
        ----------
        kwargs : dict = `{}`

        Returns
        -------
        kwargs : dict
            Returns dict with `'clock':self` data
        """  
        #return super().output_port(kwargs)
        kwargs['clock'] = self
        return kwargs

class TimeComponent(Component):
    """
    Represents the base timecomponent class.

    This class is the base class for all components which are time dependent on clock data.

    It provides methods for simulate() and input_port() based on clock data.

    Parameters
    ----------
    name : str = `"default_time_component"`
        Name of the component
        
    Attributes
    ----------
    _data: any = `0`
        A container for specific data according to child classes
    """
    def __init__(self, name:str="default_time_component"):
        super().__init__(name)
        self._data = 0
        """data for TimeComponent"""

    def simulate(self, clock:Clock):
        """
        TimeComponent simulate method (to override)

        Parameters
        ----------
        clock : **Clock**
            
        Empty method
        ------------
        """
        #return super().simulate(args)
        pass

    def input_port(self):
        """
        TimeComponent input port method (to override)

        Returns
        -------
        kwargs : dict
            Returns dict with `'clock':None` data as requirements for simulate()
        """  
        #return super().input_port()
        kwargs = {'clock':None}
        return kwargs

class DataComponent(Component):
    """
    Represents the base datacomponent class.

    This class manages simulation data, and their corresponding data units.

    It provides methods for data handling like get, display, store.

    Parameters
    ----------
    name : str = `"default_data_component"`
        Name of the component
        
    Attributes
    ----------
    _simulation_data: dict = `{}`
        A dict storing keys and it stores values for those keys, at each sampling time step
    _simulation_data_units: dict = `{}`
        A dict storing units corresponding to the keys
    """
    def __init__(self, name:str="default_data_component"):
        super().__init__(name)
        self._simulation_data = {}
        """DataComponent simulation data"""

        self._simulation_data_units = {}
        """DataComponent simulation data units"""

    def _handle_display_data(self, time_data: ndarray):
        """
        DataComponent _handle_display_data method

        Checks if data can be displayed based on **_handle_get_data()**.

        Parameters
        ----------
        time_data: ndarray
            A numpy array containing sequential time data
        
        Returns
        -------
        bool
            Returns `True` when data cannot be displayed
        """
        if(self._handle_get_data()):
            return True
        elif(time_data is None):
            print(f"{self.name} id:{self.class_id} got None for time_data")
            return True
        else:
            for key in self._simulation_data:
                if(len(time_data) != len(self._simulation_data[key])):
                    print(f"{self.name} id:{self.class_id} {key} has {len(self._simulation_data[key])} while time_data has {len(time_data)}")
                    return True
        return False

    def _handle_get_data(self):
        """
        DataComponent _handle_get_data method

        Handles data checks and key matches internally.
        
        Returns
        -------
        bool
            Returns `True` when data is not saved or empty due to errors
        """
        if(not self._save_simulation):
            print(f"{self.name} id:{self.class_id} did not save simulation data")
            return True
        elif(len(self._simulation_data) == 0):
            print(f"{self.name} id:{self.class_id} simulation data is empty")
            return True
        return False

    def store_data(self):
        """
        DataComponent store_data method

        Stores data for each key based on matching name of variable and key.
        """
        for key in self._simulation_data:
            self._simulation_data[key].append(getattr(self, key))

    def reset_data(self):
        """
        DataComponent reset_data method

        Clears all key data.
        """
        for key in self._simulation_data:
            self._simulation_data[key].clear()

    def display_data(self, time_data: ndarray, simulation_keys:tuple[str,...]|None=None):
        """
        DataComponent display_data method
        
        Plots stored data of the component based on **time_data** and **simulation_keys**.

        Parameters
        ----------
        time_data: ndarray
            A numpy array containing sequential time data

        simulation_keys: tuple[str, ...] = `None`
            An optional tuple of strings containing keys for which to plot data, Default all defined keys
        """        
        
        # Handle cases
        if(self._handle_display_data(time_data)):
            print(f"{self.name}id:{self.class_id} cannot display data")
            return

        plt.figure(figsize=(FIG_WIDTH, FIG_HEIGHT))

        key_tuple = tuple(self._simulation_data_units)
        
        # Display fixed tuple of data
        if(simulation_keys):
            key_list = []
            for key in simulation_keys:
                if(key in self._simulation_data_units):
                    key_list.append(key)
            key_tuple = tuple(key_list)

        max_hf_plots = 1 + (len(key_tuple) >> 1)
        sub_plot_idx = 1
        for key in key_tuple:
            plt.subplot(max_hf_plots, 2, sub_plot_idx)
            plt.plot(time_data, array(self._simulation_data[key]), label=f"{key}")

            plt.xlabel(r"Time $(s)$")
            plt.ylabel(key.capitalize() + self._simulation_data_units[key])
            
            plt.grid()
            plt.legend()
            sub_plot_idx += 1

        plt.suptitle(f"{self.name} {self.__class__.__name__}_id:{self.class_id}")
        plt.tight_layout()
        plt.show()

    def get_data(self):
        """DataComponent get_data method"""

        # Handle cases
        val = self._handle_get_data()
        
        data_dict: dict[str, ndarray] = {}
        for key in self._simulation_data:
            data_dict[key] = zeros(1) if(val) else array(self._simulation_data[key])
        return data_dict

    def get_data_units(self):
        """
        DataComponent get_data_units method
        
        Returns
        -------
        dict
            A new dict copy of all the `keys:units`
        """        
        return dict(self._simulation_data_units)

    def reset(self, save_simulation:bool=False):
        """DataComponent reset method to override"""
        #return super().reset()
        self._save_simulation = save_simulation

    def output_port(self, kwargs:dict={}):
        """DataComponent output port method to override"""
        #return super().output_port(kwargs)
        for key in kwargs:
            if hasattr(self, key):
                kwargs[key] = getattr(self, key)
        return kwargs

class PhysicalComponent(DataComponent, TimeComponent):
    """
    PhysicalComponent class
    """
    def __init__(self, name:str="default_physical_component"):
        super().__init__(name)  

        self._data: float = 0.0
        """PhysicalComponent _data value to override"""

        self._simulation_data = {'_data':[]}
        self._simulation_data_units = {'_data':r" $(u)$"}

    def simulate(self, clock: Clock, _data: float|None=None):
        """PhysicalComponent simulate method to override"""
        #return super().simulate(args)
        if(_data):
            self._data += 1
        else:
            self._data = 100

    def input_port(self):
        """PhysicalComponent input port method to override"""
        kwargs = {'clock':None, '_data': None}
        return kwargs