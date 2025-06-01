#import pyautogui
#import controller
import time
import sockettest
from mgbaClient import MgbaClient
from unit import Unit
import csv
import numpy
import copy
import movement
import random
import newController
itemList = []
physWeaponList = []
magWeaponList = []
staffList = []
classList = []
terrainDictionary = {}  # id: name, Def Bonus, Avoid Bonus, Hp Recovery, Infantry A, Infantry B, Brigand, Pirate, Bereserker, Mages, Armor, Cav A, Cav B, Nomad, Nomad Trooper, Flier, Dragon
chapterData = []
commandList = ["getUnits", "getEnemies",
               "getMoney", "getMapSize", "getMap", "getIsPlayerPhase", "getChapterID"]
objective = "rout"
# Create a second dictionary corresponding to ids, to allow for similar objects to share the same dictionary.
# For example, (key ->)01:(value ->)01, 02:01 (02 is a road tile, which has the exact same stats as plain (01))


# note: Throne gets +5 Res

#Updating solely to check that git is working correctly.

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
              # 04 - Closed Village, 1A - Wall, 3F - Brace, 0x2C Sacae Building Roof
              0x04: 0x04, 0x1A: 0x04, 0x3F: 0x04, 0x2C: 0x04, 0x1B: 0x04, 0x1E: 0x04,
              0x00: 0x00,  # skip bytes
              0x1D: 0x1D  # 1D - Pillar
              # 0x1B: 0x1B,  # Breakable Wall
              # 0x1E: 0x1E  # Locked Door
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
            lines[int(line[0], base=16)] = line[1:]

    return lines


def fillItemLists():
    global itemList
    global physWeaponList
    global magWeaponList
    global staffList
    global classList
    global terrainDictionary
    global chapterData
    itemList = openItemFile("Data/items.txt")
    physWeaponList = openItemFile("Data/physWeapons.txt")
    magWeaponList = openItemFile("Data/magWeapons.txt")
    staffList = openItemFile("Data/staves.txt")
    classList = openItemFile("Data/class.txt")
    terrainDictionary = openCSV("Data/Fixed Terrain Data.csv")
    chapterData = openItemFile("Data/chapterdata.txt")


def getChapterObjective(client):
    global chapterData
    print(chapterData)
    #currChapterData = sockettest.send(commandList[6])
    currChapterData = int(client.send_command(commandList[6])[0])
    #currChapterData = int(currChapterData.decode())
    objective = chapterData[currChapterData][1:4]

    # objective = chapterData.get(str(currChapterData))
    print(objective)
    return objective


"""def moveTo(startX, startY, endX, endY):
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
"""



def enemyInRange(unitMoveMap, enemyList, unitMaxRange):
    enemiesInRange = []
    for enemy in enemyList:
        enemyX = enemy.xpos
        enemyY = enemy.ypos
        if enemyX-1 >= 0:
            # will eventually need to include unit range in this. And by eventually, I mean now
            if unitMoveMap[enemyY][enemyX-1] > 0:
                enemiesInRange.append(enemy)
                continue
        if enemyY-1 >= 0:
            if unitMoveMap[enemyY-1][enemyX] > 0:
                enemiesInRange.append(enemy)
                continue
        if enemyX+1 < len(unitMoveMap):
            if unitMoveMap[enemyY][enemyX+1] > 0:
                enemiesInRange.append(enemy)
                continue
        if enemyY+1 < len(unitMoveMap[0]):
            if unitMoveMap[enemyY+1][enemyX] > 0:
                enemiesInRange.append(enemy)
                continue
    return enemiesInRange

    """for i in range(len(unitMoveMap)):
        for j in range(len(unitMoveMap[0])):
            if (inRange(unitMoveMap, j, i)):
                for enemy in enemyList:
                    if j == enemy.xpos and i == enemy.ypos:
                        enemiesInRange.append(enemy)
                        print(enemy.xpos, enemy.ypos)

    return enemiesInRange"""


