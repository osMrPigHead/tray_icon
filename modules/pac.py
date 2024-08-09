__all__ = [
    "ProxyApplication",
    "Server"
]

import atexit
import importlib
import time
import winreg
from typing import Iterable, Optional
from wsgiref.simple_server import make_server

from application import *
from config import pac as config
from modules.pac_config import *


def flush_windows_pac(enabled: bool):
    key = winreg.OpenKey(config.REG_HKEY, config.REG_SUB_KEY, 0, winreg.KEY_ALL_ACCESS)
    if enabled:
        winreg.SetValueEx(key, config.REG_PAC, 0, winreg.REG_SZ,
                          f"http://{config.HOST}:{config.PORT}/?t={int(time.time())}")
    else:
        try:
            winreg.DeleteValue(key, config.REG_PAC)
        except FileNotFoundError:
            pass
    winreg.SetValueEx(key, config.REG_PROXY_ENABLE, 0, winreg.REG_DWORD, 0)
    winreg.CloseKey(key)


def set_proxy_state(enabled: bool):
    global pac, pac_len
    if enabled:
        pac = b"var rules = " + selected_proxy.jsonify() + b"\n" + enabled_template
    else:
        pac = disabled_template
    pac_len = str(len(pac))
    flush_windows_pac(enabled)


with config.PAC_DISABLED.open("rb") as fr_d, config.PAC_ENABLED.open("rb") as fr_e:
    disabled_template = fr_d.read()
    enabled_template = fr_e.read()
selected_proxy = config.DEFAULT_PROXY
pac: bytes
pac_len: str
set_proxy_state(config.DEFAULT_ENABLED)

atexit.register(lambda: flush_windows_pac(False))


def get_proxy_options(proxies: Optional[list] = None) -> Iterable:
    if proxies is None:
        proxies = config.PROXIES
    for proxy in proxies:
        if isinstance(proxy, Scheme):
            yield proxy.title, RadioApplication.ITEM, proxy
        else:
            assert (isinstance(proxy, tuple) and len(proxy) == 2 and
                    isinstance(proxy[0], str) and isinstance(proxy[1], Iterable))
            yield proxy[0], RadioApplication.FOLDER, get_proxy_options(proxy[1])


def update_select_options():
    importlib.reload(config)
    Select.options = get_proxy_options()
    Select.reload()


def select_proxy(proxy: Scheme):
    global selected_proxy
    selected_proxy = proxy
    Enable.enable()
    set_proxy_state(True)


def server(environ, start_response):
    start_response("200 OK", [("Content-Length", pac_len)])
    return [pac]


Server = build_service(lambda _: make_server(config.HOST, config.PORT, server).serve_forever())

Enable = option_application_object(
    OptionApplication, "代理",
    lambda _: (set_proxy_state(True), Select.select_by_value(selected_proxy)),
    lambda _: (set_proxy_state(False), Select.disable_all())
)
Reload = single_application_object(
    SingleApplication, "重新加载代理配置",
    lambda _: update_select_options()
)
Flush = single_application_object(
    SingleApplication, "刷新 Windows 代理配置",
    lambda _: flush_windows_pac(Enable.get())
)
Select = radio_application_object(
    RadioApplication, "选择代理配置",
    lambda _, value: select_proxy(value), get_proxy_options()
)

ProxyApplication = application_object(
    MultiApplication, "代理",
    [Enable, Reload, Flush, Select]
)
