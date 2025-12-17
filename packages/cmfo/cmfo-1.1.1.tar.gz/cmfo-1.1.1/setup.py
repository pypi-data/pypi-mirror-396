import os
from setuptools import setup, find_packages

# Robustly find the README in the root directory
here = os.path.abspath(os.path.dirname(__file__))
root_readme = os.path.join(here, "..", "..", "README.md")

try:
    with open(root_readme, encoding="utf-8") as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = "CMFO: Continuous Modal Fractal Oscillation Engine"

setup(
    name="cmfo",
    version="1.1.1",
    author="Jonathan Montero Viques",
    author_email="jesuslocopor@gmail.com",
    description="Fractal Universal Computation Engine",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/1JONMONTERV/CMFO-COMPUTACION-FRACTAL-",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.9",
    install_requires=[
        "numpy>=1.20",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
