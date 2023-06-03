import pyautogui
import controller
import time
import sockettest
from unit import Unit
import csv
import numpy
# Moving the mouse onto the emulator and testing extremely basic movement options.
itemList = []
physWeaponList = []
magWeaponList = []
staffList = []
classList = []
terrainDictionary = {}  # id: name, Def Bonus, Avoid Bonus, Hp Recovery, Infantry A, Infantry B, Brigand, Pirate, Bereserker, Mages, Armor, Cav A, Cav B, Nomad, Nomad Trooper, Flier, Dragon

commandList = ["getUnits", "getEnemies",
               "getMoney", "getMapSize", "getMap", "getIsPlayerPhase"]
# Create a second dictionary corresponding to ids, to allow for similar objects to share the same dictionary.
# For example, (key ->)01:(value ->)01, 02:01 (02 is a road tile, which has the exact same stats as plain (01))


# note: Throne gets +5 Res

terrainKey = {0x01: 0x01, 0x02: 0x01, 0x13: 0x01, 0x17: 0x01,  # 01 - Plains, 02 - Road, 13 - Bridge, 17 - Floor,
              # 19 - Obstacle, 2E - Roof, 26 - Cliff (need to check its not impassable)
              0x19: 0x19, 0x2E: 0x19, 0x26: 0x19,
              0x0C: 0x0C,  # 0C - Forest,
              0x11: 0x11,  # 11 - Mountain,
              0x12: 0x12,  # 12 - Peak,
              0x23: 0x23,  # 23 - Gate,
              0x05: 0x05, 0x03: 0x05, 0x06: 0x05,  # 05 - House, 03 - Village, 06 - Shop
              0x10: 0x10,  # 10 - River
              0x16: 0x16,  # 16 - Lake
              0x25: 0x25,  # 25 - Ruins (Village)
              0x1F: 0x1F,  # 1F - Throne
              0x0A: 0x0A,  # 0A - Fort
              # 04 - Closed Village, 1A - Wall, 3F - Brace
              0x04: 0x04, 0x1A: 0x04, 0x3F: 0x04,
              0x00: 0x00,  # skip bytes
              0x1D: 0x1D,  # 1D - Pillar
              0x1B: 0x1B,  # Breakable Wall
              0x1E: 0x1E  # Locked Door
              }
# Note: Door may need to be seperated in order to allow for bot to open them (aka not view them entirely as a dead end)
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
        csv_reader = csv.reader(csv_file, delimiter=',')
        next(csv_reader)
        lines = {}
        for line in csv_reader:
            # currLine = line.strip().lower().split(', ')
            lines[line[0]] = line[1:]
    return lines


def fillItemLists():
    global itemList
    global physWeaponList
    global magWeaponList
    global staffList
    global classList
    global terrainDictionary
    itemList = openItemFile("Data/items.txt")
    physWeaponList = openItemFile("Data/physWeapons.txt")
    magWeaponList = openItemFile("Data/magWeapons.txt")
    staffList = openItemFile("Data/staves.txt")
    classList = openItemFile("Data/class.txt")
    terrainDictionary = openCSV("Data/Terrain Data.csv")


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
    global terrainKey
    global terrainDictionary
    # print(mapData)
    mapList = list(mapData)
    # print(mapList)
    moveMapList = []
    mapRow = []
    wasZero = False
    for tile in mapList:
        # -1 will be my default 'unknown map tile"
        currTile = terrainKey.get(tile, "-1")
        if currTile == 0 and not wasZero:
            moveMapList.append(mapRow)
            mapRow = []
            wasZero = True
        elif currTile == 0:
            wasZero = False
        else:
            mapRow.append(currTile)

    return moveMapList

# Don't think I would actually use belowv for anything.


def unitAndDestructibleMap(moveMapList):
    mapX = moveMapList[0].length
    mapY = moveMapList.length
    uAndDMap = numpy.zeros(mapY, mapX)
    for i in range(mapX):
        for j in range(mapY):
            if moveMapList[j][i] == 0x1B:
                uAndDMap[j][i] = 0x1B

    return uAndDMap


def findGoodMoves(moveMapList, unit, unitList, enemyList):
    # unit list will be used for rescue, dancing, healing and grouping up
    unitX = unit.xpos
    unitY = unit.ypos
    unitMove = unit.trueMove
    unitMoveType = unit.classMoveType
    mapX = len(moveMapList[0])
    mapY = len(moveMapList)
    unitMoveMap = numpy.zeros((mapY, mapX))
    # unitMoveMap[unitY][unitX] = unitMove
    for currUnit in unitList:
        unitMoveMap[currUnit.ypos][currUnit.xpos] = 100
    for enemy in enemyList:
        # making it like this for now, will replace with actual unit data later?
        unitMoveMap[enemy.ypos][enemy.xpos] = 200

    unitMoveMap[unitY][unitX] = unitMove
    print(unitMoveMap)
    unitMoveX = 0
    unitMoveY = 0

    return unitMoveX, unitMoveY


def floodFill(unitMoveMap, moveMapList, unitMoveType):
    global terrainDictionary

    return


def realFloodFill(x, y, moveMapList, unitMoveType):
    global terrainDictionary
    if (x < 0 or x >= len(moveMapList[0]) or y < 0 or y >= len(moveMapList)):
        return
    if not passableTerrain(moveMapList[y][x], unitMoveType):
        return

    return

# this works, but will need to change classMoveType to be a number. Could just create a dicitonary where the name is the id and the offset is the value


def passableTerrain(tile, unitMoveType):
    global terrainDictionary
    print(terrainDictionary)
    tileData = terrainDictionary.get(tile, "found nothing")
    print(tileData)
    unitMoveOnTile = tileData[4+unitMoveType]
    if unitMoveOnTile == "-":
        return False
    return True


def main():
    global commandList
    global terrainDictionary
    fillItemLists()
    # print(terrainDictionary.get("1F", "Terrain Data Not Found"))

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

    unitData = sockettest.main(commandList[0])
    unitList = getUnitData(unitData)
    enemyData = sockettest.main(commandList[1])
    enemyList = getEnemyData(enemyData)
    # money = int(sockettest.main(commandList[2]))
    mapData = sockettest.main(commandList[4])
    mapList = list(mapData)
    # print("Base map data is:")
    # print(mapList)
    moveMapList = createMoveMap(mapData)
    print(passableTerrain('19', 11))
    # unitMoveX, unitMoveY = findGoodMoves(
    #    moveMapList, unitList[0], unitList, enemyList)
    # print("Simplified map data is:")
    # print(moveMapList)
    # mapList = list(mapData)
    # print(mapList)
    # print(mapList[20])
    # isPlayerPhase = sockettest.main(commandList[5]).decode('utf-8')
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
