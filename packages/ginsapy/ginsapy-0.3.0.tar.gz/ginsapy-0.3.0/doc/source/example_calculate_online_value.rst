Example calculate online value on controller
============================================
Description
-----------
In this example we take two values from the channel as input and use them to calculate a new value.
That value is then written on a connected controller channel.

You can execute the example ``Example_ConnectController.py`` to verify that the channel value has changed.

Requirements
------------
To run the example you need to install the following packages

    - numpy https://numpy.org/install/
	  data manipulation and scientific calculation
    
    - scipy https://scipy.org/install/
      advanced scientific calculation

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
  - ``-r / --index_to_read``: Channel indices to read. Default is ``1 2``. Multiple arguments can be given, space seperated ``1 2 3``.
  - ``-w / --index_to_write``: Channl where value is written. Default is ``3``.
  - ``-e / --execute_write_values``: Write values before calculating online value; If this flag is ``False``, -i and -v will have no effect. If this flag is ``True``, :py:func:`write_online_value()` will be called; Default is ``False``
  - ``-i / --index_array``: Channel indices to read. Default is ``1 2``. Multiple arguments can be given, space seperated ``1 2 3``.
  - ``-v / --value_array``: Values to be written. Default is ``1 10``. Multiple arguments can be given, space seperated ``1 2 3``.

Code
----
.. literalinclude:: ../../src/ginsapy/examples/online_value_communication/example_calculate_online_value.py