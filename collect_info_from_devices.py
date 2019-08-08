#!/usr/bin/env python3
import netmiko
import textfsm
from pprint import pprint
from tabulate import tabulate
from helper import read_yaml, form_connection_params_from_yaml
from concurrent.futures import ProcessPoolExecutor, as_completed
import logging

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


def collect_info():
    """
    read inventory.yml as input information, out_templates.yml as information about textfsm templates and return dic of
    collected info
    :return:
    """
    parsed_yaml_inventory = read_yaml(path="inventory.yml")
    parsed_yaml_template = read_yaml(path="out_templates.yml")
    # pprint(parsed_yaml_template)
    connection_params = form_connection_params_from_yaml(parsed_yaml_inventory)
    # pprint(connection_params)

    # check wrong names in inventory file
    wrong_names = []
    for device_type in connection_params.keys():
        if device_type not in parsed_yaml_template.keys():
            print(
                'device type {type} does not have OUT template in out_templates.yml\nDelete it'.format(
                    type=device_type))
            wrong_names.append(device_type)
    for name in wrong_names:
        del (connection_params[name])

    total_result = {}
    for device_type, device_list in connection_params.items():
        device_count = len(device_list)
        type_result_list = collect_info_device_type(
            device_list, parsed_yaml_template[device_type], device_count, parsed_yaml_template['command_list'])
        total_result.update({device_type: type_result_list})
    return total_result


if __name__ == "__main__":
    collect_info()
