import functions

from pydantic import BaseModel, validator
from ping3 import ping


class Host(BaseModel):
    name: str
    ip_address: str
    port: int
    mac_address = ''

    @validator('ip_address')
    def is_ip_address(cls, v):
        if not functions.is_ipv4_address(v) and not functions.is_ipv6_address(v):
            raise ValueError("Invalid IP address. It must be either an IPv4 or IPv6 address.")
        return v

    @validator('mac_address')
    def is_mac_address(cls, v):
        if not functions.is_mac_address(v):
            raise ValueError("Invalid MAC address.")
        return v

    @validator('port')
    def port_range(cls, v):
        if v not in range(1, 65536):
            raise ValueError("Invalid TCP Port. It must be an integer between 1 and 65535.")
        return v

    def ping(self):
        res = ping(self.ip_address, unit='ms')
        if res is False:
            return 'error'
        if res is None:
            return 'timeout'
        return res

    def __str__(self):
        return self.name
