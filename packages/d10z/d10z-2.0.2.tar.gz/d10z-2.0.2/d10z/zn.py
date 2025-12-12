import numpy as np
from typing import Union, List, Tuple

ComplexArray = np.ndarray[Union[np.complex64, np.complex128], ...]

def amplitude(Z_n: ComplexArray) -> np.ndarray:
    """Retorna la amplitud o magnitud |Zₙ| para cada nodo."""
    return np.abs(Z_n)

def phase(Z_n: ComplexArray) -> np.ndarray:
    """Retorna el argumento o fase arg(Zₙ) en radianes."""
    return np.angle(Z_n)

def normalize(Z_n: ComplexArray) -> ComplexArray:
    """Normaliza las amplitudes a la unidad (magnitud 1) mientras preserva la fase."""
    phases = phase(Z_n)
    return np.exp(1j * phases)

def coherence(Z_n: ComplexArray) -> float:
    """
    Coherencia de Fase Media (κ).
    Mide la unificación de fase del sistema (Kuramoto Order Parameter).
    
    κ = |Σ e^{iθₙ}| / N
    """
    return float(np.abs(np.sum(np.exp(1j * phase(Z_n)))) / len(Z_n))