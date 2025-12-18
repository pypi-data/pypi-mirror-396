""" The process of writing data is the same as in example_write_online
    the type of connection is the only difference
    Note: You can only write to Input or Input/Output Variables!"""

import json
import time
import argparse
import ginsapy.giutility.connect.highspeedport_client as highspeedport_client

# Class to clean up output of -h in cli
from ginsapy.examples.CustomHelpFormatter import CustomHelpFormatter


# *****************************************************
# Input parameters
# *****************************************************

parser = argparse.ArgumentParser(
    description="Write a value to one or more variables over an IP-Address",
    formatter_class=CustomHelpFormatter,
    add_help=False,
)

parser.add_argument(
    "-h",
    "--help",
    action="help",
    default=argparse.SUPPRESS,
    help="Show this help message and exit; All arguments are optional; \
                    Strings do not need to be quoted",
)
parser.add_argument(
    "-w",
    "--websocket_url",
    type=str,
    help="URL of websocket; Default is 127.0.0.1",
    required=False,
    default="127.0.0.1",
    metavar="",
)
parser.add_argument(
    "-:",
    "--port",
    type=int,
    help="Port of websocket; Default is 8090",
    required=False,
    default=8090,
    metavar="",
)
parser.add_argument(
    "-r",
    "--route",
    type=str,
    help="Route of anything connected to websocket; Default is an empty string",
    required=False,
    default="",
    metavar="",
)
parser.add_argument(
    "-u",
    "--username",
    type=str,
    help="Username for websocket; Default is an empty string",
    required=False,
    default="",
    metavar="",
)
parser.add_argument(
    "-p",
    "--password",
    type=str,
    help="Password for websocket; Default is an empty string",
    required=False,
    default="",
    metavar="",
)
parser.add_argument(
    "-t",
    "--timeout",
    type=int,
    help="Timeout for websocket connection initialisation in seconds; \
                        Default is 10 seconds",
    required=False,
    default=10,
    metavar="",
)
parser.add_argument(
    "-i",
    "--index_to_write",
    nargs="+",
    type=int,
    help="Channel indices to write; Default is 2 3; \
                        Multiple arguments can be given, space seperated (1 2 3)",
    required=False,
    default=[2, 3],
    metavar="",
)
parser.add_argument(
    "-v",
    "--value_to_write",
    nargs="+",
    type=float,
    help="Values to be written; Default is 5 10; \
                        Multiple arguments can be given, space seperated (1 2 3); \
                        Must have same number of arguments as -i/--index_to_write",
    required=False,
    default=[5, 10],
    metavar="",
)

args = parser.parse_args()

url = args.websocket_url
port = args.port
route = args.route
username = args.username
password = args.password
timeout_sec = args.timeout
index_to_write = args.index_to_write
value_to_write = args.value_to_write

add_config = {}
add_config["IntervalMs"] = 1000
add_config = json.dumps(add_config)

conn = highspeedport_client.HighSpeedPortClient()

# When handling ONLINE values we need to initWebsocket NOT initWebsocketStream
# Online variables are live data coming from the controller.
# Indices are started from 0 (seen in bench variables or singlestat on webui)
client_instance, connection_instance = conn.init_websocket_connection(
    url,
    port,
    route,
    username,
    password,
    timeout_sec,
    add_config
)

print("Client Instance:", client_instance)
print("Connection Instance:", connection_instance)

time.sleep(1)

name_index = []
print(index_to_write)
print(f"Hint: Remember, you can only write to Input or Input/Output channels!")
for i, index in enumerate(index_to_write):
    name_index.append(conn.get_channel_info_name(index))
    print(f"name of the channel where value {value_to_write[i]} will be written: {name_index[i]}")

# Get the totalIndex of Index
#conn.get_channel_info(0)

if conn.ret != 0:
    print(
        "A Mistake occured during connecting to the Gantner Controller. \
          Verifiy than you give right IP adress and controller is online"
    )
else:
    for i, index in enumerate(index_to_write):
        conn.write_online_value(index, value_to_write[i])
    conn.read_online_multiple(index_to_write)
    conn.close_connection()
