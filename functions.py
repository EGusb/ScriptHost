import ipaddress
import logging as log
import re

from cryptography.hazmat.primitives.asymmetric import dsa
from datetime import datetime
from netmiko import ConnectHandler
from ping3 import ping


def _override_check_dsa_parameters(parameters):
    """This fixed function allows netmiko to work properly. Do not remove."""
    if parameters.p.bit_length() not in [1024, 2048, 3072, 4096, parameters.p.bit_length()]:
        raise ValueError(
            "p must be exactly 1024, 2048, 3072, or 4096 bits long"
        )
    if parameters.q.bit_length() not in [160, 224, 256]:
        raise ValueError("q must be exactly 160, 224, or 256 bits long")

    if not (1 < parameters.g < parameters.p):
        raise ValueError("g, p don't satisfy 1 < g < p.")


dsa._check_dsa_parameters = _override_check_dsa_parameters


def conect_host(host, username, password, port=22, **kwargs) -> ConnectHandler or None:
    """
    Establishes an SSH conection with the IP address provided as host.
    :param string host: IP address of host.
    :param string username: username for connecting to host.
    :param string password: password for username.
    :param int port: TCP port used for connection.
    :returns: ConnectHandler object or None
    """
    ssh = ConnectHandler(
        device_type='autodetect',
        host=host,
        username=username,
        password=password,
        port=port,
        **kwargs,
    )
    return ssh


def is_ipv4_address(ip: str) -> bool:
    try:
        return type(ipaddress.ip_address(ip)) is ipaddress.IPv4Address
    except ValueError:
        return False


def is_ipv6_address(ip: str) -> bool:
    try:
        return type(ipaddress.ip_address(ip)) is ipaddress.IPv6Address
    except ValueError:
        return False


def is_mac_address(mac: str) -> bool:
    return bool(re.match("[0-9a-f]{2}([-:]?)[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", mac.lower()))


async def ping_host(host):
    return ping(host, unit='ms')


def start_log(file, log_path, ext='log', msg_fmt='{message}', datefmt='%Y/%m/%d %H:%M:%S', level=log.INFO):
    """
    Establishes an SSH conection with the IP address provided as host.
    :param string file: __file__ var from the script calling this function.
    :param string log_path: full path of the directory where the final log file will be saved.
    :param string ext: extension of the log file.
    :param string msg_fmt: format for the logs.
    :param string datefmt: date format for the logs.
    :param string level: logging level.
    :returns: A string for the full path where the log file will be saved.
    """
    now = datetime.now()
    timestamp = f"{now.year:02d}{now.month:02d}{now.day:02d}_{now.hour:02d}{now.minute:02d}{now.second:02d}"
    script_name = f"{file}".replace('\\', '/').split('/')[-1].replace('.py', '')
    logfile_name = f"{script_name}_{timestamp}.{ext}"

    if log_path:
        log_path = log_path.replace('\\', '/') + '/'
    else:
        log_path = '/'.join(f"{file}".replace('\\', '/').split('/')[:-1]) + '/logs/'
    log_path = log_path + logfile_name

    log.basicConfig(
        level=level,
        format=msg_fmt,
        datefmt=datefmt,
        style='{',
        handlers=[
            log.FileHandler(log_path, mode='w'),
            log.StreamHandler()
        ]
    )

    return log_path
