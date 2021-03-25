#    @Author: Justin C Presley
#    @Author-Email: justincpresley@gmail.com
#    @Project: NDN State Vector Sync Protocol
#    @Source-Code: https://github.com/justincpresley/ndn-python-svs
#    @Pip-Library: https://pypi.org/project/ndn-svs/

#!/usr/bin/env python3
import io
import re
from setuptools import setup, find_packages

with io.open("src/ndn/__init__.py", "rt", encoding="utf8") as f:
    version = re.search(r'__version__ = "(.*?)"', f.read()).group(1)

with io.open("README.md", "rt", encoding="utf8") as f:
    long_description = f.read()

requirements = ['python-ndn>=0.3a1','ndn-python-repo>=0.2a5','pytest>=6.2.2','pycryptodomex>=3.10.1']
setup(
    name='ndn-svs',
    version=version,
    description='The NDN State Vector Sync (SVS) Protocol in Python 3',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/justincpresley/ndn-python-svs',
    author='Justin C Presley',
    author_email='justincpresley@gmail.com',
    maintainer='Justin C Presley',
    maintainer_email='justincpresley@gmail.com',
    download_url='https://pypi.python.org/pypi/ndn-svs',
    project_urls={
        "Bug Tracker": "https://github.com/justincpresley/ndn-python-svs/issues",
        "Source Code": "https://github.com/justincpresley/ndn-python-svs",
    },
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