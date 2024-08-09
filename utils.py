__all__ = [
    "ROOT", "MODULE", "CONFIG",
    "q_icon", "ICON",
    "noicon_dialog", "info_dialog", "warning_dialog", "critical_dialog",
    "catch_error", "catch_error_no_params"
]

import functools
from pathlib import Path

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMessageBox

ROOT = Path(__file__).parent
MODULE = ROOT / "modules"
CONFIG = ROOT / "config"

DEBUG = True


def q_icon(path: Path):
    return QIcon(str(path))


def ICON():
    return q_icon(ROOT / "icon.png")


def show_dialog(title, text, window_icon, icon, ok_text):
    dialog = QMessageBox()
    dialog.setIcon(icon)
    dialog.setWindowIcon(window_icon)
    dialog.setWindowTitle(title)
    dialog.setText(text)
    dialog.addButton(ok_text, dialog.YesRole)
    dialog.show()
    dialog.exec_()


def noicon_dialog(title, text, window_icon, ok_text="彳亍"):
    show_dialog(title, text, window_icon, QMessageBox.NoIcon, ok_text)


def info_dialog(title, text, window_icon, ok_text="彳亍"):
    show_dialog(title, text, window_icon, QMessageBox.Information, ok_text)


def warning_dialog(title, text, window_icon, ok_text="OK 了解"):
    show_dialog(title, text, window_icon, QMessageBox.Warning, ok_text)


def critical_dialog(title, text, window_icon, ok_text="女子口巴"):
    show_dialog(title, text, window_icon, QMessageBox.Critical, ok_text)


def catch_error(handler):
    def catch_error_(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except:
                handler(*args, **kwargs)
        if DEBUG:
            return func
        return wrapper
    return catch_error_


def catch_error_no_params(handler):
    def catch_error_(func):
        @functools.wraps(func)
        def wrapper():
            try:
                return func()
            except:
                handler()
        if DEBUG:
            return func
        return wrapper
    return catch_error_
