from enum import Enum

class PolarizationBasis(Enum):
    """Polarization representation basis"""
    LINEAR_HV = "HV"        # Horizontal/Vertical
    LINEAR_DA = "DA"        # Diagonal/Anti-diagonal  
    CIRCULAR_RL = "RL"      # Right/Left circular
    ELLIPTICAL = "ellip"    # General elliptical