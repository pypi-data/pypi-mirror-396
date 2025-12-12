# d10z/tta/isis_resonance.py (antes isis_law.py)
import numpy as np
# from ..core.coherence import isis_law as _isis_law

def isis(Z: np.ndarray, sigma: float = None) -> np.ndarray:
    """
    Ley Isis (Resonancia Armónica).

    f_LI(φ₁, φ₂) = cos(φ₁ - φ₂) · exp(-|D₁ - D₂|² / 2σ²)
    
    Aplica una fuerza de resonancia basada en la correlación fase-velocidad.
    Es el término de "tensión" que previene la disipación total del campo nodal.
    """
    # if sigma is None:
    #     return _isis_law(Z)
    # return _isis_law(Z, sigma=sigma)
    # Temporal: Asumiendo que _isis_law calcula el término de la derecha.
    return _isis_law(Z, sigma=sigma)


__all__ = ["isis"]