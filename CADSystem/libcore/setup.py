from setuptools import setup, find_packages

install_requires = [
    'vtk>=8.1.0',
    'numpy>=1.14.0',
    'pydicom>=1.0.0',
    'pyyaml']

setup(
    name='libcore',
    version='0.1.3',
    packages=find_packages(),
    include_package_data=True,
    package_data={'': ['data/*']},
    install_requires=install_requires)

