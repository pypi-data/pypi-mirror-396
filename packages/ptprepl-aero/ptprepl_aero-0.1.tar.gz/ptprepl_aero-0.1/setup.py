#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='ptprepl-aero',
    author='Zaqar Hakobyan',
    version='0.1',
    url='https://github.com/Aero-Organization/ptprepl-aero',
    description='Python REPL build on top of prompt_toolkit.',
    long_description='',
    install_requires = [
        'prompt_toolkit'
    ],
)