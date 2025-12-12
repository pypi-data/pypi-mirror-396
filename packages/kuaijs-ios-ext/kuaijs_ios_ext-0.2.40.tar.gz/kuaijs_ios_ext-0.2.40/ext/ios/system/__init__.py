import os.path
import typing
from kuaijs import system, device, config, file, g


class R:
    @staticmethod
    def home():
        return file.getInternalDir("documents")

    @staticmethod
    def root():
        return ""

    @staticmethod
    def name():
        return g.packageJson.get("name", "")

    @staticmethod
    def res(child: str = None):
        return os.path.join(child)

    @staticmethod
    def img(child: str = None):
        return os.path.join("img", child)

    @staticmethod
    def ui(child: str = None):
        return os.path.join(child)


def get_uuid():
    return device.getServerDeviceId()


def get_ios_version():
    return device.getOSVersion()


def app_start(
    bundle_id: str,
    arguments: typing.List[str] = [],
    environment: typing.Dict[str, str] = {},
):
    return system.startApp(bundle_id, arguments, environment)


def scheme_start(scheme: str):
    return system.openURL(scheme)


def app_stop(bundle_id: str):
    return system.stopApp(bundle_id)


def app_current():
    return system.activateApp()


def open_url(url: str):
    return system.openURL(url)


def is_locked():
    return system.isLocked()


def lock():
    return system.lock()


def unlock():
    return system.unlock()


def set_clipboard(content: str):
    return system.setClipboard(content)


def get_clipboard() -> str:
    return system.getClipboard()


def screen_size():
    return device.getScreenRealSize()


def screen_orientation():
    return device.getOrientation()


def notify(msg: str, title: str = None, _id: str = "9800"):
    system.notify(msg, title, _id)


class KeyValue:
    @staticmethod
    def save(key: str, value):
        config.updateConfig(key, value)

    @staticmethod
    def get(key: str, default=None):
        allConfig = config.getConfigJSON()
        res = allConfig.get(key, default)
        return res
