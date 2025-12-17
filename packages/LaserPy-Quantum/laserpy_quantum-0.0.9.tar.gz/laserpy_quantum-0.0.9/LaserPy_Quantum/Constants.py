"""Constants for LaserPy_Quantum"""

from enum import Enum

from importlib import resources
import json

#import rust_optimizer

# fixed Scientific Constants
class UniversalConstants(float, Enum):
    """
    Universal Constants for LaserPy_Quantum
    """

    CHARGE = 1.602 * (1.0e-19)
    """
    single unit of Charge of elctron / proton (magnitude)
    """

    H = 6.626 * (1.0e-34)
    """
    Plank's Constant 
    """

    HBAR = 1.054 * (1.0e-34)
    """
    reduced Plank's Constant 
    """

    C = 2.997 * (1.0e+8)
    """
    Speed of light in vacuum 
    """

    EPSILON_0 = 8.8541878128e-12
    """
    Permittivity of free space
    """

class LaserPyConstants:
    """
    Simulation Constants for LaserPy_Quantum
    """
    _Constants: dict[str, float] = {}

    @classmethod
    def load_from_json(cls, filepath=r'Constants.json'):
        """Loads constants from a JSON file."""
        try:
            with resources.open_text("LaserPy_Quantum", filepath) as f:
                cls._Constants = json.load(f)
        except FileNotFoundError:
            print(f"Error: The file '{filepath}' was not found.")
            exit()

    @classmethod
    def get(cls, key, default=1.0):
        """Retrieves a constant value by key."""
        return cls._Constants.get(key, default)

    @classmethod
    def set(cls, key, value):
        """Allows for runtime modification of a constant."""
        cls._Constants[key] = value

# Load the constants at the runtime
LaserPyConstants.load_from_json()

ERR_TOLERANCE = 1.0e-12

FIG_WIDTH = 12
FIG_HEIGHT = 6

# if __name__ == "__main__":
#     constants = rust_optimizer.UniversalConstant
#     print(constants.SpeedOfLight.value())        # 299792458.0