# d10z/physics/omdi_invariant.py (antes omdi.py)

from typing import Iterable, Union
import numpy as np

FloatArray = np.ndarray[Union[np.float32, np.float64], ...]

def omdi_invariant(gradients: Iterable[FloatArray], weights: Iterable[float] = None) -> float:
    """
    Calcula el Invariante Omni-Dimensional Ω_DI.

    Ω_DI = Σ_d w_d · ||∇Φ_d||²
    
    Mide la magnitud total del cambio de coherencia a través de todas las
    dimensiones (d), con un peso (w_d) por cada capa.
    """
    grads = list(gradients)
    if weights is None:
        weights = [1.0] * len(grads)
    weights = np.asarray(list(weights))
    if len(weights) != len(grads):
        raise ValueError("Los pesos deben coincidir con el número de componentes de gradiente.")
        
    norm_terms = [wd * float(np.sum(gd ** 2)) for wd, gd in zip(weights, grads)]
    return float(np.sum(norm_terms))


def omdi_metric(gradients: Iterable[FloatArray], coherence: float) -> float:
    """
    Métrica OmDi Normalizada (M_omdi).

    M_omdi = Ω_DI · Φ̄ / (1 + Ω_DI)
    
    Esta métrica es CRÍTICA para el Homo Fractalis:
    Asegura que la complejidad del gradiente (Ω_DI) se pondera por la coherencia
    global (Φ̄), previniendo la acumulación de un gradiente fragmentado.
    """
    omega = omdi_invariant(gradients)
    # El denominador (1.0 + omega) previene la explosión de valores y asegura 
    # que M_omdi se sature cerca de la coherencia máxima.
    return omega * coherence / (1.0 + omega)


__all__ = ["omdi_invariant", "omdi_metric"]