#!/usr/bin/env python3
import netmiko
import textfsm

from helper import read_yaml, form_connection_params_from_yaml

#SITE_NAME = "SJ-HQ"

COMMANDS_LIST = [
    "show clock", "show version", "show inventory", "show ip interface brief"
]

def collect_outputs(devices, commands):
    """
    Collects commands from the list of devices
    Args:
        devices (list): list of netmiko connection dictionaries
        commands (list): list of commands to be executed on every device
    Returns:
        dict: key is the hostname, value is string with all outputs
    """
    for device in devices:
#        hostname = device.pop("hostname")
        connection = netmiko.ConnectHandler(**device)
        device_result = ["{0} {1} {0}".format("=" * 20, device)]

        for command in commands:
            command_result = connection.send_command(command)
            device_result.append("{0} {1} {0}".format("=" * 20, command))
            device_result.append(command_result)


        with open('/Users/den/PycharmProjects/netbox_utils/out_templates/cisco_ios_show_ip_int_brief.template') as template:
            fsm = textfsm.TextFSM(template)
            result_out = fsm.ParseText(result)

        device_result_string = "\n\n".join(device_result)
        connection.disconnect()
        yield device_result_string


def main():
    parsed_yaml = read_yaml()
    connection_params = form_connection_params_from_yaml(parsed_yaml, site=SITE_NAME)
    for device_result in collect_outputs(connection_params, COMMANDS_LIST):
        print(device_result)


if __name__ == "__main__":
    main()