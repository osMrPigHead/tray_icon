import ctypes
import importlib
import os
import sys
from pathlib import Path

import psutil
from PyQt5.QtWidgets import QApplication, QMenu, QMessageBox, QSystemTrayIcon

from application import *
from utils import *


def about():
    noicon_dialog("托盘快捷操作", "托盘快捷操作\nBy osMrPigHead\n2024.08.09", ICON())


def error_when_launch(*_, **__):
    critical_dialog("错误", "启动失败\n请检查配置", ICON())
    sys.exit(1)


def error_when_reload(self: "MainApplication"):
    critical_dialog("错误", "重新加载失败\n请检查配置", ICON())
    self.menu.clear()
    self.applications = [self.basic_application]
    self.build(self.menu)


class MainApplication(MultiApplication):
    @catch_error(error_when_launch)
    def __init__(self, app: QApplication):
        import settings
        self.settings = settings
        self.basic_application = BasicApplication(self, app)
        super().__init__(settings.APPLICATION_ENABLED + [self.basic_application])
        for service in settings.SERVICES_ENABLED:
            thread = service(app)
            thread.daemon = True
            thread.start()

    def build(self, menu: QMenu):
        menu.addAction("托盘快捷操作").setDisabled(True)
        menu.addAction("By osMrPigHead").setDisabled(True)
        menu.addAction("2024.08.09").setDisabled(True)
        menu.addSeparator()
        super().build(menu)

    @catch_error(error_when_launch)
    def load(self, menu: QMenu):
        self.menu = menu
        self.build(menu)

    @catch_error(error_when_reload)
    def reload(self):
        self.menu.clear()
        importlib.reload(self.settings)
        self.applications = self.settings.APPLICATION_ENABLED + [self.basic_application]
        self.build(self.menu)
        info_dialog("成功", "已重新加载面板", ICON())


class BasicApplication(MultiApplication):
    def __init__(self, main_application: MainApplication, app: QApplication):
        super().__init__([
            single_application_object(SingleApplication, "关于",
                                      lambda _: about()),
            single_application_object(SingleApplication, "重新加载面板",
                                      lambda _: main_application.reload()),
            single_application_object(SingleApplication, "重新启动程序",
                                      lambda _: os.execv(
                                          psutil.Process().exe(),
                                          psutil.Process().cmdline()
                                      )),
            single_application_object(SingleApplication, "退出",
                                      lambda _: app.quit())
        ])


class TrayIcon(QSystemTrayIcon):
    def __init__(self, app: QApplication):
        super().__init__(ICON(), app)
        menu = QMenu()
        self.setContextMenu(menu)
        self.main_application = MainApplication(app)
        self.main_application.load(menu)
        self.activated.connect(lambda reason: about() if reason != self.Context else None)

    def startup_message(self):
        self.showMessage("托盘快捷操作 已启动", "在系统托盘查看详情", ICON())


def main(argv):
    app = QApplication(argv)
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("osmrpighead.tray_icon")
    app.setQuitOnLastWindowClosed(False)

    tray = TrayIcon(app)
    tray.show()
    tray.startup_message()

    return app.exec_()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
