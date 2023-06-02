import pyautogui
import controller
import time
import sockettest
from unit import Unit
import csv
# Moving the mouse onto the emulator and testing extremely basic movement options.
itemList = []
physWeaponList = []
magWeaponList = []
staffList = []
classList = []
commandList = ["getUnits", "getEnemies",
               "getMoney", "getMapSize", "getMap", "getIsPlayerPhase"]
#               id: name, Def Bonus, Avoid Bonus, Hp Recovery, Infantry A, Infantry B, Brigand, Pirate, Bereserker, Mages, Armor, Cav A, Cav B, Nomad, Nomad Trooper, Flier, Dragon
# Create a second dictionary corresponding to ids, to allow for similar objects to share the same dictionary.
# For example, (key ->)01:(value ->)01, 02:01 (02 is a road tile, which has the exact same stats as plain (01))


# 04 - Closed Village (Blocked), 1F - Throne

# note: Throne gets +5 Res
terrainKey = {"01": "01", "02": "01", "13": "01", "17": "01",  # 01 - Plains, 02 - Road, 13 - Bridge, 17 - Floor,
              # 19 - Obstacle, 2E - Roof, 26 - Cliff (need to check its not impassable)
              "19": "19", "2E": "19", "26": "19",
              "0C": "0C",  # 0C - Forest,
              "11": "11",  # 11 - Mountain,
              "12": "12",  # 12 - Peak,
              "23": "23",  # 23 - Gate,
              "05": "05", "03": "05", "06": "05",  # 05 - House, 03 - Village, 06 - Shop
              "10": "10",  # 10 - River
              "16": "16",  # 16 - Lake
              "25": "25",  # 25 - Ruins (Village)
              "1F": "1F",  # 1F - Throne
              "0A": "0A",  # 0A - Fort
              "04": "04", "1A": "04", "3F": "04", "1E": "04", "1B": "04"}  # 04 - Closed Village, 1A - Wall, 3F - Brace, 1E - Door (need to check door + brace), 1B - Breakable Wall
#
# terrainInfo = {"01": ["Plain", 0, 0, 0, 1,
#                     1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], }


def openItemFile(filename):
    with open(filename, "rt") as f:
        lines = [line.strip().split(', ') for line in f]
    return lines

# unfinished open csv for terrain data


def openCSV(filename):
    with open(filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimeter=',')
        rows = {}
    return rows


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
    time.sleep(1)


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
    # moveAction - "nothing", "attack", "useItem(itemPos)", "heal(unit)", "dance(unit)"
    moveAction = "attack"
    return moveX, moveY, moveAction


def findNearestEnemy(currUnit, enemyList):
    unitX = currUnit.xpos
    unitY = currUnit.ypos

# Alternative to going unit by unit - Calculate the absolute best move out of all units, execute it (swapping to the right unit using L+A),
# then repeating with the remaining units until all moves are done.
# Note: This might be slow. Will do the naive approach first (Just go unit-by-unit, find their best move, then go to the next one)

# Does not care about map information at all. Only goal is to move units to nearest enemies and kill them, and heal if hp < half maxHp

# Need to figure out map stuff before I can actually use this


def basicMoveAlgorithm(currUnit, unitList, enemyList):
    unitX = currUnit.xpos
    unitY = currUnit.ypos
    itemPos = currUnit.getHealingItem()
    enemy = findNearestEnemy(currUnit, enemyList)
    if abs(unitX - enemy.xpos) + abs(unitY-enemy.ypos) < currUnit.trueMove:
        moveX = unitX

    if currUnit.currHP < (currUnit.maxHP/2) and itemPos < 5:
        moveAction = "useItem"


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


def createMoveMap(mapData):
    currLine = line.strip().lower().split(', ')
    lines[currLine[0]] = currLine[1:]


def main():
    global commandList
    fillItemLists()
    # print("Items: " + str(itemList))
    # print("Physical Weapons: " + str(physWeaponList))
    # print("Magic Weapons: " + str(magWeaponList))
    # print("Staves: " + str(staffList))

    # pyautogui.moveTo(7, 80, 0.2)
    # pyautogui.click()

    # mapsize = list(sockettest.main(commandList[3]))

    # if a map has a width of 10, then the tiles go from 0-9
    # mapxlength = mapsize[1] + mapsize[0]
    # mapylength = mapsize[3] + mapsize[2]

    # print(mapxlength)
    # print(mapylength)

    # unitData = sockettest.main(commandList[0])
    # enemyData = sockettest.main(commandList[1])
    # money = int(sockettest.main(commandList[2]))
    mapData = sockettest.main(commandList[4])
    mapList = list(mapData)
    print(mapList)
    # print(mapList[20])
    # isPlayerPhase = sockettest.main(commandList[5]).decode('utf-8')
    # map stuff seems hard ;-;
    # might be better to store map in memory? Rather than pull it every turn?
    # print(mapsize)
    # print(isPlayerPhase)
    # if isPlayerPhase == 'T':
    #    print("It's your turn")
    # else:
    #    print("Not your turn")
    # unitList = storeUnits(unitData)
    # enemyList = storeUnits(enemyData)

    # need to figure out map stuff before I can create main loop
    """while isPlayerPhase == 'T':
        for units in unitList:
            if not units.hasMoved:
                moveX, moveY, moveAction = decideMove(
                    units, unitList, enemyList)
                moveTo(units.xpos, units.ypos, moveX, moveY)
"""
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
