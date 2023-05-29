import socket
from unit import Unit


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


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect(('localhost', 8888))
    print('Connected to server')

    command = 'console:log("Hello")'
    s.sendall(command.encode())
    print('Sent command to mgba api: ', command)

    data = s.recv(1024)
    print('Recieved response from api: ', data)
    enemyData = s.recv(1024)
    print('Recieved enemy from api')

unitData = list(data)
unitList = storeUnits(unitData)
eneData = list(enemyData)
enemyList = storeUnits(enemyData)

# Lyn = Unit(unitData)
# print("The character's id is: " + Lyn.getId() +
#      ", and their class ID is " + Lyn.getClassId())
# print("The character's first inventory slot has an item with the id of: " +
#      str(Lyn.inventory[0][0]) + " and has this many uses: " + str(Lyn.inventory[0][1]))
# print("Recieved all neccessary bits? " + str(hex(Lyn.weaponRanks[0])))

for x in range(len(unitList)):
    print("This unit's id is : " +
          unitList[x].id + ", and their class id is " + unitList[x].classId)
    print("This unit's name is " + unitList[x].getUnitName() +
          ", and their class is " + unitList[x].getClassName())
for x in range(len(enemyList)):
    print("This enemy's id is : " +
          enemyList[x].id + ", and their class id is " + enemyList[x].classId)
