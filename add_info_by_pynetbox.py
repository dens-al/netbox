import pynetbox
import re
from collect_info_from_devices import collect_info
from pprint import pprint

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
        site = nb.dcim.sites.create(name=name, slug=name.lower())
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
            slug=model.lower(),
            manufacturer=manufacturer_id
        )
        print('device type {model} is added'.format(model=result))
    except pynetbox.RequestError as e:
        print(e.error)


def create_interface(device_id, name):
    """
    Create new interface of known device
    """
    try:
        result = nb.dcim.interfaces.create(
            device=device_id,
            name=name
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


def main():
    """
    For parse site and device role from hostname use regex.
    For example: hostname is msk02-gpn-asw02. For site use first symbols, before "-"
    for role use symbols after last "-" (msk02, asw02)
    """

    """
    Read info from inventory.yml
    """
    list_params = collect_info()
    pprint(list_params)
    vendor = 'Cisco'
    regex = '(?P<site>\S+?)-(?P<role>\S+$)'
    for device_params in list_params:
        hostname = device_params['version'][0]['HOSTNAME']
        match = re.search(regex, hostname)
        device_site = match.group('site')
        device_role = match.group('role')
        device_type = device_params['version'][0]['HARDWARE']

        # because of I use eve-ng Cisco images, Hardware is empty. So I made device_type = uknown
        if device_type == '':
            device_type = 'IOS-L3v'
        device_serial = device_params['version'][0]['SERIAL']

        # check if site is in base and create nb_site object
        if nb.dcim.sites.get(name=device_site) is None:
            print('site {site} not exists. Creating site'.format(site=device_site))
            nb.dcim.sites.create(name=device_site, slug=device_site.lower())
            print('...done')
        nb_site = nb.dcim.sites.get(name=device_site)

        # find role from hostname and create nb_device_role object
        for key in NETBOX_ROLES.keys():
            if key in device_role:
                nb_device_role = nb.dcim.device_roles.get(name=NETBOX_ROLES[key])

        nb_manufacturer = nb.dcim.manufacturers.get(name=vendor)  ## don't know how make Cisco

        # check if model is in base and create nb_model object
        if nb.dcim.device_types.get(model=device_type) is None:
            print('model {model} not exists. Creating model'.format(model=device_type))
            create_device_type(device_type, nb_manufacturer.id)
            print('...done')
        nb_device_type = nb.dcim.device_types.get(model=device_type)

        # check if device is in base and create nb_device object
        if nb.dcim.devices.get(name=hostname) is None:
            create_device(hostname, nb_device_type.id, nb_device_role.id, nb_site.id, serial=device_serial)
        nb_device = nb.dcim.devices.get(name=hostname)

        ## add interfaces from device
        device_interfaces = device_params['interfaces']  # list of dictionaries
        for interface in device_interfaces:
            if nb.dcim.interfaces.get(device=nb_device.id, name=interface['INTF']) is None:
                print('interface {intf} not exists. Creating interface'.format(intf=interface['INTF']))
                create_interface(nb_device.id, interface['INTF'])
                print('...done')
            nb_interface = nb.dcim.interfaces.get(device=nb_device.id, name=interface['INTF'])

            ## create IP address from interface
            if interface['VRF'] is '':
                for ip_prefix in interface['IPADDR']:
                    if nb.ipam.ip_addresses.get(addess=ip_prefix) is None:
                        print('ip address {ipaddr} not exists. Creating ip address on interface {intf}'.format(
                            ipaddr=ip_prefix, intf=nb_interface))
                        create_ip_address(ip_prefix, nb_device.id, nb_interface.id)
            # if nb.ipam.ip_addresses.get():
            # nb.ipam.ip_addresses.create(address='192.168.88.101/24', device=nb_device.id, interface=nb_interface.id)


if __name__ == "__main__":
    main()
