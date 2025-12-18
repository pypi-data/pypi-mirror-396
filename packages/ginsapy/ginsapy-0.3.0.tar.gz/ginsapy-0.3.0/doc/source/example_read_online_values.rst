Example read online values from controller
==========================================
Description
-----------
In this example we read online values from a connected controller channel.

Requirements
------------
No additional packages are required to run the example

You need a Gantner Instrument controller connected to your network.

    - enter the IP of the controller
	
    - the channel indices to be changed

Tip
---
Do not forget to enter the IP of your connected controller.
The method init_online_connection is called to get the total index of channels independently of the configured data buffer.

Arguments
---------
  - ``-h / --help``: Shows a help message and exits.
  - ``-c / --controller_IP``: Controller IP address. Default is ``​``.
  - ``-i / --index_to_read``: Channel indices to read. Default is ``1 2``. Multiple arguments can be given, space seperated ``1 2 3``. Take care enter the index of input/output channels not input.
 
Code
----
.. literalinclude:: ../../src/ginsapy/examples/online_value_communication/example_read_online_values.py