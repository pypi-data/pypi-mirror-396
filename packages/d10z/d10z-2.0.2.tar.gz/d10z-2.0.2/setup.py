from setuptools import setup, find_packages
import os

# Esto lee tu README.md para que aparezca en la descripción de PyPI
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="d10z",
    version="2.0.2",  # Sube la versión a 2.0.2
    author="Jamil Al Thani",
    author_email="tu-email@ejemplo.com", # Reemplaza con el tuyo
    description="D10Z Framework - Manual de la Mecánica del Infinito",
    long_description=long_description,  # Aquí se inserta el README
    long_description_content_type="text/markdown",  # Formato del README
    url="https://github.com/jamilaltha/TTA-Universal-Data",  # URL Principal
    project_urls={
        "Bug Tracker": "https://github.com/jamilaltha/TTA-Universal-Data/issues",
        "Documentation": "https://codexlexd10z.readthedocs.io/",
        "Source Code": "https://github.com/jamilaltha/TTA-Universal-Data",
        "Wiki": "https://github.com/jamilaltha/TTA-Universal-Data/wiki",
    },
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)