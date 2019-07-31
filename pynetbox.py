import pynetbox

NETBOX_URL = "http://10.10.1.100:8085"
NETBOX_API_TOKEN = '454a75712e782741166ed11fe711e3d5f9476e05'

nb = pynetbox.api(url=NETBOX_URL, token=NETBOX_API_TOKEN)

def create_site(name):

def create_device(name, model_id, manufacture_id, role_id, site_id, serial=None):
