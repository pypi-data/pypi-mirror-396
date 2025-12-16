from setuptools import setup, find_packages

setup(
    name='nkv',
    version='0.1.1',
    description='A simple data file key-value',
    author='Decaptado',
    packages=find_packages(),
    install_requires=['batata-lib==0.1.8']
)