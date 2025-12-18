''' Writes a value to a variable through a network connection '''
import argparse

from ginsapy.examples.CustomHelpFormatter import CustomHelpFormatter

import ginsapy.giutility.connect.highspeedport_client as highspeedport_client


def write_online_value(ip, index_to_write_array, value_to_write_array):
    if len(index_to_write_array) != len(value_to_write_array):
        raise ValueError("index_to_write and value_to_write must have the same length")

    # Initialisation of a buffer connection
    conn = highspeedport_client.HighSpeedPortClient()
    conn.init_online_connection(
        str(ip)
    )  # Take care use online connection for initialisation to have overall index number

    name_index = []
    for i, index_value in enumerate(index_to_write_array):
        name_index.append(conn.get_channel_info_name(index_value))
        print(f"name of the channel where value will be written: {name_index[i]}")

    if conn.ret != 0:
        print(
            "A Mistake occured during connecting to the Gantner Controller. \
            Verifiy that you give right IP address and that the controller is online"
        )
    else:
        for i, index_value in enumerate(index_to_write_array):
            conn.write_online_value(index_value, value_to_write_array[i])
        conn.close_connection()  # Close connection


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Write a value to one or more vairables over an IP-Address",
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
        "--controller_ip",
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
        "--index_to_write",
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
        "--value_to_write",
        nargs="+",
        type=float,
        help="Values to be written; Default is 0 10; \
            Multiple arguments can be given, space seperated (1 2 3); \
            Must have same number of arguments as -i/--index_to_write",
        required=False,
        default=[0, 10],
        metavar="",
    )

    args = parser.parse_args()

    controller_ip = args.controller_ip
    index_to_write = args.index_to_write
    value_to_write = args.value_to_write

    # Execute the function with the provided arguments
    write_online_value(controller_ip, index_to_write, value_to_write)
