from setuptools import setup

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    # Nombre de la librería en PyPI (distribución)
    name="Pokemon_PJZD",
    version="1.0.0",

    # Paquete que se instala (nombre del import)
    packages=["Pokemon"],

    license="MIT",
    description="Librería para consultar estadísticas de Pokémon por grupo a partir de un CSV.",
    long_description=long_description,
    long_description_content_type="text/markdown",

    author="Pedro Javier Zambudio Decillis",
    author_email="pjzambudio@gmail.com",

    keywords=["curso", "pokemon", "consultas", "stats"],

    install_requires=[
        "pandas",
        "aiohttp",
    ],

    python_requires=">=3.8",

    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
