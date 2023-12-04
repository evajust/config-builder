#!/usr/bin/env python3

import sys
from argparse import ArgumentParser, RawTextHelpFormatter
import jinja2
import os
import re

PARSER_DESCRIPTION = "Script to save a router's config to $router_name.config"


def print_in_color(status, message):
    """
    To print texts in colors or underlined
    :param status: the message flag
    :param message: the message content
    :return: colored or underlined message
    """
    codes = {
        'ERROR': '\033[95m',
        'FAILED': '\033[41;1m',
        'OKBLUE': '\033[94m',
        'HEADER': '\033[46;1m',
        'OKGREEN': '\033[92m',
        'LINK': '\033[32;4m',
        'WARNING': '\033[93m',
        'ENDC': '\033[0m',
        'UNDERLINE': '\033[4m'
    }
    sys.stdout.write(codes.get(status.upper(), codes[
                     status]) + message + codes['ENDC'] + '\n')
    sys.stdout.flush()


def parse_args():
    '''
    Parse command line arguments

    device: a string containing either the IP address or
            hostname of the device.
    '''
    parser = ArgumentParser(description=PARSER_DESCRIPTION,
                            formatter_class=RawTextHelpFormatter,
                            add_help=True)
    parser.add_argument('-d', '--devices', dest='devices',
                        type=str, help="Name of the device. Can be regex or a single device.")
    parser.add_argument('-p', '--pattern', dest='pattern',
                        type=str, help="Regex pattern used to specify multiple devices.")
    return parser.parse_args()


def args_validator(args):
    '''
    Validate the command line arguments given.
    Provide specific help if the argument validation fails.

    Exit if any error is found.  Return if all validations pass.
    '''
    validation_failed = False
    if not args.devices and not args.pattern:
        print_in_color('ERROR', '[FAIL] - No device specified with -d or regex pattern specified with -p')
        validation_failed = True

    if validation_failed:
        exit(1)


def get_device_list(args):
    '''
    Gets the list of devices that will have their configs generated.
    '''

    if args.devices:
        return args.devices.split(',')
    if args.pattern:
        pattern = '^' + args.pattern + '$'
        device_list = []
        file_list = next(os.walk('./targetspec/'))[2]
        for file in file_list:
            if re.match(pattern, file):
                device_list.append(file)
        return device_list


def open_file(filename):
    '''
    Opens a file and returns the contents.
    '''
    with open(filename, 'r') as file:
        return file.read()


def write_config_file(config, device):
    '''
    Writes a string of text to a file.  Primarily used in this script
    to write the generated config to a file.
    '''
    with open("./out/" + device, 'w') as file:
        file.write(config)


def generate_config(device):
    '''
    Generates the deice config and outputs it to a file
    '''
    templateLoader = jinja2.FileSystemLoader(searchpath='./')
    templateEnv = jinja2.Environment(loader=templateLoader)
    config = templateEnv.get_template('./targetspec/' + device).render(HOSTNAME=device)
    try:
        os.mkdir("out")
        write_config_file(config, device)
    except Exception:
        write_config_file(config, device)


def main():
    args = parse_args()
    args_validator(args)
    device_list = get_device_list(args)
    for device in device_list:
        generate_config(device)


if __name__ == "__main__":
    main()
