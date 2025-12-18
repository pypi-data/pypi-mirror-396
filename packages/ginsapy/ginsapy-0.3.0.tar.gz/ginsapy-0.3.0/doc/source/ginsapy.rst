GInsapy
=======

Restriction
-----------

The GInsapy was developed by Gantner Instruments to illustrate the GInsData API with Python.
Despite our efforts, this software package is delivered "AS IS" without warranty.
Please contact your Gantner Instruments support team for any suggestions.

Package structure
-----------------

.. code-block:: python

	ginsapy # Project directory
	--doc # Sphinx documentation
	  --source # Documentation source directory
	--src
	  various_examples.py
	  --online_value_communication # More examples
	  --giutility # API modules
	    --buffer # Read/write buffer 
	    --connect 
	  eGateHighSpeedPort.h # C-header file used by giutility libraries
	LICENSE # MIT License disclaimer
	README.md
	requirements.txt # List of required Python packages
	setup.py # file to generate a distribution package		
	startup.py # file to automate installation process

Gantner instruments dll 
-----------------------
A version of the Gantner instruments 32/64-bit DLL (giutility.dll) is **NOT** included in the package. The giutility.dll can be found in the installation folder of GI.bench.

License
-------
This software package is delivered under MIT license.

License disclaimer
------------------

Copyright (c) 2020 Gantner Instruments

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

