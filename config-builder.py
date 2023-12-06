#!/usr/bin/env python3

import sys
import argparse
import jinja2
import os
import re

PARSER_DESCRIPTION = "Script to save a router's config to $router_name.config"


def print_in_color(status: str, message: str) -> None:
    """
    To print texts in colors or underlined
    :param status: the message flag
    :param message: the message content
    :return: colored or underlined message
    """
    codes = {
        "ERROR": "\033[95m",
        "FAILED": "\033[41;1m",
        "OKBLUE": "\033[94m",
        "HEADER": "\033[46;1m",
        "OKGREEN": "\033[92m",
        "LINK": "\033[32;4m",
        "WARNING": "\033[93m",
        "ENDC": "\033[0m",
        "UNDERLINE": "\033[4m",
    }
    sys.stdout.write(
        codes.get(status.upper(), codes[status])
        + message
        + codes["ENDC"]
        + "\n"
    )
    sys.stdout.flush()


def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments

    device: a string containing either the IP address or
            hostname of the device.
    """
    parser = argparse.ArgumentParser(
        description=PARSER_DESCRIPTION,
        formatter_class=argparse.RawTextHelpFormatter,
        add_help=True,
    )
    parser.add_argument(
        "-d",
        "--devices",
        dest="devices",
        type=str,
        help="Name of the device. Can be regex or a single device.",
        required=True,
    )
    parser.add_argument(
        "-p",
        "--pattern",
        dest="pattern",
        type=str,
        help="Regex pattern used to specify multiple devices.",
        required=True,
    )
    return parser.parse_args()


def get_device_list(args: argparse.Namespace) -> list[str]:
    """
    Gets the list of devices that will have their configs generated.
    """

    if args.devices:
        return args.devices.split(",")
    elif args.pattern:
        pattern = "^" + args.pattern + "$"
        device_list = []
        file_list = next(os.walk("./targetspec/"))[2]
        for file in file_list:
            if re.match(pattern, file):
                device_list.append(file)
        return device_list
    else:
        raise (RuntimeError("No devices or pattern found"))


def open_file(filename: str) -> str:
    """
    Opens a file and returns the contents.
    """
    with open(filename, "r") as file:
        return file.read()


def write_config_file(config: str, device: str) -> None:
    """
    Writes a string of text to a file.  Primarily used in this script
    to write the generated config to a file.
    """
    with open("./out/" + device, "w") as file:
        file.write(config)


def generate_config(device: str) -> None:
    """
    Generates the deice config and outputs it to a file
    """
    templateLoader = jinja2.FileSystemLoader(searchpath="./")
    templateEnv = jinja2.Environment(loader=templateLoader)
    config = templateEnv.get_template("./targetspec/" + device).render(
        HOSTNAME=device
    )
    try:
        os.mkdir("out")
        write_config_file(config, device)
    except Exception:
        write_config_file(config, device)


def main() -> None:
    args = parse_args()
    device_list = get_device_list(args)
    for device in device_list:
        generate_config(device)


if __name__ == "__main__":
    main()