def inRange(unitMoveMap, xpos, ypos):
    if not (unitMoveMap[ypos][xpos] == -8):
        return False
    if xpos-1 > 0:
        if not (unitMoveMap[ypos][xpos-1] == -9):
            return True
    if ypos-1 > 0:
        if not (unitMoveMap[ypos-1][xpos] == -9):
            return True
    if xpos+1 < len(unitMoveMap[0]):
        if not (unitMoveMap[ypos][xpos+1] == -9):
            return True
    if ypos+1 < len(unitMoveMap):
        if not (unitMoveMap[ypos][xpos] == -9):
            return True


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
    enemyList = []
    dataCopy = data
    # note: below might not work, data might not match 'empty'
    if data == 'empty':
        return enemyList

    else:
        enemyData = list(data)
        enemyList = storeUnits(enemyData)

    return enemyList


"""def getEnemyData(data):
    enemyList = []
    enemyData = list(data)
    enemyList = storeUnits(enemyData)
    return enemyList
"""


def createMoveMap(mapData, unitList, enemyList):
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

# Doesn't work the way I want

# don't think I use for anything


def findUnitAttacks(unitMoveMap, simpleMapList, enemyList, unit):
    mapX = len(simpleMapList[0])
    mapY = len(simpleMapList)
    enemyMapList = []
    for enemy in enemyList:
        enemyMap = numpy.zeros((mapY, mapX))
        enemyMap[enemy.ypos][enemy.xpos] = -1
        for i in range(1, 11):
            if enemy.ypos+i < mapY:
                if enemy.xpos+i < mapX:
                    enemyMap[enemy.ypos+i][enemy.xpos+i] = i
                if enemy.xpos-i >= 0:
                    enemyMap[enemy.ypos+i][enemy.xpos-i] = i
                enemyMap[enemy.ypos+i][enemy.xpos] = i
            if enemy.ypos-i >= 0:
                if enemy.xpos - i >= 0:
                    enemyMap[enemy.ypos-i][enemy.xpos-i] = i
                if enemy.xpos + i < mapX:
                    enemyMap[enemy.ypos-i][enemy.xpos+i] = i
                enemyMap[enemy.ypos-i][enemy.xpos] = i
            if enemy.xpos-i >= 0:
                enemyMap[enemy.ypos][enemy.xpos-i] = i
            if enemy.xpos+i < mapX:
                enemyMap[enemy.ypos][enemy.xpos+i] = i
        enemyMapList.append(enemyMap)
        print("New Enemy")
        print(enemyMap)

    return enemyMapList


def findAttackableEnemies(moveMapList, simpleMapList, unit, unitList, enemyList):
    if unit.ranges[0] == 0:
        return []
    mapX = len(simpleMapList[0])
    mapY = len(simpleMapList)
    attackableEnemiesList = []
    for enemy in enemyList:
        enemyAttackableFrom = []
        enemyX = enemy.xpos
        enemyY = enemy.ypos
        # all ranges will need to check the cardinal directions, so this one is done for all
        for ranges in unit.ranges:
            if enemyX - ranges >= 0:
                if moveMapList[enemyY][enemyX-ranges] >= 0:
                    enemyAttackableFrom.append([enemyY, enemyX-ranges, ranges])
            if enemyY - ranges >= 0:
                if moveMapList[enemyY-ranges][enemyX] >= 0:
                    enemyAttackableFrom.append([enemyY-ranges, enemyX, ranges])
            if enemyX+ranges < mapX:
                if moveMapList[enemyY][enemyX+ranges] >= 0:
                    enemyAttackableFrom.append([enemyY, enemyX+ranges, ranges])
            if enemyY+ranges < mapY:
                if moveMapList[enemyY+ranges][enemyX] >= 0:
                    enemyAttackableFrom.append([enemyY+ranges, enemyX, ranges])
            # Until i can figure out a systematic approach, will have to hard code each range
            if ranges == 2:
                xMinus = int(enemyX-(ranges/2))
                xPlus = int(enemyX+(ranges/2))
                yMinus = int(enemyY-(ranges/2))
                yPlus = int(enemyY+(ranges/2))
                if xMinus >= 0:
                    if yMinus >= 0:
                        if moveMapList[yMinus][xMinus] >= 0:
                            enemyAttackableFrom.append(
                                [yMinus, xMinus, ranges])
                    if yPlus < mapY:

                        if moveMapList[yPlus][xMinus] >= 0:
                            enemyAttackableFrom.append([yPlus, xMinus, ranges])
                if xPlus < mapX:
                    if yMinus >= 0:
                        if moveMapList[yMinus][xPlus] >= 0:
                            enemyAttackableFrom.append(
                                [yMinus, xPlus, ranges])
                    if yPlus < mapY:
                        if moveMapList[yPlus][xPlus] >= 0:
                            enemyAttackableFrom.append(
                                [yPlus, xPlus, ranges])
        if enemyAttackableFrom:
            attackableEnemiesList.append([enemy, enemyAttackableFrom])
    return attackableEnemiesList


