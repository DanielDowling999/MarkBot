#import pyautogui
#import controller
import time
from mgbaClient import MgbaClient
from unit import Unit
import csv
import numpy
import copy
import movement
import random
import controller
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
    currChapterData = int(client.send_command(commandList[6])[0])
    objective = chapterData[currChapterData][1:4]

    print(objective)
    return objective

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
    if data == 'empty':
        return enemyList

    else:
        enemyData = list(data)
        enemyList = storeUnits(enemyData)

    return enemyList

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


def enemyAndUnitMap(mapData, enemyList):
    for enemy in enemyList:
        mapData[enemy.ypos][enemy.xpos] = 0x9D
    return mapData

def findAttackableEnemies(unitMoveMap, simpleMapList, unit, unitList, enemyList):
    if unit.ranges[0] == 0:
        return []

    mapX = len(simpleMapList[0])
    mapY = len(simpleMapList)
    attackableEnemiesList = []

    # Get occupied tiles so we don't try to end a move on a friendly unit
    occupied_positions = {(u.xpos, u.ypos) for u in unitList if u.id != unit.id}
    print(f"Unit is at ({unit.xpos}, {unit.ypos})")
    print(f"unitMoveMap at unit tile: {unitMoveMap[unit.ypos][unit.xpos]}")
    for enemy in enemyList:
        enemyAttackableFrom = []
        ex, ey = enemy.xpos, enemy.ypos
        print(f"Checking enemy {enemy.name} at ({ex}, {ey})")

        for rng in unit.ranges:
            # Cardinal directions
            potential_positions = [
                (ey, ex - rng),  # Left
                (ey, ex + rng),  # Right
                (ey - rng, ex),  # Up
                (ey + rng, ex),  # Down
            ]

            # Diagonals (if 2-range or higher)
            if rng == 2:
                potential_positions += [
                    (ey - 1, ex - 1),
                    (ey - 1, ex + 1),
                    (ey + 1, ex - 1),
                    (ey + 1, ex + 1),
                ]

            for y, x in potential_positions:
                if 0 <= y < mapY and 0 <= x < mapX:
                    if unitMoveMap[y][x] >= 0 and (x, y) not in occupied_positions:
                        print(f"-> Can attack from ({x}, {y} using range {rng})")
                        enemyAttackableFrom.append([y, x, rng])

        if enemyAttackableFrom:
            attackableEnemiesList.append([enemy, enemyAttackableFrom])

    return attackableEnemiesList

def unitAndDestructibleMap(moveMapList):
    mapX = moveMapList[0].length
    mapY = moveMapList.length
    uAndDMap = numpy.zeros(mapY, mapX)
    for i in range(mapX):
        for j in range(mapY):
            if moveMapList[j][i] == 0x1B:
                uAndDMap[j][i] = 0x1B

    return uAndDMap

#could be combined with movement.findAllValidMoves
# An alternate approach could be to calculate the absolute best move out of all units, execute it (swapping to the right unit using L+A),
# then repeating with the remaining units until all moves are done.
# Note: This might be slow. Will do the naive approach first (Just go unit-by-unit, find their best move, then go to the next one)

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
    unitMoveMap[unitY][unitX] = unitMove
    unitMoveMap = realFloodFill(
        unitX, unitY, unitMoveMap[unitY][unitX], unitMoveMap, unitMove, simpleMap, unitMoveType)
    for other in unitList:
        if other.id != unit.id:
            unitMoveMap[other.ypos][other.xpos] = -9
    return unitMoveMap

def realFloodFill(x, y, prev, unitMoveMap, unitMove, moveMapList, unitMoveType):
    global terrainDictionary
    if (x < 0 or x >= len(moveMapList[0]) or y < 0 or y >= len(moveMapList)):
        return
    if not passableTerrain(moveMapList[y][x], unitMoveType) and not (unitMove == unitMoveMap[y][x]):
        return
    tileData = terrainDictionary.get(moveMapList[y][x])
    movePenalty = tileData[4+unitMoveType]
    # This is exclusively for when starting on a tile that is impassable (i.e a closed village, or broken bridge)
    if movePenalty == "-":
        movePenalty = 1

    tempMove = int(prev) - int(movePenalty)

    if (unitMoveMap[y][x] == tempMove or tempMove < 0 or (unitMoveMap[y][x] > tempMove and unitMoveMap[y][x] != unitMove)):
        return

    if unitMoveMap[y][x] < tempMove:
        unitMoveMap[y][x] = tempMove

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
    # Very basic calculation for attackRating. 
    attackRating = (float(damage)/enemyHp - float(enemyDamage)/unitHp)*100
    return attackRating

