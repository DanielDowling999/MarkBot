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
classList = []
commandList = ["getUnits", "getEnemies",
               "getMoney", "getMap", "getIsPlayerPhase"]


def openItemFile(filename):
    with open(filename, "rt") as f:
        lines = [line.strip().split(', ') for line in f]
    return lines


def fillItemLists():
    global itemList
    global physWeaponList
    global magWeaponList
    global staffList
    global classList
    itemList = openItemFile("Data/items.txt")
    physWeaponList = openItemFile("Data/physWeapons.txt")
    magWeaponList = openItemFile("Data/magWeapons.txt")
    staffList = openItemFile("Data/staves.txt")
    classList = openItemFile("Data/class.txt")


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
        if (abs(unitX - enemy.xpos) + abs(unitY-enemy.ypos) < currUnit.trueMove):
            enemiesInRange.append(enemy)

    return enemiesInRange


def decideMove(currUnit, unitList, enemyList):
    # unit list is passed for units that can heal, and potentially for trading possibilities, finding 'safe' moves, dancing, and the like
    unitX = currUnit.xpos
    unitY = currUnit.ypos
    enemiesInRange = enemyInRange(currUnit, enemyList)
    if not enemiesInRange:
        moveX = 0
        moveY = 0

    return moveX, moveY

# Alternative to going unit by unit - Calculate the absolute best move out of all units, execute it (swapping to the right unit using L+A),
# then repeating with the remaining units until all moves are done.
# Note: This might be slow. Will do the naive approach first (Just go unit-by-unit, find their best move, then go to the next one)


def storeUnits(unitData):
    numUnits = int(len(unitData)/72)
    unitList = []
    startAddress = 0
    endAddress = 72
    for x in range(numUnits):
        unitList.append(Unit(unitData[startAddress:endAddress]))
        startAddress = endAddress
        endAddress += 72
    return unitList


def getUnitData(data):
    unitData = list(data)
    unitList = storeUnits(unitData)
    return unitList


def getEnemyData(data):
    enemyData = list(data)
    enemyList = storeUnits(enemyData)
    return enemyList


def main():
    global commandList
    fillItemLists()
    # print("Items: " + str(itemList))
    # print("Physical Weapons: " + str(physWeaponList))
    # print("Magic Weapons: " + str(magWeaponList))
    # print("Staves: " + str(staffList))

    # pyautogui.moveTo(7, 80, 0.2)
    # pyautogui.click()
    # , enemyList = sockettest.main()
    unitData = sockettest.main(commandList[0])
    enemyData = sockettest.main(commandList[1])
    money = int(sockettest.main(commandList[2]))
    isPlayerPhase = sockettest.main(commandList[4]).decode('utf-8')

    # print(isPlayerPhase)
    # if isPlayerPhase == 'T':
    #    print("It's your turn")
    # else:
    #    print("Not your turn")
    unitList = storeUnits(unitData)
    enemyList = storeUnits(enemyData)
    # moveList = []
    # for units in unitList:
    #    units.printUnitInformation()
    # for enemies in enemyList:
    #    enemies.printUnitInformation()
    # print(money)
    # print(unitList)
    # print(enemyList)
    # print(money)
    """for currUnit in unitList:
        moveList.append(decideMove())
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
        controller.attack()"""
    # for units in unitList:

    # Test for making sure the class data is generated correctly
    # unitId = units.id
    # print("This unit is: " + unitId)
    # print(unitId + " is in the class corresponding to: " + units.classId)
    # print(units.classId + " is the " + units.className + " class")
    # print(units.className + " has " + units.classCon + " con, " +
    #      units.classMove + " move, " + units.classMoveType + " move type")
    # print("So " + unitId + " has " + str(units.trueMove) +
    #      " move and " + str(units.trueCon) + " constitution")

    # lyn moved to 0c 05
    # needs a buffer for attack animations.
    # time.sleep(2)

    # controller.press_up()

    # attacking requires 3 a presses. One to select the attack option, one to select the weapon, one to select the enemy.
    # controller.press_a(3)

    # controller.press_up()
    # controller.press_a()


main()
