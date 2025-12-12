import numpy as np
from ..utils.constants import G, ALPHA_NODAL

def velocity_tta(r, m_baryon, r0=5.0):
    """
    Predicción de velocidad orbital TTA.
    Elimina la necesidad de materia oscura mediante Zn.
    """
    # Componente bariónica estándar
    v_sq_bar = (G * m_baryon) / r
    
    # Corrección Nodal D10Z: logaritmo de escala nodal
    v_sq_nodal = (G * m_baryon / r) * ALPHA_NODAL * np.log(r / r0)
    
    return np.sqrt(v_sq_bar + np.maximum(0, v_sq_nodal))