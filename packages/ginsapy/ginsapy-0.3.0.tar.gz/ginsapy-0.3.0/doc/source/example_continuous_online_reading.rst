Example continuously read online values from controller
=======================================================
Description
-----------
In this example we read online values from a connected controller channel in an infinite loop.
Read values are stored in a .csv file.

Requirements
------------
No additional packages are required to run the example

You need a Gantner Instrument controller connected to your network.

    - enter the IP of the controller
	
    - the channel indices to be read

Tip
---
Do not forget to enter the IP of your connected controller.
The method init_online_connection is called to get the total index of channels independently of the configured data buffer.

Arguments
---------
  - ``-h / --help``: Shows a help message and exits.
  - ``-c / --controller_IP``: Controller IP address. Default is ``​``.
  - ``-r / --index_to_read``: Channel indices to read. Default is ``1 2``. Multiple arguments can be given, space seperated ``1 2 3``.
  - ``-s / --sample_rate``: Sampling rate in Hz. Default is ``1``.
  - ``-d / --delimiter``: Delimiter for .csv file. Default is ``,``.
  - ``-f / --file_name``: Name of the .csv file to save values to. Default is ``out.csv``. 

Code
----
.. literalinclude:: ../../src/ginsapy/examples/online_value_communication/example_continuous_online_reading.py