Introduction
============

What is the GInsData API?
-------------------------

The **GInsData API** provides a platform-independent interface to measurement data from
**eGate/pac, Q.gate/pac, Q.station**, and ProcessBuffers of **GI.data (GI.bench)**.

The library ships as:

- ``giutility.dll`` (Windows)
- ``libGInsUtility.so`` (Linux)

It supports both standard interfaces (Profibus, EtherCAT, Modbus, ASCII) and
high-performance binary access via:

- HighSpeedPort (HSP) communication
- UDBF file decoding

Core functionality includes:

- Reading and decoding high-speed measurement data
- Online data access, file transfer, diagnostics
- UDBF decoding
- Endianness detection and conversion
- A full C++ API plus a simplified C-style API (usable from C#, VB, Python, Matlab, …)

.. figure:: ginsdataapi_overview3.jpg
   :scale: 25 %
   :alt: GInsData API overview

   GInsData API overview.

Resources
*********
Examples and libraries are included with GI.bench:

``C:\Users\Public\Documents\Gantner Instruments\GI.bench\api``


What is GInsapy?
----------------

.. warning::

   **Status: Beta / Limited Scope**

   GInsapy covers only **HighSpeedPort (HSP)** and **local GI.bench ProcessBuffers**.
   It is **not a complete Python wrapper** for the full GInsData API, and several
   parts are experimental or not fully tested.
   **GI.cloud is not supported.**

    For REST, WebSocket, or GraphQL access, refer to `Pygidata <https://pypi.org/project/pygidata/>`_.


GInsapy provides Python access to the **C-style eGateHighSpeedPort API**, enabling:

- LAN connections to **Q.station** / **Q.core**
- Access to local GI.bench ProcessBuffers
- Decoding buffered measurement data into Python

Requirements
************

- Python **3.10 – 3.14** (tested: 3.10)
- A working **GI.bench** installation or a **Q.station / Q.core** device
- Access to the GInsData library files (e.g. ``giutility.dll``)

Installation & Setup
--------------------

1. **Create and activate a virtual environment**::

      python -m venv venv
      # Windows
      .\venv\Scripts\activate
      # Linux / macOS
      source venv/bin/activate

2. **Build and install the package** (optional example dependencies included)::

      python startup.py -r

3. **Provide library access**
   Ensure the Python process can locate ``giutility.dll``.
   Default path::

      C:\Users\Public\Documents\Gantner Instruments\GI.bench\api\bin\windows\x64\

4. **Run examples**::

      python src\any_example.py -h

Development Notes
-----------------

- Code checked with **pylint**
- Documentation generated with **Sphinx**::

      .\doc\make.bat html

- Multi-version testing using ``uv`` and ``tox``::

      uv python install 3.10 3.11 3.12 3.13 3.14
      tox -e py310