def checkIfEnemy(enemyList, i, j):
    for enemy in enemyList:
        if enemy.ypos == i and enemy.xpos == j:
            return True
    return False


def unitAndDestructibleMap(moveMapList):
    mapX = moveMapList[0].length
    mapY = moveMapList.length
    uAndDMap = numpy.zeros(mapY, mapX)
    for i in range(mapX):
        for j in range(mapY):
            if moveMapList[j][i] == 0x1B:
                uAndDMap[j][i] = 0x1B

    return uAndDMap


def findAllMoves(simpleMapList, unit, unitList, enemyList):
    # unit list will be used for rescue, dancing, healing and grouping up
    simpleMap = copy.deepcopy(simpleMapList)
    unitX = unit.xpos
    unitY = unit.ypos
    unitMove = unit.trueMove
    unitMoveType = unit.classMoveId
    mapX = len(simpleMapList[0])
    mapY = len(simpleMapList)
    unitMoveMap = numpy.zeros((mapY, mapX))
    for i in range(mapX):
        for j in range(mapY):
            unitMoveMap[j][i] = -9

    for enemy in enemyList:
        simpleMap[enemy.ypos][enemy.xpos] = 0x9D
    #    unitMoveMap[enemy.ypos][enemy.xpos] = -8
    unitMoveMap[unitY][unitX] = unitMove
    unitMoveMap = realFloodFill(
        unitX, unitY, unitMoveMap[unitY][unitX], unitMoveMap, unitMove, simpleMap, unitMoveType)
    return unitMoveMap


def findFullMapMove(simpleMapList, unit, unitList):
    unitX = unit.xpos
    unitY = unit.ypos
    unitMove = unit.trueMove
    unitMoveType = unit.classMoveId
    mapX = len(simpleMapList[0])
    mapY = len(simpleMapList)
    unitMoveMap = numpy.zeros((mapY, mapX))
    for i in range(mapX):
        for j in range(mapY):
            unitMoveMap[j][i] = -9

   # for enemy in enemyList:
        # simpleMapList[enemy.ypos][enemy.xpos] = 0x9D
    #    unitMoveMap[enemy.ypos][enemy.xpos] = -8
    unitMoveMap[unitY][unitX] = 99
    unitMoveMap = realFloodFill(
        unitX, unitY, unitMoveMap[unitY][unitX], unitMoveMap, 99, simpleMapList, unitMoveType)
    return unitMoveMap


def realFloodFill(x, y, prev, unitMoveMap, unitMove, moveMapList, unitMoveType):
    global terrainDictionary
    # print(moveMapList[y][x])
    if (x < 0 or x >= len(moveMapList[0]) or y < 0 or y >= len(moveMapList)):
        return
    if not passableTerrain(moveMapList[y][x], unitMoveType) and not (unitMove == unitMoveMap[y][x]):
        return
    tileData = terrainDictionary.get(moveMapList[y][x])
    # print(tileData)

    movePenalty = tileData[4+unitMoveType]
    # This is exclusively for when starting on a tile that is impassable (i.e a closed village, or broken bridge)
    if movePenalty == "-":
        movePenalty = 1

    tempMove = int(prev) - int(movePenalty)

    if (unitMoveMap[y][x] == tempMove or tempMove < 0 or (unitMoveMap[y][x] > tempMove and unitMoveMap[y][x] != unitMove)):
        return
    # print(tempMove)
    # if unitMoveMap[y][x] > tempMove:
    #    return
    if unitMoveMap[y][x] < tempMove:
        unitMoveMap[y][x] = tempMove
    # print("Start of new")
    # print(x)
    # print(y)
    # print(unitMoveMap)
    realFloodFill(x-1, y, unitMoveMap[y][x],
                  unitMoveMap, unitMove, moveMapList, unitMoveType)
    realFloodFill(x+1, y, unitMoveMap[y][x],
                  unitMoveMap, unitMove, moveMapList, unitMoveType)
    realFloodFill(x, y-1, unitMoveMap[y][x],
                  unitMoveMap, unitMove, moveMapList, unitMoveType)
    realFloodFill(x, y+1, unitMoveMap[y][x],
                  unitMoveMap, unitMove, moveMapList, unitMoveType)
    return unitMoveMap


