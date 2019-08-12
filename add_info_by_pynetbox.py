import pynetbox
import re
import ipaddress
from collect_info_from_devices import collect_info
from pprint import pprint
from helper import make_slug

NETBOX_URL = "http://10.10.1.100:8085"
NETBOX_API_TOKEN = '454a75712e782741166ed11fe711e3d5f9476e05'
NETBOX_ROLES = {
    'br': 'Router',
    'ir': 'Router',
    'vg': 'Voice Gateway',
    'csp': 'Crypto',
    'fw': 'Firewall',
    'csw': 'Core Switch',
    'asw': 'Access Switch',
    'dsw': 'Distribution Switch',
    'bsw': 'Border Switch'
}
nb = pynetbox.api(url=NETBOX_URL, token=NETBOX_API_TOKEN)


def create_site(name):
    """
    Check if site doesn't exist add new site with same slug
    """
    sites = [str(site) for site in nb.dcim.sites.all()]
    if name not in sites:
        print('site {site} not exists. Creating site'.format(site=name))
        site = nb.dcim.sites.create(name=name, slug=make_slug(name))
        print('...done')
    else:
        print('site {site} is already exists'.format(site=name))
        site = nb.dcim.sites.get(name=name)
    return site


def create_device_type(model, manufacturer_id):
    """
    Create new device type (model). Manufacture ID must be known
    """
    try:
        result = nb.dcim.device_types.create(
            model=model,
            slug=make_slug(model),
            manufacturer=manufacturer_id
        )
        print('device type {model} is added'.format(model=result))
    except pynetbox.RequestError as e:
        print(e.error)


def create_device(name, device_type_id, device_role_id, site_id, serial=None):
    """
    creating device with type, role, site IDs
    or print error if device is already added or IDs are wrong
    """
    try:
        result = nb.dcim.devices.create(
            name=name,
            device_type=device_type_id,
            device_role=device_role_id,
            site=site_id,
            serial=serial
        )
        print('device {device} is added'.format(device=result))
    except pynetbox.RequestError as e:
        print(e.error)


def create_interface(device_id, name, type_id=1000, status=True, mtu=None, mac_address=None, description=None):
    """
    Create new interface of known device
    """
    try:
        result = nb.dcim.interfaces.create(
            device=device_id,
            name=name,
            form_factor=type_id,
            enabled=status,
            mtu=mtu,
            mac_address=mac_address,
            description=description
        )
        print('interface {intf} is added'.format(intf=result))
    except pynetbox.RequestError as e:
        print(e.error)


def update_interface(device, name, status=True, description=None):
    """
    Update description and status interface of known device
    """
    device_params = {
        'enabled': status,
        'description': description
    }
    try:
        result = nb.dcim.interfaces.get(
            device=device,
            name=name
        )
        for key, value in device_params.items():
            if dict(result)[key] is not value:
                result.update({key: value})
                print('{param} on interface {intf} is updated'.format(param=key, intf=result))

    except pynetbox.RequestError as e:
        print(e.error)


def create_vrf(name, description='', rd=None):
    """
    creating device with type, role, site IDs
    or print error if device is already added or IDs are wrong
    """
    try:
        result = nb.ipam.vrfs.create(
            name=name,
            description=description,
            rd=rd
        )
        print('VRF {vrf} is added'.format(vrf=result))
    except pynetbox.RequestError as e:
        print(e.error)


def create_ip_address(address, device_id, interface_id, vrf_id=None):
    """
    creating IP address for interface, VRF is optional
    """
    try:
        result = nb.ipam.ip_addresses.create(
            address=address,
            device=device_id,
            interface=interface_id,
            vrfs=vrf_id
        )
        print('IP address {ipaddr} is added'.format(ipaddr=result))
    except pynetbox.RequestError as e:
        print(e.error)


def delete_ip_address(address, device, interface, vrf_id=None):
    """
    deleting IP address for interface, VRF is optional
    """
    try:
        result = nb.ipam.ip_addresses.get(
            address=address,
            device=device,
            interface=interface,
            vrfs=vrf_id
        ).delete()
        print('IP address {ipaddr} is deleted'.format(ipaddr=address))
    except pynetbox.RequestError as e:
        print(e.error)


