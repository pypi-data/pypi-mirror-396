# d10z/core/constants.py (VERSIÓN REVISADA - Núcleo Único)

import numpy as np
from typing import Dict

# ═══════════════════════════════════════════════════════════════════════════════
# 1. ESCALA GM (FUNDAMENTAL: POINT ZERO)
# ═══════════════════════════════════════════════════════════════════════════════
GM_SCALE = 1e-51          # GM·10⁻⁵¹ (metros) - Longitud fundamental del Point Zero
C_EMERGENT = 2.99792458e8 # Velocidad de la luz emergente (m/s)

# Masa y Tiempo Equivalente GM
GM_MASS = GM_SCALE * (C_EMERGENT**2) / 6.67430e-11 # Masa mínima coherente
GM_TIME = GM_SCALE / C_EMERGENT # Tiempo asociado a la longitud GM·10⁻⁵¹

# ═══════════════════════════════════════════════════════════════════════════════
# 2. INFIFOTÓN (ε_ifi)
# ═══════════════════════════════════════════════════════════════════════════════
EPSILON_IFI = GM_MASS * (C_EMERGENT**2) # Energía mínima cuántica de D10Z (Infifotón)

# Funciones de Utilidad (para consolidar infifoton.py)
def infifoton_energy(n_ifi: int) -> float:
    """Calcula la energía total E = N·ε_ifi."""
    return n_ifi * EPSILON_IFI

def infifoton_count(energy: float) -> int:
    """Calcula el número de Infifotones N = round(E / ε_ifi)."""
    if EPSILON_IFI == 0:
        return 0
    return int(np.round(energy / EPSILON_IFI))

# ═══════════════════════════════════════════════════════════════════════════════
# 3. GEOMETRÍA / COHERENCIA
# ═══════════════════════════════════════════════════════════════════════════════
PHI_IGNITION = 0.99       # Umbral de Coherencia para el Big Start
FLOWER_OF_LIFE_NODES = 19 # Número de nodos primordiales
FILAMENT_THICKNESS = 1e-7 * GM_SCALE
FILAMENT_SEPARATION = 1e-12 * GM_SCALE

# Tabla de Parámetros GM (para el uso de gm1051.py)
GM_TABLE = {
    GM_SCALE: {
        'epsilon_ifi': EPSILON_IFI,
        'mass_equivalent': GM_MASS,
    }
}

def get_gm_parameters(scale: float) -> Dict[str, float]:
    """Busca parámetros en la tabla GM. Necesaria para gm1051.py."""
    return GM_TABLE.get(scale)