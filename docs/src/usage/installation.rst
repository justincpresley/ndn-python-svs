Installation
============

Dependencies / Pre-Installs
---------------------------

* Install / Setup NFD_. This documentation assumes basic use of NFD.

Instruction for use
-------------------

Install the latest release with pip_:

.. code-block:: bash

    $ /usr/bin/pip3 install ndn-svs

Optionally, you can install the latest development version from source_:
(note: also add root folder of this github repo to PYTHONPATH environment variable)

.. code-block:: bash

    $ git clone https://github.com/justincpresley/ndn-python-svs.git
    $ cd ndn-python-svs && /usr/bin/pip3 install -e .


Instruction for developers
--------------------------

Setup virtual environment with editable installation:

.. code-block:: bash

    $ python3 -m venv venv
    $ . venv/bin/activate
    $ pip3 install -e .

Run all tests:

.. code-block:: bash

    $ pip3 install pytest
    $ pytest

Compile the documentation with Sphinx:

.. code-block:: bash

    $ cd docs && pip3 install -r requirements.txt
    $ make html
    $ open _build/html/index.html

.. _NFD: https://named-data.net/doc/NFD/current/INSTALL.html
.. _source: https://github.com/justincpresley/ndn-python-svs
.. _pip: https://pypi.python.org/pypi/ndn-svs