# might change the fileopener in main to copy this, as dictionary allows for way faster search
def openClassFile(filename):
    lines = {}
    with open(filename, "rt") as f:
        for line in f:
            currLine = line.strip().lower().split(', ')
            lines[currLine[0]] = currLine[1:]
    return lines


def openItemFile(filename):
    with open(filename, "rt") as f:
        lines = [line.strip().split(', ') for line in f]
    return lines


class Unit:
    # Notably the unit's con, aid and movement aren't directly accessible from the character's data address. Move and con bonuses are saved here, but will likely need
    # to hardcode the base move and con based on their class.

    # physWeaponList = [["01", "Iron Sword", ""]]
    # magWeaponList = []
    # otherList = []
    classList = openClassFile("Data/class.txt")
    nameList = openClassFile("Data/units.txt")
    # itemList = openClassFile("Data/items.txt")
    itemList = openClassFile("Data/items.txt")
    physWeaponList = openClassFile("Data/physWeapons.txt")
    magWeaponList = openClassFile("Data/magWeapons.txt")
    staveList = openItemFile("Data/staves.txt")
    weaponRanksList = {"sword": 0, "lance": 1, "axe": 2,
                       "bow": 3, "staff": 4, "anima": 5, "light": 6, "dark": 7}
    minWeaponRanksList = {"-": 0x00, "e": 0x01, "d": 0x1F,
                          "c": 0x47, "b": 0x79, "a": 0xB5, "s": 0xFB}
    # order is Sword, Lance, Axe, Bow, Staff, Anima, Light, Dark}

    def __init__(self, unitData):
        # f formats the string {0} ensures no leading 0's are deleted
        self.id = str(
            hex(unitData[0])) + f'{unitData[1]:{0}2x}' + f'{unitData[2]:{0}2x}' + f'{unitData[3]:{0}2x}'
        self.nameId = f'{unitData[1]:{0}2x}' + f'{unitData[0]:{0}2x}'



        self.classId = f'{unitData[5]:{0}2x}' + f'{unitData[4]:{0}2x}'
        self.level = unitData[8]
        self.exp = unitData[9]
        self.deployPos = unitData[11]
        self.status = unitData[12:16]
        self.alive = unitData[12]
        self.xpos = unitData[16]
        self.ypos = unitData[17]
        self.maxHP = int(unitData[18])
        self.currHP = int(unitData[19])
        self.strength = int(unitData[20])
        self.skill = int(unitData[21])
        self.speed = int(unitData[22])
        self.defense = int(unitData[23])
        self.res = int(unitData[24])
        self.luck = int(unitData[25])
        self.conBonus = unitData[26]
        self.isRescued = unitData[27]
        # 28 seems to be useless, and 29 is assumed to be the movebonus until I can test properly
        self.movBonus = unitData[29]
        invData = [[unitData[30], unitData[31]], [unitData[32], unitData[33]], [
            unitData[34], unitData[35]], [unitData[36], unitData[37]], [unitData[38], unitData[39]]]
        
        self.hasMoved = False

        # 00 - weapon disabled
        # 01 through 1E - Skill level E
        # 1F through 46 - Skill level D
        # 47 through 78 - Skill level C
        # 79 through B4 - Skill level B
        # B5 through FA - Skill level A
        # FB through FF - Skill level S
        # order is Sword, Lance, Axe, Bow, Staff, Anima, Light, Dark
        self.weaponRanks = [unitData[40], unitData[41], unitData[42],
                            unitData[43], unitData[44], unitData[45], unitData[46], unitData[47]]
        classData = Unit.classList.get(self.classId)
        self.className = classData[0]
        self.classMove = classData[1]
        self.classCon = classData[2]
        # need to check dancer movement type manually, since it isn't on the website
        self.classMoveType = classData[3]
        self.classMoveId = int(classData[4])
        self.trueMove = int(self.classMove) + int(self.movBonus)
        self.trueCon = int(self.classCon) + int(self.conBonus)
        self.name = Unit.nameList.get(self.nameId, "E")[0]
        self.fullInv = Unit.fillInventory(self, invData)
        self.maxRange, self.minRange = Unit.findMinMaxRanges(self)
        self.ranges = Unit.findRanges(self)


            #When a unit dies, a flag is set that changes their status. However, this seems to be frustratingly inconsistent. I have seen 3 values so far denoting a dead unit.
    def isAlive(self):
        return not (self.alive == 0xD or self.alive == 0x4 or self.alive == 0x5)
    


        # self.maxRange = self.findMaxRange(self.inventory, self.weaponRanks)
        # self.className = self.getClassName()
        # self.classMove = self.getClassMov()
        # self.classCon = self.getClassCon()
        # self.classMoveType = self.getClassMoveType()
        # self.move = int(self.classMove) + int(self.movBonus)


# Helper functions that only exist if I ever want/need to make things prettier, or ever have a reason to need the unit's name or class name.
# These lists will have to be added to manually, fortunately lists exist online already

    # def getClassName(self):
    #    return Unit.classList.get(self.classId)[0]

    # def getClassMov(self):
    #    return Unit.classList.get(self.classId)[1]

    # def getClassCon(self):
    #    return Unit.classList.get(self.classId)[2]

    # def getClassMoveType(self):
    #    return Unit.classList.get(self.classId)[3]



