from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="core_e2",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[],
    author="Alonzo Forgreting",
    description="Una practica de paquetes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="http://core_e2.com",
)
