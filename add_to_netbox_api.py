import requests
from helper import read_yaml, form_connection_params_from_yaml
from pprint import pprint

NETBOX_API_ROOT = "http://10.10.1.100:8085/api"
NETBOX_DEVICES_ENDPOINT = "/dcim/devices/"
NETBOX_DEVICE_TYPES = "/dcim/device-types/"
NETBOX_SITES_ENDPOINT = "/dcim/sites/"
NETBOX_API_TOKEN = '454a75712e782741166ed11fe711e3d5f9476e05'

SITES = [{"name": "Krakow", "slug": "krk"}, {"name": "Reykjavík", "slug": "rkvk"}]


def form_headers():
    headers = {
        "Authorization": "Token {}".format(NETBOX_API_TOKEN),
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    return headers


def get_sites():
    """
    Getting info about sites from netbox and put them in list of "names"
    """
    headers = form_headers()
    r = requests.get(
        NETBOX_API_ROOT + NETBOX_SITES_ENDPOINT, headers=headers
    )
    sites = r.json()  # full dictionary from json response
    list_of_sites = [name['name'] for name in sites['results']]
    return list_of_sites


def get_device_types():
    """
    Getting info about device models from netbox and put them in list of "models"
    """
    headers = form_headers()
    r = requests.get(
        NETBOX_API_ROOT + NETBOX_DEVICE_TYPES, headers=headers
    )
    models = r.json()  # full dictionary from json response
    list_of_models = [model['model'] for model in models['results']]
    return list_of_models


def get_devices():
    """
    Getting info about devices from netbox and return dictionary
    """
    headers = form_headers()
    r = requests.get(
        NETBOX_API_ROOT + NETBOX_DEVICES_ENDPOINT, headers=headers
    )
    devices = r.json()  # full dictionary from json response
    return devices


# def fetch_netbox_info(netbox_session, url, params):
#    with netbox_session.get(url, params=params) as response:
#        result = await response.json()
#        return result["results"]


def add_site(name):
    """
    Add site with name
    """
    headers = form_headers()
    data = {"name": name, "slug": name}
    r = requests.post(
        NETBOX_API_ROOT + NETBOX_SITES_ENDPOINT, headers=headers, json=data
    )
    if r.status_code == 201:
        print(f"Site {name} was created successfully")
    else:
        r.raise_for_status()


def add_model(name):
    """
    Add site with name
    """
    headers = form_headers()
    data = {"name": name, "slug": name}
    r = requests.post(
        NETBOX_API_ROOT + NETBOX_SITES_ENDPOINT, headers=headers, json=data
    )
    if r.status_code == 201:
        print(f"Site {name} was created successfully")
    else:
        r.raise_for_status()


def add_sites():
    """Add sites from SITES dictionary"""
    for site in SITES:
        add_site(**site)
    print("All sites have been added")


def add_device(name, device_type_id, site_id, device_role_id):

    if 'access-switch' in devices['results'][1]['device_role'].values():
        ...: print(devices['results'][1]['device_role']['id'])

    headers = form_headers()
    data = {
        "name": name,
        "display_name": name,
        "device_type": device_type_id,  # 2,
        "site": site_id,  # 1,
        "status": 1,
    }
    if device_role_id is not None:
        data["device_role"] = device_role_id

    r = requests.post(
        NETBOX_API_ROOT + NETBOX_DEVICES_ENDPOINT, headers=headers, json=data
    )

    if r.status_code == 201:
        print(f"Device {name} was added successfully")
    else:
        r.raise_for_status()


def add_devices():
    parsed_yaml = read_yaml()
    devices_params_gen = form_connection_params_from_yaml(parsed_yaml)
    for device_params in devices_params_gen:
        add_device(**device_params)
    print("All devices have been imported")


def main():
    # headers = form_headers()
    # add_sites()
    # add_devices()
    get_sites()
    pprint(get_sites())

    parsed_yaml = read_yaml()
    for devices in parsed_yaml['all']['hosts']:
        if 'cisco' in devices['device_type']:
            pprint('ok')
            ## Add device with manufacture Cisco


if __name__ == "__main__":
    main()
