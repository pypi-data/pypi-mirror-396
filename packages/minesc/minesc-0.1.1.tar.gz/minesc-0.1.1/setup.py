from setuptools import setup, find_packages

setup(
    name='minesc',
    version='0.1.1',
    author='Decaptado',
    description='Biblioteca pessoal pra facilitar minha vida',
    url='https://github.com/aaaa560/Mine-Server-Manager-2',
    packages=find_packages(),
    python_requires='>=3.10',
    install_requires=['batata-lib==0.1.8', 'nkv==0.1'],
)