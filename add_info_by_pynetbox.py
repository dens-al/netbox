import pynetbox
import re

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
        nb.dcim.sites.create(name=name, slug=name.lower())
        print('...done')
    else:
        print('site {site} is already exists'.format(site=name))

def create_device_type(name):
    """
    Check if device-type doesn't exist add new model with same slug
    """
    models = [str(model) for model in nb.dcim.device_types.all()]
    if name not in models:
        print('model {model} not exists. Creating new model'.format(model=name))
        nb.dcim.device_types.create(name=name, slug=name.lower())
        print('...done')
    else:
        print('site {site} is already exists'.format(site=name))

def main():
    """
    For parse site and device role from hostname use regex.
    For example: hostname is msk02-gpn-asw02. For site use first symbols, before "-"
    for role use symbols after last "-" (msk02, asw02)
    """
    regex = '(?P<site>\S+?)-(?P<role>\S+$)'
    hostname = 'msk02-br01'
    match = re.search(regex, hostname)
    device_site = match.group('site')
    device_role = match.group('role')

    create_site(device_site)

if __name__ == "__main__":
    main()

