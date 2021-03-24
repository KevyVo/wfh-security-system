#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

import sys
sys.path.insert(0, './files/')

import pyfingerprint

setup(
    name            = 'pyfingerprint',
    version         = pyfingerprint.__version__,
    description     = 'Python written library for using ZhianTec fingerprint sensors.',
    author          = 'Bastian Raschke',
    author_email    = 'bastian.raschke@posteo.de',
    url             = 'https://sicherheitskritisch.de',
    license         = 'D-FSL',
    package_dir     = {'': 'files'},
    packages        = ['pyfingerprint'],
)
