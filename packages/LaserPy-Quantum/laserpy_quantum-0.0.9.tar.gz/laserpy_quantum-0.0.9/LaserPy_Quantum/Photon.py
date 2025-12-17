from __future__ import annotations

from dataclasses import dataclass, field as data_field

from .QuantumOptics import PolarizationBasis

from numpy import (
    linalg, 
    ndarray, dtype, object_,
    array, angle, abs
)

from .Constants import ERR_TOLERANCE

""" Photon dtype for Photon class"""
Photon_dtype = dtype([
    ('field', complex),
    ('frequency', float),
    ('photon_number', float),
    ('source_phase', float),
    ('polarization', (complex, 2)),
    ('polarization_basis', object_) # For simplicity, store the Python Enum object
])

def default_polarization():
    """:meta private:"""
    return array([1.0 + 0j, 0.0 + 0j], dtype=complex)

@dataclass(slots= True)
class Photon:
    """
    Photon class.
    """

    # Microscopic parameters 
    field: complex
    frequency: float

    # Macroscopic parameters
    photon_number: float = ERR_TOLERANCE
    source_phase: float = ERR_TOLERANCE

    # Polarization qubit components (basis)
    # amplitude for [|X>, |Y>]
    polarization: ndarray = data_field(default_factory= default_polarization)

    # Label of the basis
    polarization_basis: PolarizationBasis = PolarizationBasis.LINEAR_HV

    @classmethod
    def from_photon(cls, other: Photon) -> Photon:
        """Photon classmethod from photon constructor"""
        photon = cls.__new__(cls)
        photon.field = other.field
        photon.frequency = other.frequency
        photon.photon_number = other.photon_number
        photon.source_phase = other.source_phase
        photon.polarization = other.polarization.copy()
        photon.polarization_basis = other.polarization_basis
        return photon

    @property
    def amplitude(self) -> float:
        """amplitude (V/m) of the field"""
        return abs(self.field)

    @property
    def phase(self) -> float:
        """phase (rad) of the field"""
        return float(angle(self.field))

    def normalized_polarization_vector(self) -> ndarray:
        """Return normalized polarization vector"""
        n = linalg.norm(self.polarization)
        return self.polarization / n if n > 0 else self.polarization

    def __repr__(self):
        return (f"Photon(ω={self.frequency:.4e}rad/s, |E|={self.amplitude:.4e}V/m, φ={self.phase:.2f}rad)")

Empty_Photon = Photon(ERR_TOLERANCE + 0j, ERR_TOLERANCE)