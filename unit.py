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
