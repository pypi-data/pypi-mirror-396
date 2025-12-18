import os
import csv
import time
import argparse

import ginsapy.giutility.connect.highspeedport_client as highspeedport_client

# Class to clean up output of -h in cli
from ginsapy.examples.CustomHelpFormatter import CustomHelpFormatter

parser = argparse.ArgumentParser(
    description="Read values over an IP-Address indefinitely \
        and continously write them into a .csv file",
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
    help="Channel indices to read; Default is 1 2; \
        Multiple arguments can be given, space seperated (1 2 3)",
    required=False,
    default=[1, 2],
    metavar="",
)
parser.add_argument(
    "-s",
    "--sample_rate",
    type=int,
    help="Sampling rate in Hz; Default is 1",
    required=False,
    default=1,
    metavar="",
)
parser.add_argument(
    "-d",
    "--delimiter",
    type=str,
    help='Delimiter for CSV file; default is ","',
    required=False,
    default=",",
    metavar="",
)
parser.add_argument(
    "-f",
    "--file_name",
    type=str,
    help='Name of the CSV file to save values into; \
        Default is "out.csv"; \
        Note: .csv has to be added',
    required=False,
    default="out.csv",
    metavar="",
)

args = parser.parse_args()

controller_IP = args.controller_IP
index_to_read = args.index_to_read
sample_rate = args.sample_rate
delimiter = args.delimiter
file_name = args.file_name

sample_rate_ms = int(1000 / sample_rate)  # Sampling rate in milliseconds

# Initialisation of a buffer connection
conn = highspeedport_client.HighSpeedPortClient()
conn.init_online_connection(
    str(controller_IP)
)  # Take care use online connection for initialisation to have overall index number

csv_file = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
csv_dir = os.path.join(csv_file, "csv")
os.makedirs(csv_dir, exist_ok=True)
csv_file = os.path.join(csv_dir, file_name)

for i in range(len(index_to_read)):
    name_index = conn.get_channel_info_name(index_to_read[i])
    print(f"name_index:{name_index}")
if conn.ret != 0:
    print("Error: Check IP address and controller connection.")
else:
    with open(csv_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file, delimiter=delimiter)
        print(f"Start writing output to file: {csv_file}")
        try:
            while True:
                data = conn.read_online_multiple(index_to_read)
                writer.writerow(data)
                file.flush()
                time.sleep(sample_rate_ms / 1000)
        except KeyboardInterrupt:
            conn.close_connection()