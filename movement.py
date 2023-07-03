import numpy
from numpy import Inf


def findObjective(simpleMapList, unit, unitList, terrainDictionary, objective):
    print("Attempting to find path to throne")
    unitX = unit.xpos
    unitY = unit.ypos
    objectiveY = int(objective[0])
    objectiveX = int(objective[1])
    # print(objectiveY)
    # print(objectiveX)
    unitMoveType = unit.classMoveId
    mapX = len(simpleMapList[0])
    mapY = len(simpleMapList)
    unitMoveMap = numpy.ones((mapY, mapX))*Inf
    visited = numpy.zeros((mapY, mapX))
    unitMoveMap[unitY][unitX] = 0
    path = findShortestPathToAllEnemiesAndTiles(
        unitX, unitY, unitMoveMap, objectiveX, objectiveY, simpleMapList, unitMoveType, visited, terrainDictionary)
    print(path)
    return path


def findAllMoves(simpleMapList, unit, unitList, enemyList, terrainDictionary):
    # unit list will be used for rescue, dancing, healing and grouping up
    unitX = unit.xpos
    unitY = unit.ypos
    unitMove = unit.trueMove
    unitMoveType = unit.classMoveId
    mapX = len(simpleMapList[0])
    mapY = len(simpleMapList)
    unitMoveMap = numpy.ones((mapY, mapX))*Inf
    visited = numpy.zeros((mapY, mapX))
    enemyPaths = []

    """for i in range(mapX):
        for j in range(mapY):
            unitMoveMap[j][i] = Inf"""

    """for enemy in enemyList:
        simpleMapList[enemy.ypos][enemy.xpos] = 0x9D"""
    #    unitMoveMap[enemy.ypos][enemy.xpos] = -8
    unitMoveMap[unitY][unitX] = 0
    # unitMoveMap = realFloodFill(
    #    unitX, unitY, unitMoveMap[unitY][unitX], unitMoveMap, unitMove, simpleMapList, unitMoveType)
    # unitMoveMap = findShortestPathToAllEnemiesAndTiles(unitX, unitY,
    #                                                   unitMoveMap, unit, enemyList, unitList, simpleMapList, unitMoveType, visited, terrainDictionary)
    iterator = 0
    for enemy in enemyList:
        enemyPaths.append(findShortestPathToAllEnemiesAndTiles(
            unitX, unitY, unitMoveMap, enemy.xpos, enemy.ypos, simpleMapList, unitMoveType, visited, terrainDictionary))
        iterator += 1
        print("Path found to " + str(iterator))
        unitMoveMap = numpy.ones((mapY, mapX))*Inf
        unitMoveMap[unitY][unitX] = 0

        visited = numpy.zeros((mapY, mapX))

    return enemyPaths


def up(y, x):
    return (y-1, x)


def left(y, x):
    return (y, x-1)


def right(y, x):
    return (y, x+1)


def down(y, x):
    return (y+1, x)


def findShortestPathToAllEnemiesAndTiles(x, y, unitMoveMap, goalX, goalY, simpleMap, unitMoveType, visited, terrainDictionary):
    initX = x
    initY = y
    # print(initX, initY, goalX, goalY)
    directions = [up, down, left, right]
    # print(visited)
    iterator = 0
    while True:
        for direction in directions:
            nextY, nextX = direction(y, x)
            # print(nextY)
            # print(nextX)
            if validTile(terrainDictionary, simpleMap, unitMoveType, nextX, nextY):
                # print("Tile at : " + str(nextX) + ", " + str(nextY))
                if visited[nextY][nextX] == 0:
                    tileData = terrainDictionary.get(simpleMap[nextY][nextX])
                    movePenalty = tileData[4+unitMoveType]
                    temp = float(movePenalty) + float(unitMoveMap[y][x])
                    # terrainDictionary.get(simpleMap[nextY][nextX])[
                    #    4+unitMoveType]
                    if temp < unitMoveMap[nextY][nextX]:
                        unitMoveMap[nextY][nextX] = int(temp)
                        # print(unitMoveMap[nextY][nextX])
        iterator += 1
        # print("Loop" + str(iterator))
        visited[y][x] = 1

        """t = unitMoveMap.copy()
        t[numpy.where(visited)] = Inf
        node_index = numpy.argmin(t)
        # This part might not work
        y = node_index//len(simpleMap)
        x = node_index % len(simpleMap[0])"""
        t = unitMoveMap.copy()
        t[numpy.where(visited)] = Inf
        node_index = numpy.argmin(t)
        y, x = findMinYX(t)
        # print(y, x)
        # print(unitMoveMap)
        # print(t)
        # print(node_index)
        # y = node_index//len(unitMoveMap)
        # x = node_index % len(unitMoveMap[0])
        # print(x)
        # print(y)
        if x == goalX and y == goalY:
            # print(unitMoveMap)
            break

    return backtrack(initX, initY, goalX, goalY, unitMoveMap)


def findMinYX(t):
    # print(t)
    xMin = 0
    yMin = 0
    minVal = Inf
    for row in range(len(t)):
        for col in range(len(t[0])):
            if t[row][col] < minVal:
                minVal = t[row][col]
                xMin = col
                yMin = row
    return yMin, xMin


def backtrack(initX, initY, goalX, goalY, unitMoveMap):
    endNode = [goalY, goalX]
    path = [endNode]
    # print(goalY, goalX)

    while True:
        potential_tiles = []
        potential_nodes = []
        directions = [up, down, left, right]
        for direction in directions:
            node = path[-1]
            currX = node[1]
            currY = node[0]
            # print(currY)
            # print(currX)

            node = direction(currY, currX)
            # print(node)
            if (validSquare(unitMoveMap, node[1], node[0])):
                potential_nodes.append(node)
                potential_tiles.append(unitMoveMap[node[0]][node[1]])
        least_distance_index = numpy.argmin(potential_tiles)
        path.append(potential_nodes[least_distance_index])
        # print(path)

        if path[-1][1] == initX and path[-1][0] == initY:
            # print("Found path")
            break
    print("Found path")
    return list(reversed(path))


def validTile(terrainDictionary, simpleMap, unitMoveType, x, y):
    if not validSquare(simpleMap, x, y):
        return False
    if not passableTerrain(simpleMap[y][x], unitMoveType, terrainDictionary):
        return False
    return True


def validSquare(simpleMap, x, y):
    if (x < 0 or x >= len(simpleMap[0]) or y < 0 or y >= len(simpleMap)):
        return False
    return True


def passableTerrain(tile, unitMoveType, terrainDictionary):
    # global terrainDictionary
    # print(terrainDictionary)
    # print(terrainDictionary.get("01", "something's going wrong here"))
    # print(terrainDictionary.get(0x0))
    tileData = terrainDictionary.get(tile, "Found no tile")
    # print(tileData)
    unitMoveOnTile = tileData[4+unitMoveType]
    if unitMoveOnTile == "-":
        return False
    return True
