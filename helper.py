from copy import deepcopy
import yaml
from pprint import pprint


def read_yaml(path="inventory.yml"):
    """
    Reads inventory yaml file and return dictionary with parsed values
    Args:
        path (str): path to inventory YAML
    Returns:
        dict: parsed inventory YAML values
    """
    with open(path) as f:
        yaml_content = yaml.safe_load(f.read())
    return yaml_content


def form_connection_params_from_yaml(parsed_yaml):
    """
    Form dictionary of netmiko connections parameters for all devices on the site
    Args:
        parsed_yaml (dict): dictionary with parsed yaml file
    Returns:
        list of dics containing netmiko connection parameters for the host
    """
    parsed_yaml = deepcopy(parsed_yaml)
    dic_types = parsed_yaml["hosts"]
    for list_params in dic_types.values():
        for site_dict in list_params:
            site_dict.update(parsed_yaml['vars'])
    return dic_types


if __name__ == '__main__':
    # print(read_yaml())
    pprint(form_connection_params_from_yaml(read_yaml()))
