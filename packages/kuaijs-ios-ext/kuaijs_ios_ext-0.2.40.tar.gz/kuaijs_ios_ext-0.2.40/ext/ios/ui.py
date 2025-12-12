from kuaijs import pip, ui


class WebWindow:

    def __init__(self, ui_path: str, tunner=None):
        ui.onEvent(tunner)

    def show(self):
        ui.show()

    def call(self, script: str):
        ui.eval(script)

    def close(self):
        print("不支持的方法[close]")


class FloatWindow:
    @staticmethod
    def hidden():
        pip.closeLogWindow()

    @staticmethod
    def hide():
        pip.closeLogWindow()

    @staticmethod
    def show():
        pip.showLogWindow()
