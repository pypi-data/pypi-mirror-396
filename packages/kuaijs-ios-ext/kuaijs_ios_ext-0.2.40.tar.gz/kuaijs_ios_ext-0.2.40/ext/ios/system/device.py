from kuaijs import device


def get_device_id():
    return device.getServerDeviceId()


def get_device_name():
    return device.getDeviceName()


def get_device_model():
    return device.getDeviceModel()


def get_screen_size():
    return device.getScreenRealSize()


def get_screen_scale():
    return device.getScreenScale()


def get_orientation():
    return device.getOrientation()


def get_battery_info():
    return device.getBatteryInfo()


# duration 毫秒单位
# intensity 0~1 强度，小数
def vibrate(duration, intensity=0.5):
    device.vibrate(duration, intensity)
