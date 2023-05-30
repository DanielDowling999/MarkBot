import pyautogui
import controller
import time
import sockettest
from unit import Unit
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


def moveTo(startX, startY, endX, endY):
    moveX = endX-startX
    moveY = endY-startY
    if (moveX < 0):
        controller.press_left(abs(moveX))
    elif (moveX > 0):
        controller.press_right(moveX)
    if (moveY < 0):
        controller.press_up(abs(moveY))
    elif (moveY > 0):
        controller.press_down(moveY)
    controller.press_a()


def enemyInRange(currUnit, enemyList):
    enemiesInRange = []
    unitX = currUnit.xpos
    unitY = currUnit.ypos
    for enemy in enemyList:
        if (abs(unitX - enemy.xpos) + abs(unitY-enemy.ypos) < 5):
            enemiesInRange.append(enemy)

    return enemiesInRange


def main():
    fillItemLists()
    # print("Items: " + str(itemList))
    # print("Physical Weapons: " + str(physWeaponList))
    # print("Magic Weapons: " + str(magWeaponList))
    # print("Staves: " + str(staffList))

    pyautogui.moveTo(7, 80, 0.2)
    pyautogui.click()
    unitList, enemyList = sockettest.main()
    controller.next_unit()
    unitX = unitList[0].xpos
    unitY = unitList[0].ypos
    enemiesInRange = enemyInRange(unitList[0], enemyList)
    if not enemiesInRange:
        moveTo(unitX, unitY, unitX-3, unitY-2)
        time.sleep(1)
        controller.end_move()

    else:
        moveTo(unitX, unitY,
               enemiesInRange[0].xpos+1, enemiesInRange[0].ypos)
        time.sleep(1)
        controller.attack()

    # lyn moved to 0c 05
    # needs a buffer for attack animations.
    # time.sleep(2)

    # controller.press_up()

    # attacking requires 3 a presses. One to select the attack option, one to select the weapon, one to select the enemy.
    # controller.press_a(3)

    # controller.press_up()
    # controller.press_a()


main()
