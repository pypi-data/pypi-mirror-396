#!/usr/bin/env python
"""Setup script."""
from __future__ import print_function

from setuptools import find_packages, setup

install_requires = [r.strip() for r in open('requirements.txt', 'r') if not r.startswith('#')]

setup(
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
    python_requires=">=3.9",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Programming Language :: Python :: 3.14',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
    ],
    entry_points={
        'console_scripts': [
            'malpz = malpz:_entry',
        ]
    },
    keywords='malware, malpz, neuter',
    platforms=['any'],
)
