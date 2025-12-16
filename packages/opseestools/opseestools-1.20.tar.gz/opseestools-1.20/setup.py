# -*- coding: utf-8 -*-
"""
Created on Sat Mar 16 11:40:26 2024

@author: HOME
"""

from setuptools import setup, find_packages

setup(
    name='opseestools',
    version='1.20',
    author='Orlando Arroyo',
    author_email='orlando.arroyo@uis.edu.co',
    packages=find_packages(),
    description='A collection of OpenSeesPy routines for performing several types of analyses and other tools',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    install_requires=[
        'openseespy>=3.5',  # Requires a version of OpenSeesPy later than 3.5
        'matplotlib',  # Any version of matplotlib
        'numpy',  # Any version of numpy
        'scipy>=1.11',
        'pandas>=2.0',
        'opstool'
    ],
    python_requires='>=3.9', # Adjust based on your compatibility
    url='https://github.com/odarroyo/opseestools',
    license='LICENSE', # If you have a license file
)