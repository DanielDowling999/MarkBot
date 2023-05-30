import pyautogui
import controller
import time
# Moving the mouse onto the emulator and testing extremely basic movement options.
itemList = []
physWeaponList = []
magWeaponList = []
staffList = []


def openItemFile(filename):
    with open(filename, "rt") as f:
        lines = [line.strip().split(', ') for line in f]
    return lines


def fillItemLists():
    global itemList
    global physWeaponList
    global magWeaponList
    global staffList
    itemList = openItemFile("Data/items.txt")
    physWeaponList = openItemFile("Data/physWeapons.txt")
    magWeaponList = openItemFile("Data/magWeapons.txt")
    staffList = openItemFile("Data/staves.txt")


def main():
    fillItemLists()
    # print("Items: " + str(itemList))
    # print("Physical Weapons: " + str(physWeaponList))
    # print("Magic Weapons: " + str(magWeaponList))
    # print("Staves: " + str(staffList))

    # pyautogui.moveTo(7, 80, 0.2)
    # pyautogui.click()
    # controller.next_unit()

    # needs a buffer for attack animations.
    # time.sleep(2)

    # controller.press_up()

    # attacking requires 3 a presses. One to select the attack option, one to select the weapon, one to select the enemy.
    # controller.press_a(3)

    # controller.press_up()
    # controller.press_a()


main()