def findBestMove(simpleMapList, unitMoveList, unit, unitList, attackableEnemies, enemyList, objective):
    # the default best move is to not move at all.
    global terrainDictionary
    bestMoveX = unit.xpos
    bestMoveY = unit.ypos
    bestMoveAction = ""
    itemPos = 0
    friendly_positions = {(u.xpos, u.ypos) for u in unitList if u.id != unit.id}
    enemy_positions = {(e.xpos, e.ypos) for e in enemyList}
    if (unit.currHP < unit.maxHP/2):
        bestMoveAction = "heal"
    bestMove = [-100]

    if not attackableEnemies:
        moveTowardList = movement.findAllValidMoves(
            simpleMapList, unit, unitList, enemyList, terrainDictionary)
        valid_paths = []
        trimmed_paths = []
        for path in moveTowardList:
            if len(path) < 2:
                continue
            pre_end = path[-2]
            end = path[-1]
            if (end[1], end[0]) in enemy_positions:
                ex, ey = end[1], end[0]
                px, py = pre_end[1], pre_end[0]
                if abs(px-ex) + abs(py-ey) ==1:
                    path = path[:-1]
            end_y, end_x = path[-1]
            if (end_x, end_y) in friendly_positions:
                continue  # Can't stop on another unit
            blocked = False
            if (end_x, end_y) in enemy_positions:
                print(f"Path ends on enemy at {(end_x, end_y)}")
                continue
            for y,x in path[1:-1]:
                if (x, y) in enemy_positions:
                    blocked=True
                    break
            if blocked:
                print(f"Blocked path due to enemy at: {(x, y)} - {path}")
            elif (end_x, end_y) in friendly_positions:
                print(f"Path ends on friendly unit at {(end_x, end_y)}")
            if not blocked:
                valid_paths.append(path)
        moveTowardList = valid_paths
        print(moveTowardList)
        if not moveTowardList:
            if unit.name == 'lyn' and objective[0] == 'seize':
                seizeLocation = objective[1:3]
                moveTowardList = movement.findObjective(
                    simpleMapList, unit, unitList, terrainDictionary, seizeLocation)
                bestMoveAction = "move"
                #index = -1
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
        #should be moved to own function
        maxVal = len(moveTowardList)
        totalCost = 0
        moveIndex = 0
        index = random.randint(0, maxVal-1)
        path = moveTowardList[index]
        for i in range(1, len(path)):
            y, x = path[i]
            tile = simpleMapList[y][x]
            moveCost = terrainDictionary[tile][4+unit.classMoveId]
            if moveCost == "-" or moveCost.strip() == "":
                break
            moveCost = float(moveCost)
            if totalCost + moveCost > unit.trueMove:
                break
            totalCost +=moveCost
            if (x,y) not in friendly_positions:
                moveIndex=i
        bestMoveY = path[moveIndex][0]
        bestMoveX = path[moveIndex][1]
        bestMoveAction = "move"
        print(bestMoveY, bestMoveX)
        return [0, [bestMoveY, bestMoveX], 0, 0, bestMoveAction]



    for enemyAttack in attackableEnemies:
        print(enemyAttack)
        attackRange = enemyAttack[1][0][2]
        for item in unit.fullInv:
            if not item[3] == "ITEM":
                for attacks in enemyAttack[1]:
                    if attacks[2] == int(item[0][7]):
                        attackRating = calculateAttackRating(
                            unit, item, enemyAttack[0], attacks[2])

                        if attackRating > bestMove[0]:
                            bestMove = [attackRating,
                                        attacks, item, itemPos, "attack"]

            itemPos += 1
    if bestMove[0] <= -100:
        healingItem = Unit.getHealingItems(unit)
        print(str(healingItem) + " this is where the healing item is")
        if healingItem >= 0:
            bestMove = [-100, [bestMoveY, bestMoveX],
                        "potion", healingItem, "heal"]

    return bestMove



