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
