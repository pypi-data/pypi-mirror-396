''' Read values through a network connection '''
import argparse

import ginsapy.giutility.connect.highspeedport_client as highspeedport_client

from ginsapy.examples.CustomHelpFormatter import CustomHelpFormatter

parser = argparse.ArgumentParser(
    description="Read the value of one variable over an IP-Address",
    formatter_class=CustomHelpFormatter,
    add_help=False,
)

parser.add_argument(
    "-h",
    "--help",
    action="help",
    default=argparse.SUPPRESS,
    help="Show this help message and exit; \
        All arguments are optional; \
        Strings do not need to be quoted",
)
parser.add_argument(
    "-c",
    "--controller_IP",
    type=str,
    help='Controller IP address; \
        Default is an empty String; \
        Available Controllers can be found by clicking the "Read" button in GI.bench',
    required=False,
    default="",
    metavar="",
)
parser.add_argument(
    "-i",
    "--index_to_read",
    nargs="+",
    type=int,
    help="Channel indices to read; \
        Default is 1 2; \
        Multiple arguments can be given, space seperated (1 2 3); \
        Take care enter the index of input/output channels not input",
    required=False,
    default=[1, 2],
    metavar="",
)

args = parser.parse_args()

controller_IP = args.controller_IP
index_to_read = args.index_to_read

# Initialisation of a buffer connection
conn = highspeedport_client.HighSpeedPortClient()
conn.init_online_connection(
    str(controller_IP)
)  # Take care use online connection for initialisation to have overall index number

name_index = []
for i, index_value in enumerate(
    index_to_read, start=0
):  # Print all the channel names where data will be read
    name_index.append(conn.get_channel_info_name(index_value))
    print("name of the channel where value will be read :", name_index[i])

if conn.ret != 0:
    print(
        "A Mistake occured during connecting to the Gantner Controller. \
        Verifiy that you give right IP adress and that the controller is online"
    )
else:
    print(conn.read_online_multiple(index_to_read))
    conn.close_connection()  # Close connection
