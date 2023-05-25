import pyautogui
import controller
import time
# Moving the mouse onto the emulator and testing extremely basic movement options.


def main():
    pyautogui.moveTo(7, 80, 0.2)
    pyautogui.click()
    controller.next_unit()
    # controller.press_left(5)
    # controller.press_a()

    # needs a buffer for attack animations.
    # time.sleep(2)

    controller.press_up()

    # attacking requires 3 a presses. One to select the attack option, one to select the weapon, one to select the enemy.
    controller.press_a(3)

    controller.press_up()
    controller.press_a()
    # controller.press_down(5)
    # controller.press_up(4)
    # controller.press_left(2)
    # controller.press_right(3)
    # controller.press_l(2)
    # controller.press_r(1)
    # controller.press_a(2)
    # controller.press_b(2)
    # controller.press_start(2)
    # controller.press_sel()
    # press_button("x")
    # press_button("down", 20)

# basic press_button function.  I don't forsee a need to hold down the buttons at all,
# so will likely use this function to control all interaction with the game
# def press_button(button, n_times = 1):
 #   for num in range(n_times):
  #      pyautogui.keyDown(button)
   #     pyautogui.keyUp(button)


main()
