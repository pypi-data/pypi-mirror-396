Example write online values to controller
=========================================
Description
-----------
In this example we write online values on a connected controller channel.

You can execute the example ``Example_ConnectController.py`` to verify that the channel value has changed.

Requirements
------------
To run the example you need to install the following packages

    - numpy https://numpy.org/install/
	  data manipulation and scientific calculation

You also need a Gantner Instrument controller connected to your network.

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
  - ``-i / --index_to_write``: Channel indices to read. Default is ``1 2``. Multiple arguments can be given, space seperated ``1 2 3``.
  - ``-v / --value_to_write``: Values to be written. Default is ``0 10``; Multiple arguments can be given, space seperated ``1 2 3``. Must have same number of arguments as ``-i/--index_to_write``.

Code
----
.. literalinclude:: ../../src/ginsapy/examples/online_value_communication/example_write_online_values.py