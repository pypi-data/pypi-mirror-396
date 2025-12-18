import time
import argparse
import numpy as np

import ginsapy.giutility.connect.highspeedport_client as highspeedport_client

from scipy.integrate import quad  # Module for integration

# Class to clean up output of -h in cli
from ginsapy.examples.CustomHelpFormatter import CustomHelpFormatter

from example_write_online_values import (
    write_online_value,
)  # Module for writing online value before using them to calculate

parser = argparse.ArgumentParser(
    description="Calculate value of variable using other variables \
        and mathematical operations and write result to variable over an IP-Address",
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
    help='Controller IP address; Default is an empty String; \
        Available Controllers can be found by clicking the "Read" button in GI.bench',
    required=False,
    default="",
    metavar="",
)
parser.add_argument(
    "-r",
    "--index_to_read",
    nargs="+",
    type=int,
    help="Channel indices to read; Default is 1 2; \
        Multiple arguments can be given, space seperated (1 2 3)",
    required=False,
    default=[1, 2],
    metavar="",
)
parser.add_argument(
    "-w",
    "--index_to_write",
    type=int,
    help="Index where value is to be written; Default is 3",
    required=False,
    default=3,
    metavar="",
)
parser.add_argument(
    "-e",
    "--execute_write_values",
    type=bool,
    help="Write values before calculating online value; \
        If this flag is false, -i and -v will have no effect. \
        If this flag is true, write_online_value() will be called; \
        Default is False",
    required=False,
    default=False,
    metavar="",
)
parser.add_argument(
    "-i",
    "--index_array",
    nargs="+",
    type=int,
    help="Channel indices to write; \
        Default is 1 2; \
        Multiple arguments can be given, space seperated (1 2 3)",
    required=False,
    default=[1, 2],
    metavar="",
)
parser.add_argument(
    "-v",
    "--value_array",
    nargs="+",
    type=float,
    help="Values to be written; \
        Default is 1 10; \
        Multiple arguments can be given, space seperated (1 2 3)",
    required=False,
    default=[1, 10],
    metavar="",
)

args = parser.parse_args()

controller_IP = args.controller_IP
index_to_read = args.index_to_read
index_to_write = args.index_to_write
index_to_write_array = args.index_array
value_to_write_array = args.value_array

# *****************************************************
# Optional: write online values first
# *****************************************************

execute = args.execute_write_values
if execute:
    write_online_value(controller_IP, index_to_write_array, value_to_write_array)
time.sleep(1)  # Wait for values to be written

# *****************************************************
# Calculate Online Value
# *****************************************************

# Initialisation of a buffer connection
conn = highspeedport_client.HighSpeedPortClient()
conn.init_online_connection(
    str(controller_IP)
)  # Take care use online connection for initialisation to have overall index number

name_index = conn.get_channel_info_name(index_to_write)
print("name of the channel where value will be written :", name_index)

# Read variables specified by indices in index_to_read
variable_values = conn.read_online_multiple(index_to_read)


# We integrate from var1 to var2
def f(x):
    ''' defines a function that is used to calculate the value '''
    return (1 / np.log(x) ** 2) ** 0.5


print(variable_values)

value_to_write, err = quad(f, variable_values[0], variable_values[1])

if conn.ret != 0:
    print(
        "A Mistake occured during connecting to the Gantner Controller. \
            Verifiy that you give right IP adress and that the controller is online"
    )
else:
    conn.write_online_value(index_to_write, value_to_write)
    print("we add value to the selected channel")
    conn.close_connection()  # Close connection
