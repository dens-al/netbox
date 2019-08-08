from copy import deepcopy
import yaml
from pprint import pprint
import re


def make_slug(s):
    # Remove all non-word characters (everything except numbers and letters)
    s = re.sub(r"[^\w\s]", '', s)
    # Replace all runs of whitespace with a single dash
    s = re.sub(r"\s+", '-', s)

    return s.lower()


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
    for key, list_params in dic_types.items():
        for site_dict in list_params:
            site_dict.update(parsed_yaml['vars'])
            site_dict.update({'device_type': key})
    return dic_types


if __name__ == '__main__':
    pprint(read_yaml(path="out_templates.yml"))
    # pprint(form_connection_params_from_yaml(read_yaml()))
