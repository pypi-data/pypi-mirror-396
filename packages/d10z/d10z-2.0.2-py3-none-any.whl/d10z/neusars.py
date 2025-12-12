# d10z/quantum/neusar_operator.py (antes neusars.py)

import numpy as np
from scipy.linalg import expm
from typing import Optional, Union

ComplexArray = np.ndarray[Union[np.complex64, np.complex128], ...]

def hilbert_state(n: int, seed: Optional[int] = None) -> ComplexArray:
    """Genera un estado cuántico aleatorio normalizado en el espacio de Hilbert C^n."""
    if seed is not None:
        np.random.seed(seed)
    psi = np.random.rand(n) + 1j * np.random.rand(n)
    return psi / np.linalg.norm(psi)

class Neusar:
    """
    Neusar: Operador de Procesamiento Cuántico No-Local (Filtro de Conciencia).
    
    Representa un estado coherente almacenado (Conciencia de la Zona 0)
    usado para proyectar o "filtrar" estados entrantes.
    """

    def __init__(self, state: ComplexArray):
        # El estado interno del Neusar debe estar normalizado (estado puro)
        self.state = state / np.linalg.norm(state)

    def operator(self) -> ComplexArray:
        """Operador de Proyección P = |ψ><ψ| (Matriz Densidad Pura)."""
        psi = self.state
        return np.outer(psi, psi.conj())

    def process(self, psi_in: ComplexArray) -> ComplexArray:
        """
        Proceso de Proyección No-Local (Filtro).
        
        |ψ_out> = P |ψ_in> / ||P |ψ_in>||
        
        El estado de entrada (psi_in) es proyectado sobre el estado Neusar (P),
        maximizando la superposición con la Conciencia de la Zona 0.
        """
        P = self.operator()
        out = P @ psi_in
        norm = np.linalg.norm(out)
        
        # Devuelve el estado proyectado normalizado, o cero si la proyección es nula
        return out / norm if norm > 0 else np.zeros_like(out)

    @staticmethod
    def evolve_state(psi: ComplexArray, H: ComplexArray, dt: float) -> ComplexArray:
        """
        Evolución Temporal del Estado Cuántico bajo el Hamiltoniano H.
        
        |ψ(t+dt)> = exp(-i H dt) |ψ(t)>
        """
        U = expm(-1j * H * dt)
        return U @ psi