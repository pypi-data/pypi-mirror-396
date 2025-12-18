Example read a GI.data stream
=============================
Description
-----------
In this example a GI.data stream will be read and imported into a Python object (numpy array).

.. figure:: plot_python_variable.jpg
   :scale: 75 %
   :alt: map to buried treasure
   
   Stream from GI.bench
   
The measurement will be plotted into a pyqtgraph time diagram. 

.. figure:: plot_online_values.jpg
   :scale: 75 %
   :alt: map to buried treasure

   Stream plotted in Python with pyqtgraph library
   
Requirements
------------
To run the example you need to install the following packages

    - numpy https://numpy.org/install/
	  data manipulation and scientific calculation
	
    - pyqtgraph http://www.pyqtgraph.org/
	  scientific graphics and GUI Library for Python to generate fast graph

You need also a Gantner Instrument controller connected to your network to fill GI.data or run ``Example_CreateBuffer.py``
 
Arguments
---------
  - ``-h / --help``: Shows a help message and exits.
  - ``-i / -ID``: The ID of the buffer in GI.bench. Default is ``ff1fbdd4-7b23-11ea-bd6d-005056c00001``.
  - ``-p / --plot_data``: Plot data. Default is ``True``.

Code
----
.. literalinclude:: ../../src/ginsapy/examples/example_get_buffer.py