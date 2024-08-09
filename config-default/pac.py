__all__ = [
    "HOST", "PORT",
    "DEFAULT_ENABLED", "DEFAULT_PROXY",
    "PAC_DISABLED", "PAC_ENABLED",
    "REG_HKEY", "REG_SUB_KEY", "REG_PAC", "REG_PROXY_ENABLE",
    "PROXIES"
]

import winreg

from modules.pac_config import *
from utils import *

HOST = "127.0.0.1"
PORT = 38326
DEFAULT_ENABLED = False
PAC_DISABLED = CONFIG / "pac" / "disabled.js"
PAC_ENABLED = CONFIG / "pac" / "enabled.js"

REG_HKEY = winreg.HKEY_CURRENT_USER
REG_SUB_KEY = R"SOFTWARE\Microsoft\Windows\CurrentVersion\Internet Settings"
REG_PAC = "AutoConfigURL"
REG_PROXY_ENABLE = "ProxyEnable"

DIRECT = Proxy("DIRECT")
LOCAL38325 = Proxy("PROXY 127.0.0.1:38325")

PROXIES = [
    Scheme("直连", Rule("*", DIRECT)),
    Scheme("代理",
           Rule(["*.baidu.com", "baidu.com"], DIRECT),
           Rule("*", [LOCAL38325, DIRECT])),
    ("文件夹", [
        Scheme("文件夹内的代理", Rule("*", [LOCAL38325, DIRECT]))
    ])
]

DEFAULT_PROXY = PROXIES[0]
