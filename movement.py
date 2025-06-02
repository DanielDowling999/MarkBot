import numpy
import heapq
from numpy import inf


def findObjective(simpleMapList, unit, unitList, terrainDictionary, objective):
    print("Attempting to find path to throne")
    unitX = unit.xpos
    unitY = unit.ypos
    objectiveY = int(objective[0])
    objectiveX = int(objective[1])
    unitMoveType = unit.classMoveId
    mapX = len(simpleMapList[0])
    mapY = len(simpleMapList)
    unitMoveMap = numpy.ones((mapY, mapX))*inf
    visited = numpy.zeros((mapY, mapX))
    unitMoveMap[unitY][unitX] = 0
    path = findShortestPathToAllEnemiesAndTiles(
        unitX, unitY, unitMoveMap, objectiveX, objectiveY, simpleMapList, unitMoveType, visited, terrainDictionary)
    print(path)
    return path


def findAllValidMoves(simpleMapList, unit, unitList, enemyList, terrainDictionary):
    # unit list will  be used for rescue, dancing, healing and grouping up
    unitX = unit.xpos
    unitY = unit.ypos
    unitMove = unit.trueMove
    unitMoveType = unit.classMoveId
    mapX = len(simpleMapList[0])
    mapY = len(simpleMapList)

     # DEBUG: Print dimensions
    #print(f"Map dimensions: {mapX} x {mapY}")
    #print(f"Unit position: ({unitX}, {unitY})")
    
    # Validate dimensions
    if mapX <= 0 or mapY <= 0:
        print(f"ERROR: Invalid map dimensions: {mapX} x {mapY}")
        return []
    
    if unitX >= mapX or unitY >= mapY or unitX < 0 or unitY < 0:
        print(f"ERROR: Unit position out of bounds: ({unitX}, {unitY}) for map {mapX} x {mapY}")
        return []
    unitMoveMap = numpy.ones((mapY, mapX))*inf
    visited = numpy.zeros((mapY, mapX))
    enemyPaths = []

    unitMoveMap[unitY][unitX] = 0

    iterator = 0
    for enemy in enemyList:
        enemyPaths.append(findShortestPathToAllEnemiesAndTiles(
            unitX, unitY, unitMoveMap, enemy.xpos, enemy.ypos, simpleMapList, unitMoveType, visited, terrainDictionary))
        print("Path found to " + str(iterator))
        print(enemyPaths[iterator])
        iterator += 1

        unitMoveMap = numpy.ones((mapY, mapX))*inf
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
    
    # DEBUG: Check initial array state
    print(f"Starting pathfind from ({x}, {y}) to ({goalX}, {goalY})")
    print(f"Initial unitMoveMap shape: {unitMoveMap.shape}")
    print(f"Initial visited shape: {visited.shape}")
    
    directions = [up, down, left, right]
    iterator = 0
    
    while True:
        visited[y][x] = 1
        # DEBUG: Check array before processing
        if len(unitMoveMap) == 0 or len(unitMoveMap[0]) == 0:
            print("ERROR: unitMoveMap became empty during pathfinding!")
            break
            
        for direction in directions:
            nextY, nextX = direction(y, x)
            if validTile(terrainDictionary, simpleMap, unitMoveType, nextX, nextY):
                if visited[nextY][nextX] == 0:
                    tileData = terrainDictionary.get(simpleMap[nextY][nextX])
                    movePenalty = tileData[4+unitMoveType]
                    if movePenalty == "-" or movePenalty.strip() == "":
                        continue
                    temp = float(movePenalty) + float(unitMoveMap[y][x])
                    if temp < unitMoveMap[nextY][nextX]:
                        unitMoveMap[nextY][nextX] = temp
        
        iterator += 1

        t = unitMoveMap.copy()

        
        t[numpy.where(visited)] = inf

        
        # DEBUG: Check if t is valid before calling findMinYX
        if len(t) == 0 or len(t[0]) == 0:
            print("ERROR: t became empty before findMinYX!")
            break
            
        y, x = findMinYX(t)

        
        if x == goalX and y == goalY:
            print("Goal reached!")
            break
            
        # Add iteration limit to prevent infinite loops
        if iterator > 1000:  # Adjust this based on your map size
            print("ERROR: Too many iterations, breaking to prevent infinite loop")
            break

    return backtrack(initX, initY, goalX, goalY, unitMoveMap)



def findMinYX(t):
    xMin = 0
    yMin = 0
    minVal = inf
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


    while True:
        potential_tiles = []
        potential_nodes = []
        directions = [up, down, left, right]
        for direction in directions:
            node = path[-1]
            currX = node[1]
            currY = node[0]
            node = direction(currY, currX)

            if (validSquare(unitMoveMap, node[1], node[0])):
                potential_nodes.append(node)
                potential_tiles.append(unitMoveMap[node[0]][node[1]])
        least_distance_index = numpy.argmin(potential_tiles)
        path.append(potential_nodes[least_distance_index])


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
    tileData = terrainDictionary.get(tile, "Found no tile")
    unitMoveOnTile = tileData[4+unitMoveType]
    if unitMoveOnTile == "-":
        return False
    return True
