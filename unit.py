class Unit:
    def __init__(self, unitData):

        self.id = str(
            hex(unitData[0])) + f'{unitData[1]:{0}2x}' + f'{unitData[2]:{0}2x}' + f'{unitData[3]:{0}2x}'  # f formats the string {0} ensures no leading 0's are deleted
        # f formats the string {0} ensures no leading 0's are deleted
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

    # def __init__(self, name, isLord, hp, maxhp, xpos, ypos, stats, mov, inv):
    #    self.name = name
    #    self.isLord = isLord
    #    self.hp = hp
    #    self.maxhp = maxhp
    #    self.xpos = xpos
    #    self.ypos = ypos
    #    self.stats = stats
    #    self.mov = mov
    #    self.inv = inv

    def getId(self):
        return self.id

    def getClassId(self):
        return self.classId

    def getLevel(self):
        return self.level
