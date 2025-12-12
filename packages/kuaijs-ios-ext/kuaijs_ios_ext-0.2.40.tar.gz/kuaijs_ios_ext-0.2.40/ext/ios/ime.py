from kuaijs import ime


def input_text(text: str):
    ime.input(text)


def input_clear():
    ime.clearText()


def input_enter():
    ime.pressEnter()
