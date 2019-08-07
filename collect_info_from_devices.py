#!/usr/bin/env python3
import netmiko
import textfsm
from pprint import pprint
from tabulate import tabulate
from helper import read_yaml, form_connection_params_from_yaml
from concurrent.futures import ProcessPoolExecutor, as_completed
import logging

COMMANDS_LIST = [
    "version", "inventory", "interfaces"
]
COMMANDS_CISCO_IOS_DIC = {
    'show version': 'out_templates/cisco_ios_show_version.template',
    'show inventory': 'out_templates/cisco_ios_show_inventory.template',
    'show interfaces': 'out_templates/cisco_ios_show_interfaces.template'
}
COMMANDS_CISCO_NXOS_DIC = {
    'show version': 'out_templates/cisco_nxos_show_version.template',
    'show inventory': 'out_templates/cisco_nxos_show_inventory.template',
    'show interface': 'out_templates/cisco_nxos_show_interface.template'
}
COMMANDS_CISCO_ASA_DIC = {
    'show version': 'out_templates/cisco_asa_show_version.template',
    'show inventory': 'out_templates/cisco_asa_show_inventory.template',
    'show interface': 'out_templates/cisco_asa_show_interface.template'
}

# COMMANDS_LIST = {
#    'cisco_ios': COMMANDS_LIST_CISCO_IOS,
#    'cisco_nxos' : COMMANDS_LIST_CISCO_NXOS
#    'cisco_asa': COMMANDS_LIST_CISCO_ASA
# }

logging.getLogger("paramiko").setLevel(logging.WARNING)
logging.basicConfig(
    format='%(message)s',
    level=logging.INFO)
start_msg = '=======> Connect to: {}'
received_msg = '<=== Received from: {}'
send_command_msg = '==> Send command: {}'


def send_commands(device, commands):
    """
    :param device: netmiko device dictionary
    :param commands: dictionary {command : textfsm template}. Defined in top
    :return: list of dictionaries {textfsm headers: out values}
    """
    ip = device['ip']
    results = []
    logging.info(start_msg.format(ip))
    for command, template in commands.items():
        with netmiko.ConnectHandler(**device) as ssh:
            # logging.info(send_command_msg.format(command))
            command_result = ssh.send_command(command)
            logging.info(received_msg.format(ip))
        with open(template) as temp:
            fsm = textfsm.TextFSM(temp)
            headers_out = fsm.header
            values_out = fsm.ParseText(command_result)
        command_result = [dict(zip(headers_out, outs)) for outs in values_out]
        results.append(command_result)
        print(tabulate(command_result, headers='keys') + "\n")  # For OUT print
    return results


def send_commands_to_devices(devices, commands, workers=6):
    """
    send list of commands for several devices in parallel.
    generate error if exception of connections
    :param devices: list of netmiko device dictionaries
    :param commands: dictionary {command : textfsm template}. Defined in top
    :param workers: number of parallel workers. Default = 6
    :return: list of dictionaries made in send_commands
    """
    list_of_results = []
    with ProcessPoolExecutor(max_workers=workers) as executor:
        future_ssh = [
            executor.submit(send_commands, device, commands) for device in devices
        ]
        for f in as_completed(future_ssh):
            try:
                result = f.result()
            except netmiko.ssh_exception.NetMikoAuthenticationException as e:
                print(e)
            except netmiko.ssh_exception.AuthenticationException as e:
                print(e)
            except netmiko.ssh_exception.NetMikoTimeoutException as e:
                print(e)
            except netmiko.ssh_exception.SSHException as e:
                print(e)
            else:
                list_of_results.append(result)
    return list_of_results


def collect_info_device_type(devices, commands_dic, workers, commands_type_list):
    """
    Make total dictionary of results of one device type (example: all info about all cisco_ios devices)
    :param devices: list of netmiko device dictionaries
    :param workers: number of parallel workers.
    :param commands_type_list: list of commands type. Defined in top.
    :param commands_dic:  dictionary {command : textfsm template}. Defined in top
    :return:
    """
    list_of_device_type_results = []
    result = send_commands_to_devices(devices, commands_dic, workers)
    for device in result:
        output_dic = dict(zip(commands_type_list, device))
        list_of_device_type_results.append(output_dic)
    return list_of_device_type_results


def collect_info2():
    parsed_yaml = read_yaml()
    pprint(parsed_yaml)
    connection_params = form_connection_params_from_yaml(parsed_yaml)

    for device_type in connection_params.keys():
        if device_type == 'cisco_ios':
            device_count = len(connection_params[device_type])
            cisco_ios_list = []
            result = send_commands_to_devices(connection_params[device_type], COMMANDS_CISCO_IOS_DIC,
                                              workers=device_count)
            for device in result:
                output_dic = dict(zip(COMMANDS_LIST, device))
                cisco_ios_list.append(output_dic)

        if device_type == 'cisco_asa':
            device_count = len(connection_params[device_type])
            cisco_asa_list = []
            result = send_commands_to_devices(connection_params[device_type], COMMANDS_CISCO_ASA_DIC,
                                              workers=device_count)
            for device in result:
                output_dic = dict(zip(COMMANDS_LIST, device))
                cisco_asa_list.append(output_dic)

        if device_type == 'cisco_nxos':
            device_count = len(connection_params[device_type])
            cisco_nxos_list = []
            result = send_commands_to_devices(connection_params[device_type], COMMANDS_CISCO_NXOS_DIC,
                                              workers=device_count)
            for device in result:
                output_dic = dict(zip(COMMANDS_LIST, device))
                cisco_nxos_list.append(output_dic)

    print('Collecting information completed')
    pprint(cisco_ios_list)
    pprint(cisco_asa_list)
    # pprint(cisco_nxos_list)
    output_list = cisco_ios_list + cisco_nxos_list + cisco_asa_list
    return output_list


if __name__ == "__main__":
    parsed_yaml = read_yaml()
    connection_params = form_connection_params_from_yaml(parsed_yaml)
    pprint(connection_params)
    for device_type, device_list in connection_params.items():
        if device_type == 'cisco_ios':
            device_count = len(device_list)
            cisco_ios_list = collect_info_device_type(device_list, COMMANDS_CISCO_IOS_DIC, device_count, COMMANDS_LIST)
        if device_type == 'cisco_asa':
            device_count = len(device_list)
            cisco_asa_list = collect_info_device_type(device_list, COMMANDS_CISCO_ASA_DIC, device_count, COMMANDS_LIST)
        if device_type == 'cisco_nxos':
            device_count = len(device_list)
            cisco_nxos_list = collect_info_device_type(device_list, COMMANDS_CISCO_NXOS_DIC, device_count, COMMANDS_LIST)
    pprint(cisco_ios_list)

    #collect_info2()
    #collect_info_device_type()
