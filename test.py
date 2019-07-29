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
    'show version': 'out_templates/cisco_ios_show_version.template',
    'show inventory': 'out_templates/cisco_ios_show_inventory.template',
    'show ip route': 'out_templates/cisco_ios_show_ip_route.template'
}
COMMANDS_CISCO_NXOS_DIC = {
    'show version': 'out_templates/cisco_nxos_show_version.template',
    'show inventory': 'out_templates/cisco_nxos_show_inventory.template',
    'show ip route': 'out_templates/cisco_nxos_show_ip_route.template'
}
COMMANDS_CISCO_ASA_DIC = {
    'show version': 'out_templates/cisco_nxos_show_version.template',
    'show inventory': 'out_templates/cisco_nxos_show_inventory.template',
    'show route': 'out_templates/cisco_nxos_show_ip_route.template'
}
# COMMANDS_LIST = {
#    'cisco_ios': COMMANDS_LIST_CISCO_IOS,
#    'cisco_nxos' : COMMANDS_LIST_CISCO_NXOS
#    'cisco_asa': COMMANDS_LIST_CISCO_ASA
# }
output = '''
Cisco IOS Software, C2960 Software (C2960-LANBASEK9-M), Version 15.0(2)SE4, RELEASE SOFTWARE (fc1)
Technical Support: http://www.cisco.com/techsupport
Copyright (c) 1986-2013 by Cisco Systems, Inc.
Compiled Wed 26-Jun-13 02:49 by mnguyen

ROM: Bootstrap program is C2960 boot loader
BOOTLDR: C2960 Boot Loader (C2960-HBOOT-M) Version 12.2(25r)FX, RELEASE SOFTWARE (fc4)

Switch uptime is 39 minutes
System returned to ROM by power-on
System image file is "flash:c2960-lanbasek9-mz.150-2.SE4.bin"

This product contains cryptographic features and is subject to United
....

cisco WS-C2960-24TT-L (PowerPC405) processor (revision B0) with 65536K bytes of memory.
Processor board ID FOC1010X104
Last reset from power-on
1 Virtual Ethernet interface
24 FastEthernet interfaces
2 Gigabit Ethernet interfaces
The password-recovery mechanism is enabled.

64K bytes of flash-simulated non-volatile configuration memory.
Base ethernet MAC Address : 00:17:59:A7:51:80
Motherboard assembly number : 73-10390-03
Power supply part number : 341-0097-02
Motherboard serial number : FOC10093R12
Power supply serial number : AZS1007032H
Model revision number : B0
Motherboard revision number : B0
Model number : WS-C2960-24TT-L
System serial number : FOC1010X104
Top Assembly Part Number : 800-27221-02
Top Assembly Revision Number : A0
Version ID : V02
CLEI Code Number : COM3L00BRA
Hardware Board Revision Number : 0x01


Switch Ports Model SW Version SW Image
------ ----- ----- ---------- ----------
* 1 26 WS-C2960-24TT-L 15.0(2)SE4 C2960-LANBASEK9-M


Configuration register is 0xF
'''


def collect_outputs(command_result):
    with open('out_templates/cisco_ios_show_version.template') as template:
        fsm = textfsm.TextFSM(template)
        header_out = fsm.header
        result_out = fsm.ParseText(command_result)
        result = [dict(zip(header_out, results)) for results in result_out]
        print(tabulate(result, headers='keys'))
    #            device_result.append("{0} {1} {0}".format("=" * 20, command))
    #            device_result.append(command_result)
    # connection.disconnect()

    return result


#       device_result_string = "\n\n".join(device_result)
#        connection.disconnect()
#        yield device_result_string


def main():
    for device_result in collect_outputs(output):
        print(device_result)


if __name__ == "__main__":
    main()
