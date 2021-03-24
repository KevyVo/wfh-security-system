#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import sys
sys.path.insert(0, '../src/files/')

import pyfingerprint

project = u'PyFingerprint'
master_doc = 'PyFingerprint'
author = 'Bastian Raschke <bastian.raschke@posteo.de>'
copyright = '2014-{}, {}'.format(datetime.date.today().year, author)
version = pyfingerprint.__version__
release = version
exclude_patterns = [
    '_build',
    'Thumbs.db',
    '.DS_Store'
]
extensions = [
    'sphinx.ext.autodoc',
]
autoclass_content = "both"