def calculateAttackRating(unit, weapon, enemy, attackRange):
    print("Entered attack rating function")
    attackRating = 0
    enemyHp = enemy.currHP
    unitHp = unit.currHP
    enemyCanAttackBack = False
    enemyWeapon = enemy.fullInv[0]
    unitDouble = False
    enemyDouble = False
    triangleAdvantage = 0

    # do basic attack calculation first
    if weapon[0][7] == enemyWeapon[0][7]:
        enemyCanAttackBack = True

    unitAttack = int(weapon[0][3]) + unit.strength

    if (weapon[0][1] == "sword" and enemyWeapon[0][1] == "axe") or (weapon[0][1] == "axe" and enemyWeapon[0][1] == "lance") or (weapon[0][1] == "lance" and enemyWeapon[0][1] == "sword"):
        triangleAdvantage = 1
    elif (weapon[0][1] == "sword" and enemyWeapon[0][1] == "lance") or (weapon[0][1] == "axe" and enemyWeapon[0][1] == "sword") or (weapon[0][1] == "lance" and enemyWeapon[0][1] == "axe"):
        triangleAdvantage = -1

    damage = unitAttack + triangleAdvantage - enemy.defense
    weaponSlowdown = int(weapon[0][4]) - unit.trueCon
    if weaponSlowdown < 0:
        weaponSlowdown = 0
    attackSpeed = unit.speed - weaponSlowdown
    if attackSpeed < 0:
        attackSpeed = 0

    enemyWeaponSlowdown = int(enemyWeapon[0][4]) - enemy.trueCon
    if enemyWeaponSlowdown < 0:
        enemyWeaponSlowdown = 0
    enemyAS = enemy.speed - enemyWeaponSlowdown
    if enemyAS < 0:
        enemyAS = 0
    if attackSpeed >= enemyAS + 4:
        unitDouble = True
    elif enemyAS >= attackSpeed + 4:
        enemyDouble = True

    hpDamage = enemyHp - damage

    # enemyHp = enemyHp - damage
    if enemyCanAttackBack:
        enemyAttack = int(enemyWeapon[0][3]) + enemy.strength
        # minus triangleAdvantage because we're looking at it from the reverse. So if player wins it, we minus it, and if player loses, we add
        enemyDamage = enemyAttack - triangleAdvantage - unit.defense
        enemyHpDamage = unitHp - enemyDamage
    else:
        enemyDamage = 0
        enemyHpDamage = 0
    if unitDouble:
        hpDamage = hpDamage - damage
    elif enemyDouble and enemyCanAttackBack:
        enemyHpDamage = enemyHpDamage - enemyDamage
    # print(hpDamage)
    # print(enemyHpDamage)
    # BAD CALCULATION, BUT THIS ALL WORKS NEEDS HIT CALC BARE MINIMUM, AND TERRAIN STATS
    attackRating = (float(damage)/enemyHp - float(enemyDamage)/unitHp)*100
    return attackRating


