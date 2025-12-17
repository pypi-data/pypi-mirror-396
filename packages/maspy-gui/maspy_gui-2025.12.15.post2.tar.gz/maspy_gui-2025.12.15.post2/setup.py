from setuptools import setup, find_packages

VERSION = '2025.12.15-2'
DESCRIPTION = 'Interface for the Visual Representation and Debugging of the MASPY Framework'
LONG_DESCRIPTION = 'Interface for the Visual Representation and Debugging of the MASPY Framework https://github.com/laca-is/MASPY-GUI'

# Setting up
setup(
    name="maspy-gui",
    version=VERSION,
    author="Gabriel Galvan Neres",
    author_email="<neres@alunos.utfpr.edu.br>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(include=['gui', 'gui.*']),
    include_package_data=True,
    package_data={"gui": ["*.qss", "*.svg", "py.typed"]},
    install_requires=['maspy-ml>=2025.11.9','PyQt5'],
    keywords=['python', 'autonomous agents', 'multi-agent system', 'user interface'],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.12",
        "Operating System :: Unix",
        "Operating System :: Microsoft :: Windows",
    ]
)