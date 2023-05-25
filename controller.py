import pyautogui
import time


def press_button(button, n_times=1):
    for num in range(n_times):
        pyautogui.keyDown(button)
        pyautogui.keyUp(button)
        time.sleep(0.1)


def press_up(n_times=1):
    press_button("up", n_times)


def press_down(n_times=1):
    press_button("down", n_times)


def press_left(n_times=1):
    press_button("left", n_times)


def press_right(n_times=1):
    press_button("right", n_times)


def press_a(n_times=1):
    press_button("x", n_times)


def press_b(n_times=1):
    press_button("z", n_times)


def press_l(n_times=1):
    press_button("a", n_times)


def press_r(n_times=1):
    press_button("s")


def press_sel(n_times=1):
    press_button("backspace")


def press_start(n_times=1):
    press_button("return")

# Helper function that allows the bot to easily select the next character.
# Press L will highlight the next unit, and press a will select them


def next_unit():
    press_l()
    press_a()

# Each attack requires 3 a presses. One to confirm an attack. One to select a weapon.
# one to select an enemy. This function will not stay in this form.


def attack():
    press_a(3)

# end move function. pressing up at the start of menuing will always bring you to the bottom of
# the menu provided no inputs get eaten


def end_move():
    press_up()
    press_a()