def findBestMove(simpleMapList, unitMoveList, unit, unitList, attackableEnemies, enemyList, objective):
    # the default best move is to not move at all.
    global terrainDictionary
    bestMoveX = unit.xpos
    bestMoveY = unit.ypos
    bestMoveAction = ""
    itemPos = 0
    if (unit.currHP < unit.maxHP/2):
        bestMoveAction = "heal"

    # enemiesInRange = enemyInRange(unitMoveList, enemyList, unit.maxRange)
    # print(enemiesInRange)
    # bestMoveAction = "nothing"
    bestMove = [-100]
    if not attackableEnemies:
        print("entered here")
        # fullMapRange = findFullMapMove(simpleMapList, unit, unitList)
        # nearestEnemy = findNearestEnemy(
        #    fullMapRange, simpleMapList, unit, unitList, enemyList)
        moveTowardList = movement.findAllMoves(
            simpleMapList, unit, unitList, enemyList, terrainDictionary)
        print(moveTowardList)
        if not moveTowardList:
            if unit.name == 'lyn':
                seizeLocation = objective[1:3]
                moveTowardList = movement.findObjective(
                    simpleMapList, unit, unitList, terrainDictionary, seizeLocation)
                bestMoveAction = "move"
                index = -1
                if len(moveTowardList) < unit.trueMove:
                    bestMoveY = moveTowardList[-1][0]
                    bestMoveX = moveTowardList[-1][1]
                else:
                    bestMoveY = moveTowardList[unit.trueMove][0]
                    bestMoveX = moveTowardList[unit.trueMove][1]
                if len(moveTowardList) <= unit.trueMove-1:
                    bestMoveAction = "seize"

                return (0, [bestMoveY, bestMoveX], 0, 0, bestMoveAction)

            return [0, [bestMoveY, bestMoveX], 0, 0, "wait"]

        # First idea: Randomly select an enemy to move towards. Will also need to include a 0,0 point. Or Objective.
        # Or just wait in place?
        # will need to work the maxVal stuff into the seize stuff
        maxVal = len(moveTowardList)
        index = random.randint(0, maxVal-1)
        bestMoveY = moveTowardList[index][unit.trueMove][0]
        bestMoveX = moveTowardList[index][unit.trueMove][1]
        bestMoveAction = "move"
        print(bestMoveY, bestMoveX)
        return [0, [bestMoveY, bestMoveX], 0, 0, bestMoveAction]

        # return [0, [bestMoveY, bestMoveX]]

    for enemyAttack in attackableEnemies:
        print(enemyAttack)
        attackRange = enemyAttack[1][0][2]
        for item in unit.fullInv:
            if not item[3] == "ITEM":
                for attacks in enemyAttack[1]:
                    # print("range is: " + str(attacks[2]))
                    # print("current weapon range is: " + str(item[0][7]))
                    if attacks[2] == int(item[0][7]):
                        # print("reached here")
                        attackRating = calculateAttackRating(
                            unit, item, enemyAttack[0], attacks[2])
                        # print(enemyAttack[0], attackRating)
                        # print(bestMove)
                        # print(attackRating)
                        # print(attackRating > float(bestMove[0])
                        if attackRating > bestMove[0]:
                            bestMove = [attackRating,
                                        attacks, item, itemPos, "attack"]
                            print(bestMove)
            itemPos += 1
    if bestMove[0] <= -100:
        healingItem = Unit.getHealingItems(unit)
        print(str(healingItem) + " this is where the healing item is")
        if healingItem >= 0:
            bestMove = [-100, [bestMoveY, bestMoveX],
                        "potion", healingItem, "heal"]

    return bestMove


def findNearestEnemy(fullMoveMap, simpleMapList, unit, unitList, enemyList):
    # due to the different way fullMoveMap works, this might not work
    enemiesReachableEventually = findAttackableEnemies(
        fullMoveMap, simpleMapList, unit, unitList, enemyList)
    if not enemiesReachableEventually:
        return 0
    nearestEnemy = []
    nearestEnemyDistance = 999
    xPos = unit.xpos
    yPos = unit.ypos
    currEnemy = []
    for enemies in enemiesReachableEventually:
        currEnemy = enemies
        currEnemyXpos = enemies.xpos
        currEnemyYpos = enemies.ypos
        if fullMoveMap[currEnemyYpos][currEnemyXpos] < nearestEnemyDistance:
            nearestEnemy = currEnemy
            nearestEnemyDistance = fullMoveMap[currEnemyYpos][currEnemyXpos]

    return [nearestEnemy, ]


