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
    return sites


def get_device_types():
    """
    Getting info about device models from netbox and put them in list of "models"
    """
    headers = form_headers()
    r = requests.get(
        NETBOX_API_ROOT + NETBOX_DEVICE_TYPES, headers=headers
    )
    models = r.json()  # full dictionary from json response
    return models


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


# def add_sites():
#    """Add sites from SITES dictionary"""
#    for site in SITES:
#        add_site(**site)
#    print("All sites have been added")


def add_device(name, model_id, manufacture_id, role_id, site_id, serial=None):
    """
    Add device using income parameters
    :param serial: Serial Number, not nessesusary
    :param name: hostname
    :param model_id: id of model (existing list, require to use from list)
    :param manufacture_id: id of manufacturer (e2ixisting list, require to use from list)
    :param site_id: id of site (existing list, require to use from list)
    :param role_id: id of role (existing list, (router,switch etc.), require to use from list)
    :return: nothing. Make POST url to netbox API
    """
    headers = form_headers()
    data = {
        "name": name,
        "display_name": name,
        "device_type": [model_id],  # 2,
        "manufacturer": manufacture_id,  # 3
        "device_role": [role_id],
        "site": [site_id],  # 1,
        "serial": serial,
        "status": 1
    }
    pprint(data)
    #r = requests.post(
    #   NETBOX_API_ROOT + NETBOX_DEVICES_ENDPOINT, headers=headers, json=data
    #)

    #if r.status_code == 201:
    #   print("Device {name} was added successfully")
    #else:
    #   r.raise_for_status()


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

    sites = get_sites()
    list_of_sites = [name['name'] for name in sites['results']]
    pprint(list_of_sites)

    models = get_device_types()
    list_of_models = [model['model'] for model in models['results']]
    pprint(list_of_models)

    devices = get_devices()
    list_of_devices = [device['name'] for device in devices['results']]
    pprint(list_of_devices)

    # if 'access-switch' in devices['results'][1]['device_role'].values():
    #   ...: print(devices['results'][1]['device_role']['id'])

    # parsed_yaml = read_yaml()
    # for devices in parsed_yaml['all']['hosts']:
    #    if 'cisco' in devices['device_type']:
    #        pprint('ok')
    ## Add device with manufacture Cisco
    add_device('ufa01-csw01', 3, 2, 1, 4)


if __name__ == "__main__":
    main()
