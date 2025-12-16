#!/usr/bin/env python3
"""
Setup script for Infiltrator WiFi Red Team Auditing Suite.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read long description from README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# Read version
VERSION = '1.0.1'

# Read requirements
requirements = []
if (this_directory / "requirements.txt").exists():
    requirements = (this_directory / "requirements.txt").read_text().splitlines()
    requirements = [r.strip() for r in requirements if r.strip() and not r.startswith('#')]

setup(
    name='infiltrator-wifi',
    version=VERSION,
    author='LAKSHMIKANTHAN K',
    author_email='letchupkt@example.com',
    description='WiFi Red Team Auditing Suite - Professional penetration testing framework',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/letchupkt/infiltrator',
    project_urls={
        'Bug Reports': 'https://github.com/letchupkt/infiltrator/issues',
        'Source': 'https://github.com/letchupkt/infiltrator',
        'Documentation': 'https://github.com/letchupkt/infiltrator#readme',
    },
    packages=find_packages(exclude=['tests', 'docs']),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'Topic :: Security',
        'Topic :: System :: Networking',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Operating System :: POSIX :: Linux',
        'Environment :: Console',
    ],
    keywords='wifi security penetration-testing red-team wireless hacking ethical-hacking',
    python_requires='>=3.8',
    install_requires=requirements,
    extras_require={
        'dev': ['pytest', 'black', 'flake8', 'mypy'],
        'gps': ['gps3>=0.33.3', 'gpsd-py3>=0.3.0'],
    },
    entry_points={
        'console_scripts': [
            'infiltrator=infiltrator.cli:main',
            'infiltrator-config=infiltrator.config_wizard:main',
        ],
    },
    include_package_data=True,
    package_data={
        'infiltrator': ['data/*.txt', 'data/*.json'],
    },
    zip_safe=False,
    platforms=['Linux'],
)