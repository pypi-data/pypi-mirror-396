import d10z
from d10z.physics.gravity import velocity_tta
import matplotlib.pyplot as plt
import numpy as np

# Datos simulados de una galaxia SPARC (ej. NGC 3198)
r_kpc = np.linspace(0.5, 30, 50)
m_baryon = 1e10  # Masas solares

# Predicción TTA (Sin Materia Oscura)
v_pred = [velocity_tta(r, m_baryon) for r in r_kpc]

plt.plot(r_kpc, v_pred, label="Predicción D10Z-TTA")
plt.xlabel("Radio (kpc)")
plt.ylabel("Velocidad (km/s)")
plt.title("Validación de Curva de Rotación Nodal")
plt.legend()
plt.show()