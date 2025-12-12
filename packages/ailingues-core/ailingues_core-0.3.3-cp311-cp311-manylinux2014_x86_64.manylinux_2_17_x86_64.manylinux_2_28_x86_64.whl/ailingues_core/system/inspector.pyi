from ailingues_core.system.cpu import CPUInfo as CPUInfo
from ailingues_core.system.mainboard import MainboardInfo as MainboardInfo
from ailingues_core.system.netadapter import NetAdapterInfo as NetAdapterInfo
from ailingues_core.system.osinfo import OSInfo as OSInfo
from typing import Any

class SystemInfo:
    def __init__(self, include_virtual: bool = False, include_loopback: bool = False, only_up: bool = True, require_ip: bool = False, prefer_non_laa: bool = True) -> None: ...
    def get_data(self) -> dict[str, Any]: ...
