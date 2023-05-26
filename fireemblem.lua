--local address = 0x0202BD50 Unit in Position 1's address
local currUnitAddress = 0x03004690
local address = emu:read32(currUnitAddress)
console:log(tostring(address)) 
local unitNamePointer= emu:read32(address)
console:log(tostring(unitNamePointer))
local unitClassPointer = emu:read32(address+4)
console:log(tostring(unitClassPointer))

local unitLevel = emu:read8(address+8)
console:log(tostring(unitLevel))

local unitExp = emu:read8(address+9)
console:log(tostring(unitExp))

local unitDepolyPos1 = emu:read8(address+10)
console:log(tostring(unitDepolyPos1)) --most likely useless

local unitDeployPos2 = emu:read8(address+11)
console:log(tostring(unitDeployPos2))

local unitStatus = emu:read32(address+12)
console:log(tostring(unitStatus))

local unitXPos = emu:read8(address+16)
console:log("Xpos is " .. tostring(unitXPos))
local unitYPos = emu:read8(address+17)
console:log("Ypos is " .. tostring(unitYPos))
local unitMaxHp = emu:read8(address+18)
console:log("Max hp is " .. tostring(unitMaxHp))
local unitCurrHp = emu:read8(address+19)
console:log("Hp is " .. tostring(unitCurrHp))

local unitStrength = emu:read8(address+20)
console:log(tostring(unitStrength))
local unitSkill = emu:read8(address+21)
console:log(tostring(unitSkill))
local unitSpeed = emu:read8(address+22)
console:log(tostring(unitSpeed))
local unitDefense = emu:read8(address+23)
console:log(tostring(unitDefense))

local unitResistance = emu:read8(address+24)
console:log(tostring(unitResistance))
local unitLuck = emu:read8(address+25)
console:log(tostring(unitLuck))
local unitConstitutionBonus = emu:read8(address+26)
console:log("Unit con bonus is: " .. tostring(unitConstitutionBonus)) 
--unit constituion is calculated as unit con + class con + bonus con. Only the bonus is stored here. Will need to find other solution for full con (may have to hardcode unit+class con per character)
local unitIsRescued = emu:read8(address+27)
console:log(tostring(unitIsRescued))

--Unsure of what the first byte is
--local unsure = emu:read8(address+28)
local unitMoveBonus = emu:read8(address+29)
local unitItem1ID = emu:read8(address+30)
local unitItem1Uses = emu:read8(address+31)
console:log(tostring(unitItem1ID) .. " has " .. tostring(unitItem1Uses) .. " left")
local unitItem2ID = emu:read8(address+32)
local unitItem2Uses = emu:read8(address+33)
console:log(tostring(unitItem2ID) .. " has " .. tostring(unitItem2Uses) .. " left")

local unitItem3ID = emu:read8(address+34)
local unitItem3Uses = emu:read8(address+35)
console:log(tostring(unitItem3ID) .. " has " .. tostring(unitItem3Uses) .. " left")

local unitItem4ID = emu:read8(address+36)
local unitItem4Uses = emu:read8(address+37)
console:log(tostring(unitItem4ID) .. " has " .. tostring(unitItem4Uses) .. " left")

local unitItem5ID = emu:read8(address+38)
local unitItem5Uses = emu:read8(address+39)
console:log(tostring(unitItem5ID) .. " has " .. tostring(unitItem5Uses) .. " left")
