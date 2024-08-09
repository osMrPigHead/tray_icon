__all__ = [
    "application_error",
    "Service", "Application",
    "SingleApplication", "OptionApplication",
    "MenuApplication", "RadioApplication",
    "MultiApplication",
    "build_service", "application_object",
    "single_application_object", "option_application_object", "radio_application_object"
]

from abc import ABC, abstractmethod
from threading import Thread
from typing import Callable, Iterable, Type, TypeVar, Any

from PyQt5.QtWidgets import QApplication, QMenu

from utils import *


def application_error(title):
    def handler():
        critical_dialog("错误", f"发生错误：{title}", ICON())
    return handler


class Service(Thread):
    def __init__(self, app: QApplication):
        super().__init__()
        self.app = app


class Application(ABC):
    title: str = "Application"
    @abstractmethod
    def build(self, menu: QMenu): ...


class SingleApplication(Application, ABC):
    def build(self, menu: QMenu):
        self.action = menu.addAction(self.title)
        self.action.triggered.connect(
            catch_error_no_params(application_error(self.title))(self.main)
        )

    @abstractmethod
    def main(self): ...


class OptionApplication(SingleApplication, ABC):
    default: bool = False

    def main(self):
        if self.action.isChecked():
            self.enabled()
        else:
            self.disabled()

    def enable(self):
        self.action.setChecked(True)
        self.enabled()

    def disable(self):
        self.action.setChecked(False)
        self.disabled()

    def toggle(self):
        self.set(not self.get())

    def set(self, value: bool):
        if value:
            self.enable()
        else:
            self.disable()

    def get(self):
        return self.action.isChecked()

    def build(self, menu: QMenu):
        super().build(menu)
        self.action.setCheckable(True)
        self.action.setChecked(self.default)

    @abstractmethod
    def enabled(self): ...
    @abstractmethod
    def disabled(self): ...


class ValuedOptionApplication(OptionApplication, ABC):
    value: Any = None


class MenuApplication(Application):
    def __init__(self, applications: Iterable[Application]):
        self.applications = list(applications)

    def build(self, menu: QMenu):
        self.sub_menu = menu.addMenu(self.title)
        for application in self.applications:
            application.build(self.sub_menu)

    def reload(self):
        self.sub_menu.clear()
        for application in self.applications:
            application.build(self.sub_menu)


class SelectableApplication(MenuApplication):
    def disable_all(self):
        for application in self.applications:
            if isinstance(application, OptionApplication):
                application.disable()
            if isinstance(application, SelectableApplication):
                application.disable_all()

    def select_by_value(self, value):
        for application in self.applications:
            if isinstance(application, ValuedOptionApplication):
                if application.value == value:
                    application.action.setChecked(True)
                else:
                    application.action.setChecked(False)
            if isinstance(application, SelectableApplication):
                application.select_by_value(value)


class RadioApplication(SelectableApplication, ABC):
    ITEM = 0
    FOLDER = 1

    def __init__(self, options):
        self.options = options
        super().__init__(self.build_applications(options))

    def build_applications(self, options: Iterable) \
            -> Iterable[Application]:
        build_applications, disable_all, main = self.build_applications, self.disable_all, self.main
        for option in options:
            assert (isinstance(option, tuple) and len(option) == 3 and
                    isinstance(option[0], str) and option[1] in [self.ITEM, self.FOLDER])
            if option[1] == self.ITEM:
                class Option(ValuedOptionApplication):
                    title = option[0]
                    value = option[2]

                    def enabled(self):
                        disable_all()
                        self.action.setChecked(True)
                        main(self.value)

                    def disabled(self): pass
                yield Option()
                continue
            assert isinstance(option[2], Iterable)
            yield application_object(
                SelectableApplication, option[0],
                build_applications(option[2])
            )

    def reload(self):
        self.applications = self.build_applications(self.options)
        super().reload()

    @abstractmethod
    def main(self, value): ...


class MultiApplication(Application):
    def __init__(self, applications: Iterable[Application]):
        self.applications = applications

    def build(self, menu: QMenu):
        menu.addSeparator()
        for application in self.applications:
            application.build(menu)
        menu.addSeparator()


APPLICATION = TypeVar("APPLICATION", bound=Application)
SINGLE_APPLICATION = TypeVar("SINGLE_APPLICATION", bound=SingleApplication)
OPTION_APPLICATION = TypeVar("OPTION_APPLICATION", bound=OptionApplication)
RADIO_APPLICATION = TypeVar("RADIO_APPLICATION", bound=RadioApplication)


def build_service(run: Callable[[Service], Any]) -> Type[Service]:
    class ServiceObject(Service):
        def run(self):
            run(self)
    return ServiceObject


def application_object(
        base: Type[APPLICATION],
        title_: str,
        *args,
        **kwargs
) -> APPLICATION:
    class ApplicationObject(base):
        title = title_

        def __init__(self):
            super().__init__(*args, **kwargs)
    return ApplicationObject()


def single_application_object(
        base: Type[SINGLE_APPLICATION],
        title_: str,
        main: Callable[[SINGLE_APPLICATION], Any]
) -> SINGLE_APPLICATION:
    class ApplicationObject(base):
        title = title_

        def main(self):
            main(self)
    return ApplicationObject()


def option_application_object(
        base: Type[OPTION_APPLICATION],
        title_: str,
        enabled: Callable[[OptionApplication], Any],
        disabled: Callable[[OptionApplication], Any]
) -> OPTION_APPLICATION:
    class ApplicationObject(base):
        title = title_
        
        def enabled(self):
            enabled(self)
        
        def disabled(self):
            disabled(self)
    return ApplicationObject()


def radio_application_object(
        base: Type[RADIO_APPLICATION],
        title_: str,
        main: Callable[[RADIO_APPLICATION, Any], Any],
        options: Iterable
) -> RADIO_APPLICATION:
    class ApplicationObject(base):
        title = title_

        def main(self, value):
            main(self, value)
    return ApplicationObject(options)
