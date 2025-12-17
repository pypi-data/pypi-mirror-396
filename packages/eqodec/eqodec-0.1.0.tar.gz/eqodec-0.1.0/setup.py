from setuptools import setup, find_packages

setup(
    name="eqodec",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "torch>=2.0",
        "codecarbon>=3.1.0",
        "numpy"
    ],
)