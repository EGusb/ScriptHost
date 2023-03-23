import functions

from time import sleep
from pydantic import BaseModel, validator
from ping3 import ping


class CommandTemplate(BaseModel):
    """Represents the template of a command to be sent to a host."""

    cmd_template: str
    "The command template that has parameters that later will be replaced by actual values."

    wait_after = 0
    "The time in milliseconds that the host must wait after executing this command."

    params: list[str] = []
    "The list of parameter names to be replaced in the template."

    def get_cmd(self, kwargs: dict, wait_after: int = 0) -> tuple:
        """
        Replaces all the parameters sent as arguments in the command template to get the full command with values

        :param kwargs: A dictionary containing the parameters to replace and their values
        :param wait_after: The time in milliseconds that the host should wait after executing this command.
        :returns: A tuple containing the final command as the first arg, and the time to wait in ms as second arg.
        Returns None if there is an error.
        """
        params = self.dict().get('params', [])
        template = self.dict().get('cmd_template', '')
        wait_after = wait_after or self.dict().get('wait_after', 0)

        for param in params:
            if param in kwargs:
                template = template.replace(param, f"{kwargs[param]}")
            else:
                raise KeyError(f"Parameter '{param}' must be provided.")

        return template, wait_after


class Script(BaseModel):
    """Represents a set of command templates to be executed in order by the host."""

    name: str
    "The name for the script."

    commands: list[CommandTemplate] = []
    "The list of command templates to be executed."

    def get_cmds(self, kwargs: dict) -> tuple:
        """
        Replaces all the parameters sent as arguments in each of the command templates.
        :param kwargs: A dictionary containing the parameters to replace and their values.
        :return: A generator with the finished commands.
        """
        cmd_templates = self.dict().get('commands', [])

        for dic in cmd_templates:
            cmd = CommandTemplate(**dic)
            cmd_str, wait = cmd.get_cmd(kwargs)
            yield cmd_str
            sleep(wait / 1000)

    def __str__(self):
        return self.name


class Host(BaseModel):
    name: str
    ip_address: str
    mac_address = ''
    scripts: list[Script] = []

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

    def ping(self):
        res = ping(self.ip_address, unit='ms')
        if res is False:
            return 'error'
        if res is None:
            return 'timeout'
        return res

    def __str__(self):
        return f"{self.name} ({self.ip_address})"
