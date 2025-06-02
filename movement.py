import numpy
import heapq
from numpy import inf


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
    unitMoveMap = numpy.ones((mapY, mapX))*inf
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

def pqfindShortestPathToAllEnemiesAndTiles(startX, startY, unitMoveMap, goalX, goalY, simpleMap, unitMoveType, terrainDictionary):
    height, width = unitMoveMap.shape
    visited = numpy.zeros_like(unitMoveMap, dtype=bool)
    prev = numpy.full((height, width, 2), -1, dtype=int)

    directions = [up, down, left, right]

    pq=[]

    heapq.heappush(pq, (0, startY, startX))
    unitMoveMap[startY][startX] = 0

    print(f"Starting pathfind from ({startX}, {startY}) to ({goalX}, {goalY})")
    while pq:
        cost, y, x = heapq.heappop(pq)
        if visited[y][x]:
            continue
        if (x, y) == (goalX, goalY):
            print("Goal Reached!")
            break
        for direction in directions:
            ny, nx = direction(y,x)
            #assert 0 <= ny < height and 0 <= nx < width, f"Out of bounds: ({ny}, {nx})"
            if not (0 <= ny < height and 0 <= nx < width):
                continue  # SAFETY FIRST
            if not validTile(terrainDictionary, simpleMap, unitMoveType, nx, ny):
                continue
            if visited[ny][nx]:
                continue
            tileData = terrainDictionary.get(simpleMap[ny][nx])
            try:
                movePenalty = float(tileData[4+unitMoveType])
            except (ValueError, TypeError):
                continue
        newCost = cost + movePenalty

        if newCost < unitMoveMap[ny][nx]:
            unitMoveMap[ny][nx] = newCost
            prev[ny][nx] = [y,x]
            heapq.heappush(pq, (newCost, ny, nx))
    return backtrack(startX, startY, goalX, goalY, prev)

def pqbacktrack(startX, startY, goalX, goalY, prev):
    path = []
    x, y = goalX, goalY
    while (x, y) != (startX, startY):
        path.append((x, y))
        y, x = prev[y][x]
        if (x, y) == (-1, -1):
            return []  # No path
    path.append((startX, startY))
    path.reverse()
    return path
        

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
        #print(f"Loop {iterator}")
        

        # DEBUG: Check array before copying
        #print(f"unitMoveMap shape before copy: {unitMoveMap.shape}")
        t = unitMoveMap.copy()
        #print(f"t shape after copy: {t.shape}")
        
        t[numpy.where(visited)] = inf
        #print(f"t shape after setting visited to inf: {t.shape}")
        
        # DEBUG: Check if t is valid before calling findMinYX
        if len(t) == 0 or len(t[0]) == 0:
            print("ERROR: t became empty before findMinYX!")
            break
            
        y, x = findMinYX(t)
        #print(f"Next node: ({x}, {y})")
        
        if x == goalX and y == goalY:
            print("Goal reached!")
            break
            
        # Add iteration limit to prevent infinite loops
        if iterator > 1000:  # Adjust this based on your map size
            print("ERROR: Too many iterations, breaking to prevent infinite loop")
            break

    return backtrack(initX, initY, goalX, goalY, unitMoveMap)

def OldfindShortestPathToAllEnemiesAndTiles(x, y, unitMoveMap, goalX, goalY, simpleMap, unitMoveType, visited, terrainDictionary):
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
                    if movePenalty == "-" or movePenalty.strip() == "":
                        continue

                    temp = float(movePenalty) + float(unitMoveMap[y][x])
                    # terrainDictionary.get(simpleMap[nextY][nextX])[
                    #    4+unitMoveType]
                    if temp < unitMoveMap[nextY][nextX]:
                        #unitMoveMap[nextY][nextX] = int(temp)
                        unitMoveMap[nextY][nextX] = temp
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
        t[numpy.where(visited)] = inf
        node_index = numpy.argmin(t)
        y, x = findMinYX(t)
        """if unitMoveMap[y][x] == inf:
            print(f"Goal ({goalX}, {goalY}) is unreachable!")
            break  # or handle unreachable case appropriately"""
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
    #print(f"{x}, {y}, {len(simpleMap[0])}, {len(simpleMap)}")
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
