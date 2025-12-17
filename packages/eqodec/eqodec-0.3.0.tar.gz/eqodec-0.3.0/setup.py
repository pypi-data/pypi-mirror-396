from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="eqodec",
    version="0.3.0",
    packages=find_packages(),
    install_requires=[
        "torch>=2.0",
        "codecarbon>=3.1.0",
        "numpy"
    ],
    author="Ian Jure Macalisang",
    author_email="ianjuremacalisang2@gmail.com",
    long_description=long_description,
    long_description_content_type="text/markdown",
)