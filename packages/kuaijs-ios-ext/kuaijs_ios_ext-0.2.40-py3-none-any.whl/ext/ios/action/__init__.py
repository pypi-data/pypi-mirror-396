from kuaijs import action

KEY_HOME = "home"
KEY_VOLUMEUP = "volumeup"
KEY_volumedown = "volumedown"
KEY_POWER = "power"
KEY_SNAPSHOT = "snapshot"
KEY_POWER_AND_HOME = "power_plus_home"


def click(x, y: int = 0, duration: float = 20):
    action.click(x, y, duration)


def double_tap(x: int, y: int):
    action.doubleClick(x, y)


def slide(x1: int, y1: int, x2: int, y2: int, duration: float = 200):
    action.swipe(x1, y1, x2, y2, duration)


def touch_and_slide(
    from_x: int,
    from_y: int,
    to_x: int,
    to_y: int,
    touch_down_duration: int = 500,
    touch_move_duration: int = 1000,
    touch_up_duration: int = 500,
):
    action.pressAndSwipe(
        from_x,
        from_y,
        to_x,
        to_y,
        touch_down_duration,
        touch_move_duration,
        touch_up_duration,
    )


def input(value):
    action.input(value)


def home():
    action.homeScreen()


def keys(value):
    action.input(value)


def key_press(key):
    action.pressButton(key)


def key_press_hid(key, duration: int = 20):
    action.pressHidButton(key, duration)
