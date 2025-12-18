Example write online values with websocket connection
=====================================================
Description
-----------
In this example we write values on a connected controller channel.

Requirements
------------
No additional packages are required to run the example

You need GI.bench running and have at least one variable added to your current project.
Virtual variables for testing can be created with this button:

.. figure:: create_VV.png
   :scale: 100 %
   :alt: map to buried treasure

Tip
---
Do not forget to enter the IP of your connected controller.
The method init_online_connection is called to get the total index of channels independently of the configured data buffer.

Arguments
---------

  - ``-h / --help``: Shows a help message and exits.
  - ``-w / --websocket_url``: URL of websocket. Default is ``127.0.0.1``.
  - ``-: / --port``: Port of websocket. Default is ``8090``.
  - ``-r / --route``: Route of anything connected to websocket. Default is ``​``.
  - ``-u / --username``: Username for websocket. Default is ``​``.
  - ``-p / --password``: Password for websocket. Default is ``​``.
  - ``-t / --timeout``: Timeout for websocket connection initialisation in seconds. Default is ``10``.
  - ``-i / --index_to_read``: Channel indices to read. Default is ``2 3``. Multiple arguments can be given, space seperated ``1 2 3``.
  - ``-v / --value_to_write``: Values to be written. Default is ``5 10``; Multiple arguments can be given, space seperated ``1 2 3``. Must have same number of arguments as ``-i/--index_to_write``.


Code
----
.. literalinclude:: ../../src/ginsapy/examples/example_write_websocket.py