def passableTerrain(tile, unitMoveType):
    global terrainDictionary
    tileData = terrainDictionary.get(tile, "Found no tile")
    unitMoveOnTile = tileData[4+unitMoveType]
    if unitMoveOnTile == "-":
        return False
    return True

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

    controller.press_a(client)
    while not (unitX == bestMoveX):
        if unitX > bestMoveX:
            controller.press_left(client)
            unitX = unitX -1
        else:
            controller.press_right(client)
            unitX = unitX +1
        time.sleep(0.2)
    while not (unitY == bestMoveY):
        if unitY > bestMoveY:
            controller.press_up(client)
            unitY = unitY -1
        else:
            controller.press_down(client)
            unitY = unitY +1
        time.sleep(0.2)
    print("Acting")
    controller.press_a(client)

    time.sleep(3)
    if bestMoveAction == "attack":
        print("attacking")
        controller.press_a(client)
        while not (itemPos == currItemPos):
            controller.press_down(client)
            currItemPos += 1
        for i in range(3):
            controller.press_a(client)
            time.sleep(0.2)
        time.sleep(5)
    elif bestMoveAction == "seize":
        print("seizing")
        controller.press_a(client)

    elif bestMoveAction == "heal":
        print("healing")
        controller.press_a(client)
        time.sleep(0.2)
        while not (itemPos == currItemPos):
            controller.press_down(client)
            time.sleep(0.2)
            currItemPos += 1
        controller.press_a(client)
        controller.press_a(client)
        time.sleep(0.2)

    else:
        print("Ending turn")
        controller.end_move(client)
    return


def main():
    client = MgbaClient()
    global commandList
    global terrainDictionary
    fillItemLists()

    chapterObjective = getChapterObjective(client)
    time.sleep(0.1)
    print(chapterObjective)
    while (True):
        print("Turn Start")
        unitData = client.send_command(commandList[0])
        time.sleep(0.1)
        unitList = getUnitData(unitData)
        unitList = [u for u in unitList if u.isAlive()]
        enemyData = client.send_command(commandList[1])
        time.sleep(0.1)

        enemyList = getEnemyData(enemyData)
        enemyList = [e for e in enemyList if e.isAlive()]

        mapData = client.send_command(commandList[4])
        time.sleep(0.1)

        mapList = list(mapData)

        simpleMapList = createMoveMap(mapData, unitList, enemyList)
        simpleMapList = enemyAndUnitMap(simpleMapList, enemyList)

        unitMoveList = []
        allMoveList = []
        print("Terrain Map:")
        print(simpleMapList)

        
        for currUnit in unitList:
            print(f"Unit: {currUnit.name}, HP: {currUnit.currHP}, Status: {currUnit.status}, isAlive: {currUnit.isAlive()}")
            unitData = client.send_command(commandList[0])
            unitList = getUnitData(unitData)
            unitList = [u for u in unitList if u.isAlive()]

            enemyData = client.send_command(commandList[1])
            enemyList = getEnemyData(enemyData)
            enemyList = [e for e in enemyList if e.isAlive()]
            mapData = client.send_command(commandList[4])
            simpleMapList = createMoveMap(mapData, unitList, enemyList)
            oldMoveMap = findAllMoves(
                simpleMapList, currUnit, unitList, enemyList)
            
            print("Terrain Map")
            print(simpleMapList)
            print("Move Map:")
            print(oldMoveMap)
            attackableEnemies = findAttackableEnemies(
                oldMoveMap, simpleMapList, currUnit, unitList, enemyList)
            bestMove = findBestMove(simpleMapList, unitMoveList,
                                    currUnit, unitList, attackableEnemies, enemyList, chapterObjective)


            doMove(currUnit, bestMove, client)

            controller.press_l(client)

        print("Turn End")
        time.sleep(20)

main()
