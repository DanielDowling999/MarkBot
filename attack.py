from unit import Unit


def calcPhysAttack(unitStrength, enemyDef):
    unitAttack = unitStrength - enemyDef
    return unitAttack


def calcBestAttack(unit, enemiesInRange):
    return unit.inventory


def calcMagAttack(unitMag, enemyRes):
    unitAttack = unitMag - enemyRes
    return unitAttack


def main(unit, enemiesInRange):
    return (calcBestAttack(unit, enemiesInRange))

# will eventually need to account for accuracy and crit, but will keep it basic for now
