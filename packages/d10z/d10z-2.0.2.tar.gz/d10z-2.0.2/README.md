from setuptools import setup, find_packages
import os

# --- Lectura del README.md (Descripción Larga en PyPI) ---
# Esto garantiza que la descripción del proyecto no esté en blanco,
# sino que muestre el contenido completo de tu README.
try:
    with open(os.path.join(os.path.dirname(__file__), 'README.md'), encoding='utf-8') as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = "D10Z Framework: The Nodal Mechanic of Infinity and the Homo Fractalis Manifesto. Visit the project URLs for full documentation."

# --- Configuración del Paquete ---
setup(
    # --- Identificación ---
    name="d10z",
    version="2.0.2",  # ¡CRÍTICO! Versión incrementada para permitir la subida.
    author="Jamil Al Thani",
    author_email="jamil@d10z.org",  # Reemplazar con tu email de contacto oficial
    description="Framework D10Z - Mecánica Nodal del Infinito y el Homo Fractalis Manifesto",
    
    # --- Descripción y Metadatos ---
    long_description=long_description,
    long_description_content_type="text/markdown",
    
    # --- Enlaces de Proyecto (URLs Correctas) ---
    url="https://github.com/jamilaltha/TTA-Universal-Data",  # URL Principal del Repositorio
    project_urls={
        "Bug Tracker (Issues)": "https://github.com/jamilaltha/TTA-Universal-Data/issues",
        "Documentation (ReadTheDocs)": "https://codexlexd10z.readthedocs.io/",
        "Source Code": "https://github.com/jamilaltha/TTA-Universal-Data",
        "Wiki & Manifestos": "https://github.com/jamilaltha/TTA-Universal-Data/wiki",
        "Zenodo DOI (Manifesto)": "https://zenodo.org/record/17595967", # DOI de tu manifiesto
    },
    
    # --- Requisitos y Clasificación ---
    packages=find_packages(),
    install_requires=[
        "numpy>=1.20.0",
        "scipy>=1.7.0",
        "matplotlib>=3.5.0",
        "tqdm>=4.62.3",  # Agregamos tqdm para barras de progreso en simulaciones
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Intended Audience :: Science/Research",
    ],
    python_requires='>=3.6',
    keywords=['cosmology', 'physics', 'nodal', 'tta', 'd10z', 'unification', 'sparc', 'homo fractalis'],
)