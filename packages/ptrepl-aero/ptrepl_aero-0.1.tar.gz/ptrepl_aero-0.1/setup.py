#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='ptrepl-aero',
    author='Zaqar Hakobyan',
    version='0.1',
    url='https://github.com/codewithzaqar/ptrepl-aero',
    description='Python REPL build on top of prompt_toolkit.',
    long_description='',
    install_requires = [
        'prompt_toolkit'
    ],
)