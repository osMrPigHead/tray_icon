__all__ = [
    "QuickStartApplication"
]

import importlib
import os

from application import *
from config import quick_start as config


def reload():
    importlib.reload(config)
    Main.options = config.CONFIGURATIONS
    Main.reload()


Main = radio_application_object(
    RadioApplication, "快速运行",
    lambda self, value: (os.startfile(value), self.disable_all()), config.CONFIGURATIONS
)
Reload = single_application_object(
    SingleApplication, "重新加载快速运行配置",
    lambda _: reload
)

QuickStartApplication = application_object(
    MultiApplication, "快速运行",
    [Main, Reload]
)