# might need new approach, focused around using shortest path algorithms to find the optimal enemy to attack.
# would take into consideration both the enemy's attack rating (so how successful an attack would be) and the distance from the enemy
# maybe as a straight up multiplier/divisor depending on how many turns it'd take to reach it? Would also be reusable for objectives.
# I think this is the best approach, so look into Djkstra's

def findShortestPathToAllEnemiesAndTiles(unitMoveMap, unit, enemyList, unitList, simpleMap):

    return 0


def passableTerrain(tile, unitMoveType):
    global terrainDictionary
    # print(terrainDictionary)
    # print(terrainDictionary.get("01", "something's going wrong here"))
    # print(terrainDictionary.get(0x0))
    tileData = terrainDictionary.get(tile, "Found no tile")
    # print(tileData)
    unitMoveOnTile = tileData[4+unitMoveType]
    if unitMoveOnTile == "-":
        return False
    return True

# GET ADVICE ON FIXING CONTROLS. THIS IS CRUCIAL
def doMove(unit, bestMove, client):
    unitX = unit.xpos
    unitY = unit.ypos
    print(bestMove)
    bestMoveX = bestMove[1][1]
    bestMoveY = bestMove[1][0]
    itemPos = bestMove[3]
    bestMoveAction = bestMove[4]
    currItemPos = 0
    print(bestMoveX)
    print(bestMoveY)
    # controller.press_a()
    """    
    while not (unitX == bestMoveX):
        if unitX > bestMoveX:
            sockettest.send("pressLeft")
            time.sleep(0.2)
            #controller.press_left()
            unitX = unitX - 1
            print("moving")
        elif unitX < bestMoveX:
            sockettest.send("pressRight")
            time.sleep(0.2)
            #controller.press_right()
            unitX = unitX + 1
            print("moving")
    while not (unitY == bestMoveY):
        if (unitY > bestMoveY):
            sockettest.send("pressUp")
            time.sleep(0.2)
            #controller.press_up()
            unitY = unitY - 1
            print("moving")
        elif unitY < bestMoveY:
            sockettest.send("pressDown")
            time.sleep(0.2)
            #controller.press_down()
            unitY = unitY + 1
            print("moving")
    """
    newController.press_a(client)
    while not (unitX == bestMoveX):
        if unitX > bestMoveX:
            newController.press_left(client)
            unitX = unitX -1
        else:
            newController.press_right(client)
            unitX = unitX +1
        time.sleep(0.2)
    while not (unitY == bestMoveY):
        if unitY > bestMoveY:
            newController.press_up(client)
            unitY = unitY -1
        else:
            newController.press_down(client)
            unitY = unitY +1
        time.sleep(0.2)
    print("Acting")
    newController.press_a(client)
    #controller.press_a()
    time.sleep(3)
    if bestMoveAction == "attack":
        print("attacking")
        newController.press_a(client)

        #controller.press_a()
        while not (itemPos == currItemPos):
            newController.press_down(client)
            #controller.press_down()
            currItemPos += 1
        #controller.attack()
        for i in range(3):
            newController.press_a(client)
            time.sleep(0.2)
        time.sleep(5)
    elif bestMoveAction == "seize":
        print("seizing")
        #controller.press_a()
        newController.press_a(client)

    elif bestMoveAction == "heal":
        print("healing")
        #controller.press_a()
        newController.press_a(client)
        time.sleep(0.2)
        while not (itemPos == currItemPos):
            #controller.press_down()
            newController.press_down(client)
            time.sleep(0.2)
            currItemPos += 1
        #controller.press_a()
        newController.press_a(client)
        time.sleep(0.2)

    else:
        print("Ending turn")
        newController.end_move(client)
        


    return


