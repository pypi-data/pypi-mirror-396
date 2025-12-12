import numpy as np
from typing import Iterable, Union, Dict

# ASUMIENDO ESTOS IMPORTS DENTRO DE LA ESTRUCTURA d10z
from ..core.constants import EPSILON_IFI
from ..core.nodal_metrics import amplitude # Usamos la función mejorada de zn.py

ComplexArray = np.ndarray[Union[np.complex64, np.complex128], ...]

def master_equation(f: np.ndarray, v: np.ndarray, Z_n: ComplexArray) -> np.ndarray:
    """
    Ecuación de Acoplamiento F (Master Equation) vectorizada:
    F = f · v · |Zₙ|.
    
    Esto es el término 'driver' que impulsa la fase nodal.
    """
    if not (f.shape == v.shape and f.shape == Z_n.shape):
        raise ValueError("f, v, y Z_n deben tener la misma longitud/forma")
    
    # [MEJORA]: Vectorización directa (esencial para alto rendimiento)
    return f * v * amplitude(Z_n)

def nodal_energy(Z_n: ComplexArray) -> float:
    """
    Energía Emergente almacenada en el campo nodal.
    E = ε_ifi · Σ |Zₙ|² (Vinculada directamente a la escala GM·10⁻⁵¹ a través de EPSILON_IFI)
    """
    return EPSILON_IFI * float(np.sum(amplitude(Z_n) ** 2))

def evolve_step(Z: ComplexArray, connectivity: np.ndarray, F: np.ndarray, dt: float = 0.01, alpha: float = 0.001) -> ComplexArray:
    """
    Paso de evolución Nodal (dZ/dt) con términos Sahana e Isis.
    
    dZ/dt = Sahana(Z) + Isis(Z) + α·F·Z/|Z|
    """
    # Se asume que sahana y isis se importan de los módulos de leyes:
    # from .sahana_dynamics import sahana as sahana_law
    # from .isis_resonance import isis as isis_law
    
    # [NOTA]: La implementación completa depende de la estructura de imports. 
    # Usando el patrón genérico temporal:
    sahana_term = sahana_law(Z, connectivity) 
    isis_term = isis_law(Z)
    
    abs_Z = amplitude(Z)
    # Evitar división por cero. El término α·F·Z/|Z| es la fuerza de conducción.
    driving_force = np.where(abs_Z > 1e-10, alpha * F * Z / abs_Z, 0.0)
    
    return Z + dt * (sahana_term + isis_term + driving_force)