# d10z/tta/sahana_dynamics.py (antes sahana_law.py)
import numpy as np
# from ..core.coherence import sahana_law as _sahana_law

def sahana(Z: np.ndarray, connectivity: np.ndarray, gamma: float = None) -> np.ndarray:
    """
    Ley Sahana (Dinámica de Consenso).
    
    dZ/dt = -γ (Zₙ - Σ_j Cₙⱼ Zⱼ / kₙ)

    Impulsa la fase de cada nodo hacia la fase promedio de sus vecinos,
    maximizando la conectividad nodal (λ₂).
    """
    # if gamma is None:
    #     return _sahana_law(Z, connectivity)
    # return _sahana_law(Z, connectivity, gamma=gamma)
    # Temporal: Asumiendo que _sahana_law calcula el término de la derecha.
    return _sahana_law(Z, connectivity, gamma=gamma)


__all__ = ["sahana"]