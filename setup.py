#!/usr/bin/env python3
import io
import re
from setuptools import setup, find_packages

with io.open("src/ndn/__init__.py", "rt", encoding="utf8") as f:
    version = re.search(r'__version__ = "(.*?)"', f.read()).group(1)

requirements = ['python-ndn>=0.3a1']
setup(
    name='ndn-svs',
    version=version,
    description='The NDN State Vector Sync (SVS) Protocol in Python 3',
    url='https://github.com/justincpresley/ndn-python-svs',
    author='Justin C Presley',
    author_email='justincpresley@gmail.com',
    download_url='https://pypi.python.org/pypi/ndn-svs',
    license='LGPL-2.1 License',
    classifiers=[
        'Development Status :: 4 - Beta',

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'Topic :: Internet',
        'Topic :: System :: Networking',

        'License :: OSI Approved :: GNU Lesser General Public License v2 (LGPLv2)',

        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    keywords='NDN SVS',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=requirements,
    python_requires=">=3.6",
    zip_safe=False)