#!/usr/bin/env python3
import netmiko
import textfsm
from pprint import pprint
from tabulate import tabulate
from helper import read_yaml, form_connection_params_from_yaml
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime
import time
from itertools import repeat
import logging

COMMANDS_LIST = [
    "version", "inventory", "interfaces"
]
COMMANDS_CISCO_IOS_DIC = {
    'show version': 'out_templates/cisco_ios_show_version.template',
    'show inventory': 'out_templates/cisco_ios_show_inventory.template',
    'show ip interface': 'out_templates/cisco_ios_show_ip_interface.template'
}
COMMANDS_CISCO_NXOS_DIC = {
    'show version': 'out_templates/cisco_nxos_show_version.template',
    'show inventory': 'out_templates/cisco_nxos_show_inventory.template',
    'show ip route': 'out_templates/cisco_nxos_show_ip_route.template'
}
COMMANDS_CISCO_ASA_DIC = {
    'show version': 'out_templates/cisco_ios_show_version.template',
    'show inventory': 'out_templates/cisco_ios_show_inventory.template',
    'show route': 'out_templates/cisco_ios_show_ip_route.template'
}

# COMMANDS_LIST = {
#    'cisco_ios': COMMANDS_LIST_CISCO_IOS,
#    'cisco_nxos' : COMMANDS_LIST_CISCO_NXOS
#    'cisco_asa': COMMANDS_LIST_CISCO_ASA
# }

logging.getLogger("paramiko").setLevel(logging.WARNING)

logging.basicConfig(
    format='%(threadName)s %(name)s %(levelname)s: %(message)s',
    level=logging.INFO)

start_msg = '===> {} Connection: {}'
received_msg = '<=== {} Received: {}'


def send_commands(device, commands):
    """
    :param template: textfsm template
    :param device: netmiko device dictionary
    :param commands: dictionary {command : textfsm template}
    :return: list of dictionaries {textfsm headers: out values}
    """
    ip = device['ip']
    total_result = []
    logging.info(start_msg.format(datetime.now().time(), ip))
    for command, template in commands.items():
        with netmiko.ConnectHandler(**device) as ssh:
            command_result = ssh.send_command(command)
            logging.info(received_msg.format(datetime.now().time(), ip))
        with open(template) as temp:
            fsm = textfsm.TextFSM(temp)
            headers_out = fsm.header
            values_out = fsm.ParseText(command_result)
        result_for_print = [dict(zip(headers_out, results)) for results in values_out]
        total_result.append(result_for_print)
    # print(tabulate(result_for_print, headers='keys') + "\n") # For OUT print
    return total_result


def send_commands_to_devices(devices, commands, template):
    data = []
    with ProcessPoolExecutor(max_workers=6) as executor:
        future_ssh = [
            executor.submit(send_commands, device, commands, template) for device in devices
        ]
        for f in as_completed(future_ssh):
            try:
                result = f.result()
            except netmiko.ssh_exception.NetMikoAuthenticationException as e:
                print(e)
            else:
                data.append(result)
    return data


def collect_outputs(device, commands, param_names):
    """
    Collects commands from the list of devices
    Args:
        device (dic): netmiko connection dictionary
        commands (dic): key is command, value is out texfsm template
        param_names: list of params, that get with commands
    Returns:
        output dict, where key is name of parameter and value is dict
        of headers and outputs
    """
    output_results = []
    connection = netmiko.ConnectHandler(**device)
    print("\n{0} {1} {0}".format("=" * 50, device['ip']))
    for command, template in commands.items():
        command_result = connection.send_command(command)
        with open(template) as temp:
            fsm = textfsm.TextFSM(temp)
            headers_out = fsm.header
            values_out = fsm.ParseText(command_result)
        result_for_print = [dict(zip(headers_out, results)) for results in values_out]
        # print(tabulate(result_for_print, headers='keys') + "\n")
        output_results.append(result_for_print)
    output_dic = dict(zip(param_names, output_results))
    connection.disconnect()
    return output_dic


def collect_info2():
    parsed_yaml = read_yaml()
    print("Inventory file read successfully")
    connection_params = form_connection_params_from_yaml(parsed_yaml)
    all_devices = []
    for device in connection_params:
        out = collect_outputs(device, COMMANDS_CISCO_IOS_DIC, COMMANDS_LIST)
        # pprint(out)
        all_devices.append(out)
    pprint(all_devices)
    return all_devices


def collect_info():
    parsed_yaml = read_yaml()
    all_devices = []
    connection_params = form_connection_params_from_yaml(parsed_yaml)
    # pprint(connection_params)
    for command, template in COMMANDS_CISCO_IOS_DIC.items():
        result = send_command_to_devices(connection_params, command, template)
        output_dic = dict(zip(COMMANDS_LIST, result))
        all_devices.append(output_dic)
    pprint(all_devices)
    return all_devices


if __name__ == "__main__":
    collect_info()