# Better way to do this could be to convert the inventory to contain all the weapon and items actual stats, along with a flag of whether
# or not they can use it, then just pull the longest range one when calcing range.

#Note, a minor bug seems to exist with item position. Some items will be marked at different positions than they actually are. However, so far these values are being interpreted correctly (i.e, it will still press enough buttons to stop on the right item)
    def fillInventory(self, invData):
        fullInv = []
        itemPos = 0
        for item in invData:
            canUse = False
            currItem = []
            if (item[0] == 0):
                itemPos += 1
                continue
            isItem = Unit.itemList.get(hex(item[0]), False)
            if isItem:
                currItem = [isItem, item[1]]
                print(currItem)
                currItem.append(itemPos)
                currItem.append("ITEM")
                fullInv.append(currItem)
                itemPos += 1

                continue
            physWeapon = Unit.physWeaponList.get(hex(item[0]), False)
            if physWeapon:
                physWeaponType = Unit.weaponRanksList.get(physWeapon[1])
                physWeaponRank = physWeapon[2]
                currItem = [physWeapon, item[1]]
                if physWeaponRank == "prfl":
                    if (self.className == "lord (lyn)"):
                        canUse = True
                elif self.weaponRanks[physWeaponType] >= Unit.minWeaponRanksList.get(physWeaponRank):
                    canUse = True
                # print(physWeapon)
                currItem.append(canUse)
                currItem.append(itemPos)
                fullInv.append(currItem)
                itemPos += 1
                # print(Unit.physWeaponList.get("0x1"))
                continue
            magWeapon = Unit.magWeaponList.get(hex(item[0]), False)
            if magWeapon:
                magWeaponType = Unit.weaponRanksList.get(magWeapon[1])
                magWeaponRank = magWeapon[2]
                currItem = [magWeapon, item[1]]
                if self.weaponRanks[magWeaponType] >= Unit.minWeaponRanksList.get(magWeaponRank):
                    canUse = True
                currItem.append(canUse)
                currItem.append(itemPos)
                fullInv.append(currItem)
                itemPos += 1
                continue
            print("Invalid item")
            itemPos += 1

        return fullInv

# should adjust this (and the actual data) to have the min and max range of a weapon built into it, to account for 1-2 range weapons and siege weapons
    def findRanges(self):
        ranges = []
        for item in self.fullInv:
            if item[3] == "ITEM":
                continue
            if item[2]:
                tempRange = int(item[0][7])
                if tempRange in ranges:
                    continue
                ranges.append(tempRange)

        if not ranges:
            ranges.append(0)
        return ranges

    def findMinMaxRanges(self):

        maxRange = 0
        minRange = 30
        # itemPos = 0
        for item in self.fullInv:
            # if it's not a weapon, go to the next item slot
            if item[3] == "ITEM":
                continue
            # if item is usable by unit
            if item[2]:
                tempRange = int(item[0][7])
                if tempRange < minRange:
                    minRange = tempRange
                if tempRange > maxRange:
                    maxRange = tempRange
        # if minRange = 30 it means the unit has no usable weapons
        return maxRange, minRange

    # Check if unit can use weapon type
    # Check if unit has a high enough weapon rank
    # Check if range > maxRange (and range < minRange)

    def updateUnit(self, unitData):
        self.classId = str(hex(
            unitData[4])) + f'{unitData[5]:{0}2x}' + f'{unitData[6]:{0}2x}' + f'{unitData[7]:{0}2x}'
        self.level = unitData[8]
        self.exp = unitData[9]
        self.deployPos = unitData[11]
        self.status = unitData[12:16]
        self.xpos = unitData[16]
        self.ypos = unitData[17]
        self.maxHP = unitData[18]
        self.currHP = unitData[19]
        self.strength = unitData[20]
        self.skill = unitData[21]
        self.speed = unitData[22]
        self.defense = unitData[23]
        self.res = unitData[24]
        self.luck = unitData[25]
        self.conBonus = unitData[26]
        self.isRescued = unitData[27]
        # 28 seems to be useless, and 29 is assumed to be the movebonus until I can test properly
        self.movBonus = unitData[29]

        # self.inventory = [[unitData[30], unitData[31]], [unitData[32], unitData[33]], [
        #    unitData[34], unitData[35]], [unitData[36], unitData[37]], [unitData[38], unitData[39]]]
        # 00 - weapon disabled
        # 01 through 1E - Skill level E
        # 1F through 46 - Skill level D
        # 47 through 78 - Skill level C
        # 79 through B4 - Skill level B
        # B5 through FA - Skill level A
        # FB through FF - Skill level S
        # order is Sword, Lance, Axe, Bow, Staff, Anima, Light, Dark
        self.weaponRanks = [unitData[40], unitData[41], unitData[42],
                            unitData[43], unitData[44], unitData[45], unitData[46], unitData[47]]

    def printUnitInformation(self):
        print("Unit Name: " + self.name + "\nUnit Class: " + self.className + "\nUnit Level: " +
              str(self.level) + "\nI am at x: " + str(self.xpos) + " and y: " + str(self.ypos))

    def getHealingItems(self):
        itemPos = 0
        for items in self.fullInv:
            print(items[itemPos])
            if (items[0] == ['vulnerary']):
                return itemPos
            itemPos += 1
        return -1
