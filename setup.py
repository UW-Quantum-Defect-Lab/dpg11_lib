from setuptools import setup, find_packages

from dpg11_pylib import __version__

# Define preset for extra developement dependencies
extra_test = [
    'pytest>=3',
    'pytest-cov>=1'
]

extra_dev = [
    *extra_test,
]

setup(
    name='dpg11_pylib',
    version=__version__,
    
    url='https://github.com/ethan-r-hansen/dpg11_pylib',
    author='Ethan R. Hansen',
    author_email='hansen.ethan@gmail.com',
    
    py_modules=find_packages(),
    
    install_requires=[
        'numpy<=1.23',
    ],

)