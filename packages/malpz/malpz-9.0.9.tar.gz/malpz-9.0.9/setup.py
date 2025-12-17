#!/usr/bin/env python
"""Setup script."""
from __future__ import print_function

from setuptools import find_packages, setup

install_requires = [r.strip() for r in open('requirements.txt', 'r') if not r.startswith('#')]

setup(
    python_requires='>=3.10',
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    packages=find_packages('.', exclude=['test', 'tests']),
    include_package_data=True,
    install_requires=install_requires,
    name='malpz',
    author='Azul',
    author_email='azul@asd.gov.au',
    description='The MALPZ (Malware Pickled Zip) format describes a method '
    'of neutering malware while providing a simple, extensible '
    'mechanism for capturing metadata',
    entry_points={
        'console_scripts': [
            'malpz = malpz:_entry',
        ]
    },
    keywords='malware, malpz, neuter',
    platforms=['any'],
)
