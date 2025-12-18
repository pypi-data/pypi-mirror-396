Example write a GI.data stream into a .csv file
===============================================
Description
-----------
In this example a GI.data stream will be read and written into a .csv file
   
Requirements
------------
No additional packages are required to run the example

You need also a Gantner Instrument controller connected to your network to fill GI.data or run ``Example_CreateBuffer.py``

Arguments
---------
  - ``-h / --help``: Shows a help message and exits.
  - ``-i / -ID``: The ID of the buffer in GI.bench. Default is ``ff1fbdd4-7b23-11ea-bd6d-005056c00001``.
  - ``-f / --file_name``: The name of the .csv file to write to. Default is ``data.csv``.

Code
----
.. .. note:: The code responsible for parsing the arguments given by the cli has been removed in the documentation for better readability.

.. literalinclude:: ../../src/ginsapy/examples/example_buffer_to_csv.py
    :language: python
