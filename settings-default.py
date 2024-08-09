import importlib
from types import ModuleType
from typing import Type

from application import Application, Service
from modules import pac, my_files, quick_start

MODULES_ENABLED: list[ModuleType] = [
    pac, my_files, quick_start
]

for module in MODULES_ENABLED:
    importlib.reload(module)

APPLICATION_ENABLED: list[Application] = [
    pac.ProxyApplication,
    my_files.MyFilesApplication,
    quick_start.QuickStartApplication
]
SERVICES_ENABLED: list[Type[Service]] = [
    pac.Server
]