def main():
    """
    For parse site and device role from hostname use regex.
    For example: hostname is msk02-gpn-asw02. For site use first symbols, before "-"
    for role use symbols after last "-" (msk02, asw02)
    """

    """
    Read info from inventory.yml
    """
    dic_params = collect_info()
    pprint(dic_params)
    print('Begin to parsinng information for Netbox')
    regex = '(?P<site>\S+?)-(?P<role>\S+$)'
    vendors = [str(vendor).lower() for vendor in nb.dcim.manufacturers.all()]

    # Define vendor of device using device_type (must consider vendor name in Netbox)
    for device_type, list_params in dic_params.items():
        for vendor in vendors:
            if vendor in device_type:
                nb_manufacturer = nb.dcim.manufacturers.get(slug=vendor)
        # Parse devices from same vendor
        for device_params in list_params:
            hostname = device_params['version'][0]['HOSTNAME']
            match = re.search(regex, hostname)
            device_site = match.group('site')
            device_role = match.group('role')
            device_model = device_params['version'][0]['HARDWARE']
            device_serial = device_params['version'][0]['SERIAL']

            # because of I use eve-ng Cisco images, Hardware is empty. So I made device_model = unknown
            if device_model == '':
                device_model = 'unknown'

            # check if site is in base and create nb_site object
            if nb.dcim.sites.get(name=device_site) is None:
                print('site {site} does not exist. Creating site'.format(site=device_site))
                nb.dcim.sites.create(name=device_site, slug=make_slug(device_site))
                print('...done')
            nb_site = nb.dcim.sites.get(name=device_site)

            # find role from hostname and create nb_device_role object
            for key in NETBOX_ROLES.keys():
                if key in device_role:
                    nb_device_role = nb.dcim.device_roles.get(name=NETBOX_ROLES[key])

            # check if model is in base and create nb_model object
            if nb.dcim.device_types.get(model=device_model) is None:
                print('model {model} does not exist. Creating model'.format(model=device_model))
                create_device_type(device_model, nb_manufacturer.id)
                print('...done')
            nb_device_type = nb.dcim.device_types.get(model=device_model)

            # check if device is in base and create nb_device object
            if nb.dcim.devices.get(name=hostname) is None:
                create_device(hostname, nb_device_type.id, nb_device_role.id, nb_site.id, serial=device_serial)
            nb_device = nb.dcim.devices.get(name=hostname)

            # add interfaces from device
            device_interfaces = device_params['interfaces']  # list of dictionaries
            for interface in device_interfaces:
                # define values
                interface_name = interface['INTF']
                IPADDR = interface['IPADDR']
                MASK = interface['MASK']
                ip_list = [ip + '/' + mask for ip, mask in list(zip(IPADDR, MASK))]
                # transform netmask to bitmask (255.255.255.0 => 24)
                ip_list = [ipaddress.ip_interface(ip_address).with_prefixlen for ip_address in ip_list]

                interface_status = True
                if 'down' in interface['LINK_STATUS']:
                    interface_status = False

                interface_mtu = None
                if 'MTU' in interface.keys():
                    if interface['MTU'] is '':
                        interface_mtu = None
                    else:
                        interface_mtu = interface['MTU']

                interface_desc = ""
                if 'DESCRIPTION' in interface.keys():
                    interface_desc = interface['DESCRIPTION']
                interface_mac = None

                if 'MAC' in interface.keys():
                    interface_mac = interface['MAC']

                interface_vrf = None
                if 'VRF' in interface.kes():
                    if interface['VRF'] is '':
                        interface_vrf = None
                    else:
                        interface_vrf = interface['VRF']

                # create interface on device
                if nb.dcim.interfaces.get(device=nb_device, name=interface_name) is None:
                    print(
                        'interface {intf} on device {dev} does not exist. \nCreating interface'.format(
                            intf=interface_name, dev=nb_device))
                    create_interface(nb_device.id, interface_name, status=interface_status, mtu=interface_mtu,
                                     mac_address=interface_mac, description=interface_desc)
                else:
                    update_interface(nb_device, interface_name, status=interface_status, description=interface_desc)
                nb_interface = nb.dcim.interfaces.get(device=nb_device, name=interface_name)

                # create VRF from interface


                # create IP address and prefixes from interface
                # Compare list of IP from device with list of IP from ipam
                try:
                    nb_ip_list = nb.ipam.ip_addresses.filter(device=nb_device, interface=nb_interface)
                except pynetbox.RequestError as e:
                    print(e.error)
                nb_ip_list = [str(ip) for ip in nb_ip_list]

                # delete IP address in ipam if it doesn't exist on device
                for ip_addr in set(nb_ip_list).difference(ip_list):
                    print('found non actual IP address {ipaddr} on {intf} of {dev}.'
                          '\nDeleting it'.format(ipaddr=ip_addr, intf=nb_interface, dev=nb_device))
                    delete_ip_address(ip_addr, nb_device, nb_interface)

                # create IP address from device if in ipam it doesn't exist
                for ip_addr in set(ip_list).difference(nb_ip_list):
                    print('creating IP address {ipaddr} on {intf} of {dev}'.format(ipaddr=ip_addr, intf=nb_interface,
                                                                                   dev=nb_device))
                    create_ip_address(ip_addr, nb_device.id, nb_interface.id)

                for ip_addr in ip_list:
                    # create IP prefixes using "ipaddress" module
                    ip_intf = ipaddress.ip_interface(ip_addr)
                    if nb.ipam.prefixes.get(prefix=str(ip_intf.network)) is None and not str(
                            ip_intf.netmask) == '255.255.255.255':
                        nb.ipam.prefixes.create(prefix=str(ip_intf.network))


if __name__ == "__main__":
    main()
