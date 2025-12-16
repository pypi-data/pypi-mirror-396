#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='sborf',
    zip_safe=False,
    include_package_data=True,

    version='0.0.3',

    author="Gabriele Orlando",
    author_email="orlando.gabriele89@gmail.com",

    description="A neural network that predicts and designs alternative DNA encodings for proteins, aiming to fine-tune their expression",
    long_description=long_description,
    long_description_content_type="text/markdown",

    url="https://github.com/grogdrinker/sborf",

    packages=['sborf', 'sborf.src'],
    package_dir={
        'sborf': 'sborf/',
        'sborf.src': 'sborf/src/'
    },

    package_data={
        'sborf': [
            'models/*',
            'models/cerevisiae/*',
            'models/coli/*',
            'models/musculus/*'
        ]
    },

    install_requires=[
        "torch",
        "numpy",
        "scikit-learn"
    ],

    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],

    entry_points={
        "console_scripts": [
            "sborf = sborf.sborf_standalone:main",
        ]
    }
)
