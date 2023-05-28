import socket
from unit import Unit

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

# unitData = list(data)
# Lyn = Unit(unitData)
# print("The character's id is: " + Lyn.getId() +
#      ", and their class ID is " + Lyn.getClassId())
# print("The character's first inventory slot has an item with the id of: " +
#      str(Lyn.inventory[0][0]) + " and has this many uses: " + str(Lyn.inventory[0][1]))
# print("Recieved all neccessary bits? " + str(hex(Lyn.weaponRanks[0])))

eneData = list(enemyData)
enemyList = []
startAddress = 0
endAddress = 72
for x in range(5):
    enemyList.append(Unit(eneData[startAddress:endAddress]))
    startAddress = endAddress
    endAddress += 72

for x in range(5):
    print("This enemy's id is : " +
          enemyList[x].getId() + ", and their class id is " + enemyList[x].getClassId())

# unitID = unitData[0:4]
# unitClassID = unitData[4:8]
# unitLevel = unitData[8:10]

# for u in unitID:
#    print(hex(u))

# for u in unitClassID:
#    print(hex(u))