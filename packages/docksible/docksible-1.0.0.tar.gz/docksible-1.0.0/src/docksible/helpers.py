import os
from sys import path as sys_path
from secrets import token_hex
from ipaddress import ip_address


def find_templates_dir():
    for path_str in sys_path:
        try:
            try_path = os.path.join(path_str, 'docksible', 'templates')
            assert os.path.isdir(try_path)
            return try_path
        except AssertionError:
            pass
    raise RuntimeError('Found no template directory')


def host_is_local(host):
    if host.lower() == 'localhost':
        return True
    try:
        tmp_ip = ip_address(host)
        return tmp_ip.is_loopback
    except ValueError:
        return False


def host_is_private(host):
    try:
        tmp_ip = ip_address(host)
        return tmp_ip.is_private or tmp_ip.is_link_local
    except ValueError:
        return False
