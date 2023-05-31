# might change the fileopener in main to copy this, as dictionary allows for way faster search
def openClassFile(filename):
    lines = {}
    with open(filename, "rt") as f:
        for line in f:
            currLine = line.strip().lower().split(', ')
            lines[currLine[0]] = currLine[1:]
    return lines


class Unit:
    # Notably the unit's con, aid and movement aren't directly accessible from the character's data address. Move and con bonuses are saved here, but will likely need
    # to hardcode the base move and con based on their class.
    unitNameDictionary = {"0xb4cebd08": "Lyn",
                          "0xf8d2bd08": "Sain",
                          "0xc4d2bd08": "Kent"}
    unitClassNameDictionary = {"0x402be08": "Lord (Lyn)",
                               "0x7c0ebe08": "Cavalier",
                               "0x101be08": "Brigand"}
    physWeaponList = [["01", "Iron Sword", ""]]
    magWeaponList = []
    otherList = []
    classList = openClassFile("Data/class.txt")

    def __init__(self, unitData):

        self.id = str(
            hex(unitData[0])) + f'{unitData[1]:{0}2x}' + f'{unitData[2]:{0}2x}' + f'{unitData[3]:{0}2x}'  # f formats the string {0} ensures no leading 0's are deleted
        # f formats the string {0} ensures no leading 0's are deleted
        # self.classId = str(hex(
        #    unitData[4])) + f'{unitData[5]:{0}2x}' + f'{unitData[6]:{0}2x}' + f'{unitData[7]:{0}2x}'
        self.classId = f'{unitData[5]:{0}2x}' + f'{unitData[4]:{0}2x}'
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
        self.inventory = [[unitData[30], unitData[31]], [unitData[32], unitData[33]], [
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
        self.classMoveType = classData[3]
        self.trueMove = int(self.classMove) + int(self.movBonus)
        self.trueCon = int(self.classCon) + int(self.conBonus)
        # self.className = self.getClassName()
        # self.classMove = self.getClassMov()
        # self.classCon = self.getClassCon()
        # self.classMoveType = self.getClassMoveType()
        # self.move = int(self.classMove) + int(self.movBonus)


# Helper functions that only exist if I ever want/need to make things prettier, or ever have a reason to need the unit's name or class name.
# These lists will have to be added to manually, fortunately lists exist online already

    def getUnitName(self):
        return Unit.unitNameDictionary.get(self.id, "Enemy")

    # def getClassName(self):
    #    return Unit.classList.get(self.classId)[0]

    # def getClassMov(self):
    #    return Unit.classList.get(self.classId)[1]

    # def getClassCon(self):
    #    return Unit.classList.get(self.classId)[2]

    # def getClassMoveType(self):
    #    return Unit.classList.get(self.classId)[3]

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
        self.inventory = [[unitData[30], unitData[31]], [unitData[32], unitData[33]], [
            unitData[34], unitData[35]], [unitData[36], unitData[37]], [unitData[38], unitData[39]]]
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
