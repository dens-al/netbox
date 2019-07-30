#!/usr/bin/env python3
import netmiko
import textfsm
from pprint import pprint
from tabulate import tabulate
from helper import read_yaml, form_connection_params_from_yaml

COMMANDS_LIST = [
    "show version", "show inventory", "show ip interface brief", "show ip route"
]
COMMANDS_CISCO_IOS_DIC = {
   'show version' : 'out_templates/cisco_ios_show_version.template',
   'show inventory' : 'out_templates/cisco_ios_show_inventory.template'
#   'show ip route' : 'out_templates/cisco_ios_show_ip_route.template'
}
COMMANDS_CISCO_NXOS_DIC = {
   'show version' : 'out_templates/cisco_nxos_show_version.template',
   'show inventory' : 'out_templates/cisco_nxos_show_inventory.template',
   'show ip route' : 'out_templates/cisco_nxos_show_ip_route.template'
}
COMMANDS_CISCO_ASA_DIC = {
   'show version' : 'out_templates/cisco_nxos_show_version.template',
   'show inventory' : 'out_templates/cisco_nxos_show_inventory.template',
   'show route' : 'out_templates/cisco_nxos_show_ip_route.template'
}
#COMMANDS_LIST = {
#    'cisco_ios': COMMANDS_LIST_CISCO_IOS,
#    'cisco_nxos' : COMMANDS_LIST_CISCO_NXOS
#    'cisco_asa': COMMANDS_LIST_CISCO_ASA
#}
def collect_outputs(devices, commands):
    """
    Collects commands from the list of devices
    Args:
        devices (list of dics): list of netmiko connection dictionaries
        commands (dic): key is command, value is out texfsm template
    Returns:
        outputs (list of dict): key is the headers, value is string with all outputs
    """
    output_results = []
    for device in devices:
        connection = netmiko.ConnectHandler(**device)
        #device_result = {}
        #print("{0} {1} {0}".format("=" * 50, device['ip']))
        for command, template in commands.items():
            command_result = connection.send_command(command)

            with open(template) as template:
                fsm = textfsm.TextFSM(template)
                headers_out = fsm.header
                results_out = fsm.ParseText(command_result)

            #for results in results_out:
            #    device_result.update(dict(zip(headers_out,results)))
            #pprint(device_result)
            result = [dict(zip(headers_out,results)) for results in results_out]
            #print(tabulate(result, headers='keys'))
            pprint(result)
        output_results.append(result)
        #output_results.append(device_result)
        connection.disconnect()
        #device_result = device_result.update(result)
    return output_results


#       device_result_string = "\n\n".join(device_result)
#        connection.disconnect()
#        yield device_result_string

def main():
    parsed_yaml = read_yaml()
    print("Inventory file read successfully")
    connection_params = form_connection_params_from_yaml(parsed_yaml)

#    for device_result in collect_outputs(connection_params, COMMANDS_CISCO_IOS_DIC):
#        pprint(device_result)
    pprint(collect_outputs(connection_params, COMMANDS_CISCO_IOS_DIC))

if __name__ == "__main__":
    main()