def main():
    client = MgbaClient()
    print("Running branched version")
    global commandList
    global terrainDictionary
    fillItemLists()
    # print(terrainDictionary.get("1F", "Terrain Data Not Found"))

    # print("Items: " + str(itemList))
    # print("Physical Weapons: " + str(physWeaponList))
    # print("Magic Weapons: " + str(magWeaponList))
    # print("Staves: " + str(staffList))

    #pyautogui.moveTo(7, 80, 0.2)
    #pyautogui.click()

    # mapsize = list(sockettest.main(commandList[3]))

    # if a map has a width of 10, then the tiles go from 0-9
    # mapxlength = mapsize[1] + mapsize[0]
    # mapylength = mapsize[3] + mapsize[2]

    # print(mapxlength)
    # print(mapylength)
    chapterObjective = getChapterObjective(client)
    time.sleep(0.1)
    print(chapterObjective)
    while (True):
        #neccessary to skip any dialogue at the start of a chapter
        newController.press_start(client)
        newController.press_start(client)
        time.sleep(0.1)
        unitData = client.send_command(commandList[0])
        time.sleep(0.1)
        #unitData = sockettest.send(commandList[0])
        print(unitData)
        unitList = getUnitData(unitData)

    # for units in unitList:
    #    print(units.name)
    # print(units.fullInv)
    #    print(units.maxRange)
    #    print(units.minRange)

    # print(unitList[0].inventory)
    # print(unitList[0].fullInv)
        enemyData = client.send_command(commandList[1])
        time.sleep(0.1)
        #enemyData = sockettest.send(commandList[1])
        enemyList = getEnemyData(enemyData)
    # money = int(sockettest.main(commandList[2]))
        mapData = client.send_command(commandList[4])
        time.sleep(0.1)
        #mapData = sockettest.send(commandList[4])
        mapList = list(mapData)
    # print(mapList)
    # print("Base map data is:")
    # print(mapList)
        simpleMapList = createMoveMap(mapData, unitList, enemyList)

    # print(simpleMapList)
    # print(passableTerrain('19', unitList[3].classMoveId))
    # print(unitList[0].classMoveId)
        unitMoveList = []
        allMoveList = []
        print(simpleMapList)
        #controller.press_a()
        
        for currUnit in unitList:
            
            
            print(currUnit.name)
            oldMoveMap = findAllMoves(
                simpleMapList, currUnit, unitList, enemyList)
            print("Old Map:")
            print(oldMoveMap)
            attackableEnemies = findAttackableEnemies(
                oldMoveMap, simpleMapList, currUnit, unitList, enemyList)
            bestMove = findBestMove(simpleMapList, unitMoveList,
                                    currUnit, unitList, attackableEnemies, enemyList, chapterObjective)
            # if not bestMove[0] == -100:
            doMove(currUnit, bestMove, client)
            # else:
            #    controller.press_a()
            #    controller.end_move()
            #controller.next_unit()
            
            #unitData = sockettest.send(commandList[0])
            unitData = client.send_command(commandList[0])
            unitList = getUnitData(unitData)
            #enemyData = sockettest.send(commandList[1])
            enemyData = client.send_command(commandList[1])
            enemyList = getEnemyData(enemyData)
            #mapData = sockettest.send(commandList[4])
            mapData = client.send_command(commandList[4])
            mapList = list(mapData)
            simpleMapList = createMoveMap(mapData, unitList, enemyList)
            #newController.next_unit(client)
            newController.press_l(client)
        newController.end_turn(client)
        #Need to find a flag to wait for so we know when it's our turn again.
        time.sleep(20)

    # newMoveMap = findFullMapMove(simpleMapList, currUnit, unitList)
    # print("Old new map list")
    #   print(newMoveMap)
    # print("New Move List")
    # newMoveList = movement.findAllMoves(
    #    simpleMapList, currUnit, unitList, enemyList, terrainDictionary)
    """iterator = 0
        for enemy in enemyList:
            print(enemy)
            print(newMoveList[iterator])
            iterator += 1"""

    """currUnit = unitList[0]
    oldMoveMap = findAllMoves(simpleMapList, currUnit, unitList, enemyList)
    print("Old Map:")
    print(oldMoveMap)
    # newMoveMap = findFullMapMove(simpleMapList, currUnit, unitList)
    # print("Old new map list")
    # print(newMoveMap)
    print("New Move List")
    newMoveList = movement.findAllMoves(
        simpleMapList, currUnit, unitList, enemyList, terrainDictionary)
    iterator = 0
    for enemy in enemyList:
        print(enemy)
        print(newMoveList[iterator])
        iterator += 1"""
    # print(newMoveList)
    # controller.press_a()
#     for units in unitList:
#         print(units.name)
#         print("Old Map: ")
#         oldMoveMap = findAllMoves(simpleMapList, units, unitList, enemyList)
#         print(oldMoveMap)

#         print("New Map: ")
#         # unitMoveMap = newMoveMap(simpleMapList, units, unitList, enemyList)
#         unitMoveMap = findFullMapMove(
#             simpleMapList, units, unitList, enemyList)
#         print(unitMoveMap)

#         """print(units.name + "'s possible moves")
#         unitMoveList = findAllMoves(simpleMapList, units, unitList, enemyList)
#         print(unitMoveList)
#         print("Unit ranges: ")
#         print(units.ranges)
#         attackableEnemies = findAttackableEnemies(
#             unitMoveList, simpleMapList, units, unitList, enemyList)
#         print("Enemies they can attack are: ")
#         print(attackableEnemies)
#         bestMove = findBestMove(simpleMapList, unitMoveList,
#                                 units, unitList, attackableEnemies)
#         print(bestMove[0])
#         if not (bestMove[0] == 0):
#             print("trying to do a move")
#             doMove(units, bestMove)
#         else:
#             controller.press_a()
#             controller.end_move()
#         controller.next_unit()
#     controller.end_turn()"""
#     # findUnitAttacks(unitMoveList, simpleMapList, enemyList, unitList[0])

#     # unitBestMove, bestX, bestY = findBestMove(
#     #    simpleMapList, unitMoveList, units, unitList, enemyList)

#     # unitMoveX, unitMoveY = findGoodMoves(
#     #    moveMapList, unitList[0], unitList, enemyList)
#     # print("Simplified map data is:")
#     # print(moveMapList)
#     # mapList = list(mapData)
#     # print(mapList)
#     # print(mapList[20])
#     # isPlayerPhase = sockettest.main(commandList[5]).decode('utf-8')
#     # print(mapsize)
#     # print(isPlayerPhase)
#     # if isPlayerPhase == 'T':
#     #    print("It's your turn")
#     # else:
#     #    print("Not your turn")
#     # unitList = storeUnits(unitData)
#     # enemyList = storeUnits(enemyData)

#     # need to figure out map stuff before I can create main loop
#     """while isPlayerPhase == 'T':
#         for units in unitList:
#             if not units.hasMoved:
#                 moveX, moveY, moveAction = decideMove(
#                     units, unitList, enemyList)
#                 moveTo(units.xpos, units.ypos, moveX, moveY)
# """
#     # moveList = []
#     # for units in unitList:
#     #    units.printUnitInformation()
#     # for enemies in enemyList:
#     #    enemies.printUnitInformation()
#     # print(money)
#     # print(unitList)
#     # print(enemyList)
#     # print(money)
#     """for currUnit in unitList:
#         moveList.append(decideMove())
#     controller.next_unit()
#     unitX = unitList[0].xpos
#     unitY = unitList[0].ypos
#     enemiesInRange = enemyInRange(unitList[0], enemyList)
#     if not enemiesInRange:
#         moveTo(unitX, unitY, unitX-3, unitY-2)
#         time.sleep(1)
#         controller.end_move()

#     else:
#         moveTo(unitX, unitY,
#                enemiesInRange[0].xpos+1, enemiesInRange[0].ypos)
#         time.sleep(1)
#         controller.attack()"""
#     # for units in unitList:

#     # Test for making sure the class data is generated correctly
#     # unitId = units.id
#     # print("This unit is: " + unitId)
#     # print(unitId + " is in the class corresponding to: " + units.classId)
#     # print(units.classId + " is the " + units.className + " class")
#     # print(units.className + " has " + units.classCon + " con, " +
#     #      units.classMove + " move, " + units.classMoveType + " move type")
#     # print("So " + unitId + " has " + str(units.trueMove) +
#     #      " move and " + str(units.trueCon) + " constitution")

#     # lyn moved to 0c 05
#     # needs a buffer for attack animations.
#     # time.sleep(2)

#     # controller.press_up()

#     # attacking requires 3 a presses. One to select the attack option, one to select the weapon, one to select the enemy.
#     # controller.press_a(3)

#     # controller.press_up()
#     # controller.press_a()


main()
