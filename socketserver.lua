lastkeys = nil
server = nil
ST_sockets = {}
nextID = 1
command_queue = {} --[[using a queue because, with a persistent connection, the commands come in too quickly
causing the data to get corrupted]]--

local KEY_NAMES = { "A", "B", "s", "S", "<", ">", "^", "v", "R", "L" }

local INPUT_KEYS = {
	["A"] = C.GBA_KEY.A,
	["B"] = C.GBA_KEY.B,
	["UP"] = C.GBA_KEY.UP,
	["DOWN"] = C.GBA_KEY.DOWN,
	["LEFT"] = C.GBA_KEY.LEFT,
	["RIGHT"] = C.GBA_KEY.RIGHT,
	["START"] = C.GBA_KEY.START,
	["SELECT"] = C.GBA_KEY.SELECT,
	["L"] = C.GBA_KEY.L,
	["R"] = C.GBA_KEY.R
}
function ST_stop(id)
	local sock = ST_sockets[id]
	ST_sockets[id] = nil
	sock:close()
end

function ST_format(id, msg, isError)
	local prefix = "Socket " .. id
	if isError then
		prefix = prefix .. " Error: "
	else
		prefix = prefix .. " Received: "
	end
	return prefix .. msg
end

function ST_error(id, err)
	console:error(ST_format(id, err, true))
	ST_stop(id)
end

--If retrieving the current unit is ever desirable outside of using the GetUnitData function
function GetCurrUnitData()
    local currUnitAddress = 0x03004690
    local address = emu:read32(currUnitAddress)
    local unitData = emu:readRange(address,72)
    return unitData
end
--Suite of functions to retrieve player and enemy unit data. Will eventually need one for green 'ally' units as well
function GetMyUnitData()
	local address = 0x202BD50
	local maxPlayerUnits = 20 --Should be higher than is actually possible in game, but I want to leave a small buffer in case there's a chapter with a lot of reinforcements.
	local myUnitsData = GetUnitData(address, maxPlayerUnits)
	return myUnitsData
end

function GetUnitData(address, count)
	--local iterator = 1
	local data = ''
	local validUnits = 0
	--Units take up 72 bytes of data, and as far as I know, if we reach a section of the unitID code with no data, then we have reached the end of the unit list
	for i = 0, count - 1 do
		local unitAddr = address+(i*72)
		local unitID = emu:read16(unitAddr)
		if unitID > 0x0000 then
			data = data .. emu:readRange(unitAddr, 72)
			validUnits = validUnits + 1
		end
	end

	--[[while(emu:read16(address)>0x0000) do
		data = data .. emu:readRange(address,72)
		address = address+72
		iterator = iterator +1
	end]]
	if data == '' then
		data = 'empty'
	end
	console:log("Found " .. tostring(validUnits) .. " units.")
	return data

end

--[[function GetUnitDataFromPointerTable(ptrTableAddr)
	local unitData = ""
	local numUnits = 0

	for i = 0, 31 do
		local ptr = emu:read32(ptrTableAddr + i * 4)
		if ptr ~= 0 and ptr >= 0x02000000 and ptr < 0x03000000 then
			console:log(string.format("Reading unit from ptr: 0x%08X", ptr))

			unitData = unitData .. emu:readRange(ptr, 72)
			numUnits = numUnits + 1
		else
			console:log(string.format("Skipping invalid unit ptr: 0x%08X", ptr))

		end
	
	end

	console:log("Found " .. tostring(numUnits) .. " valid units.")
	return unitData
end
function GetMyUnitData()
	return GetUnitDataFromPointerTable(0x202BD50)
end--]]

function GetEnemyData()
	local enemyAddress = 0x0202CEC0
	local maxEnemies = 50 --This is a hard-coded limit of the game, there will never be more than 50 enemies at once.
	local enemyData = GetUnitData(enemyAddress, maxEnemies)
	return enemyData
end

function GetMoney()
	local money = emu:read16(0x0202BC00)
	console:log("Found Money")
	return money
end

function GetPlayerPhase()
	if emu:read8(0x0202BBF8+15) == 0x0 then
		return 'T'
	end
	return 'F'
end

function GetChapterID()
	console:log("Running branched version.")
	return emu:read8(0x0202BC06)
end
function GetMapData()
	--Get tile range
	local mapDataSize = (emu:read8(0x0202E3D8)+2)*emu:read8(0x0202E3DA)
	local fe7TerrainAddress = 0x0202E3E0
	local address = emu:read32(fe7TerrainAddress)
	--0202EBB8
	local mapAddress = emu:read32(address)
	--0202EC0A
	local terrainData = emu:readRange(mapAddress, mapDataSize)
	return terrainData
end

function GetMapSize()
	local mapsize = emu:readRange(0x0202E3D8,4)
	--local mapy = emu:read16(0x202E3)
	--console:log(mapsize)
	return mapsize
end

local next_frame = 30
function frame_callback()
    next_frame = next_frame-1
    if next_frame > 0 then
        return
    end
    next_frame = 30
end

local turnOn = {}
local turnOff = {}

function onKeysRead()
  for _, k in ipairs(turnOff) do
    emu:clearKey(INPUT_KEYS[k])
	console:log("Cleared key " .. k)
  end
  turnOff = {}
  for _, k in ipairs(turnOn) do
    emu:addKey(INPUT_KEYS[k])
	console:log("Added key " .. k)
    table.insert(turnOff, k)
  end
  turnOn = {}
end

function DoInput(input)
  table.insert(turnOn, input)
end

callbacks:add('keysRead', onKeysRead)
local buffer = ""
function ST_received(id)
	local sock = ST_sockets[id]
	if not sock then return end

	while true do
		local p, err = sock:receive(1024)
		if p then
        	buffer = buffer .. p
        	for msg in buffer:gmatch("([^\n]+)\n") do
            	console:log("Queued command: " .. msg)
            	table.insert(command_queue, {id = id, cmd = msg})
        	end
        	buffer = buffer:match("[^\n]*$") or ""
   		else
        	if err ~= socket.ERRORS.AGAIN then
            	console:error("Socket error: " .. tostring(err))
            	ST_stop(id)
        	end
        	break
    	end
	end
end
--[[
		if p then
			for msg in p:gmatch("[^\r\n]+") do
				msg = msg:match("^(.-)%s*$")
				console:log("Queued command: " .. msg)
				table.insert(command_queue, {id = id, cmd = msg})
			end
		else
			if err ~= socket.ERRORS.AGAIN then
				console:error("Socket error: " .. tostring(err))
				ST_stop(id)
			end
			break
		end
	end
end]]

function ST_process_commands()
	--# gets length of sequence
	while #command_queue > 0 do
		local request = table.remove(command_queue, 1)
		local sock = ST_sockets[request.id]
		local cmd = request.cmd
		local data = "Empty Response"
		local shouldRespond = true

		if cmd == "pressLeft" then 
			DoInput("LEFT")
			shouldRespond = false
		elseif cmd=="pressRight" then
			DoInput("RIGHT")
			shouldRespond = false
		elseif cmd=="pressUp" then
			DoInput("UP")
			shouldRespond = false
		elseif cmd == "pressDown" then
			DoInput("DOWN")
			shouldRespond = false
		elseif cmd == "pressA" then
			DoInput("A")
			shouldRespond = false
		elseif cmd == "pressB" then
			DoInput("B")
			shouldRespond = false
		elseif cmd == "pressL" then 
			DoInput("L")
			shouldRespond = false
		elseif cmd == "pressR" then
			DoInput("R")
			shouldRespond = false
		elseif cmd == "pressStart" then 
			DoInput("START")
			shouldRespond = false
		elseif cmd== "pressSelect" then
			DoInput("SELECT")
			shouldRespond = false
		elseif cmd == "getIsPlayerPhase" then
			data = GetPlayerPhase()
			console:log("Successfully retrieved player phase")
		elseif cmd == "getUnits" then
			data = GetMyUnitData()
			console:log("Successfully Collected Units")
		elseif cmd == "getEnemies" then
			data = GetEnemyData()
			console:log("Successfully Collected Enemies")
		elseif cmd == "getMoney" then
			data = GetMoney()
			console:log("Successfully retrieved Money")
		elseif cmd == "getMapSize" then
			data = GetMapSize()
			console:log("Successfully retrieved Map Size")
		elseif cmd == "getMap" then
			data = GetMapData()
			console:log("Sucessfully retrieved Map Data")
		elseif cmd == "getChapterID" then
			data = GetChapterID()
			console:log("Successfully retrieved Chapter ID")
		end

		if sock and shouldRespond then
			if data == 'empty' then
				sock:send(string.pack(">I4", 0))
			
			else
				if type(data) ~= "string" then
					console:error("Data is not a string! Type: " .. type(data))
					data = string.char(data)
				end
				local len = #data
				--console:log("Sending data of length: " .. tostring(len))

				local header = string.pack(">I4", len)
				--console:log("Header bytes (hex): " .. header:gsub(".", function(c) return string.format("%02X ", string.byte(c)) end))

				--console:log("Final sent length: " .. tostring(len))
				--console:log("First few bytes (hex): " .. data:sub(1,16):gsub(".", function(c) return string.format("%02X ", string.byte(c)) end))

				sock:send(string.pack(">I4", #data) .. data)
			end
		end
	end
end

callbacks:add("frame", ST_process_commands)


	
--[[
function ST_received(id)
	local sock = ST_sockets[id]
	local data = "Empty Response"
	local msg
	if not sock then return end
	while true do
		local p, err = sock:receive(1024)
		--console:log(p)
		if p then
			msg = p:match("^(.-)%s*$")
			if msg == "pressLeft" then 
				DoInput("LEFT")
			elseif msg=="pressRight" then
				DoInput("RIGHT")
			elseif msg=="pressUp" then
				DoInput("UP")
			elseif msg == "pressDown" then
				DoInput("DOWN")
			elseif msg == "pressA" then
				DoInput("A")
			elseif msg == "pressB" then
				DoInput("B")
			elseif msg == "pressL" then 
				DoInput("L")
			elseif msg == "pressR" then
				DoInput("R")
			elseif msg == "pressStart" then 
				DoInput("START")
			elseif msg== "pressSelect" then
				DoInput("SELECT")
			elseif msg == "getIsPlayerPhase" then
				data = GetPlayerPhase()
				console:log("Successfully retrieved player phase")
			elseif msg == "getUnits" then
				data = GetMyUnitData()
				console:log("Successfully Collected Units")
			elseif msg == "getEnemies" then
				data = GetEnemyData()
				console:log("Successfully Collected Enemies")
			elseif msg == "getMoney" then
				data = GetMoney()
				console:log("Successfully retrieved Money")
			elseif msg == "getMapSize" then
				data = GetMapSize()
				console:log("Successfully retrieved Map Size")
			elseif msg == "getMap" then
				data = GetMapData()
				console:log("Sucessfully retrieved Map Data")
			elseif msg == "getChapterID" then
				data = GetChapterID()
				console:log("Successfully retrieved Chapter ID")
			end
			
			console:log(ST_format(id, p:match("^(.-)%s*$")))
			sock:send(data)
		else
			if err ~= socket.ERRORS.AGAIN then
				console:error(ST_format(id, err, true))
				ST_stop(id)
			end
			return
		end
	end
end]]--
--[[
function ST_received(id)
	local sock = ST_sockets[id]
	if not sock then return end

	local p, err = sock:receive(1024)
	if p then
		local msg = p:match("^(.-)%s*$")
		local data = "Empty Response"
		if msg == "pressLeft" then 
				DoInput("LEFT")
			elseif msg=="pressRight" then
				DoInput("RIGHT")
			elseif msg=="pressUp" then
				DoInput("UP")
			elseif msg == "pressDown" then
				DoInput("DOWN")
			elseif msg == "pressA" then
				DoInput("A")
			elseif msg == "pressB" then
				DoInput("B")
			elseif msg == "pressL" then 
				DoInput("L")
			elseif msg == "pressR" then
				DoInput("R")
			elseif msg == "pressStart" then 
				DoInput("START")
			elseif msg== "pressSelect" then
				DoInput("SELECT")
			elseif msg == "getIsPlayerPhase" then
				data = GetPlayerPhase()
				console:log("Successfully retrieved player phase")
			elseif msg == "getUnits" then
				data = GetMyUnitData()
				console:log("Successfully Collected Units")
			elseif msg == "getEnemies" then
				data = GetEnemyData()
				console:log("Successfully Collected Enemies")
			elseif msg == "getMoney" then
				data = GetMoney()
				console:log("Successfully retrieved Money")
			elseif msg == "getMapSize" then
				data = GetMapSize()
				console:log("Successfully retrieved Map Size")
			elseif msg == "getMap" then
				data = GetMapData()
				console:log("Sucessfully retrieved Map Data")
			elseif msg == "getChapterID" then
				data = GetChapterID()
				console:log("Successfully retrieved Chapter ID")
			end
			
			console:log(ST_format(id, p:match("^(.-)%s*$")))
			sock:send(data)
		else
			if err ~= socket.ERRORS.AGAIN then
				console:error(ST_format(id, err, true))
				ST_stop(id)
			end
		end
	end
]]



function ST_scankeys()
	local keys = emu:getKeys()
	if keys ~= lastkeys then
		lastkeys = keys
		local msg = "["
		for i, k in ipairs(KEY_NAMES) do
			if (keys & (1 << (i - 1))) == 0 then
				msg = msg .. " "
			else
				msg = msg .. k;
			end
		end
		msg = msg .. "]\n"
		for id, sock in pairs(ST_sockets) do
			if sock then sock:send(msg) end
		end
	end
end

function ST_accept()
	local sock, err = server:accept()
	if err then
		console:error(ST_format("Accept", err, true))
		return
	end
	local id = nextID
	nextID = id + 1
	ST_sockets[id] = sock
	sock:add("received", function() ST_received(id) end)
	sock:add("error", function() ST_error(id) end)
	console:log(ST_format(id, "Connected"))
end



--callbacks:add("keysRead", ST_scankeys)

local port = 8888
server = nil
while not server do
	server, err = socket.bind(nil, port)
	if err then
		if err == socket.ERRORS.ADDRESS_IN_USE then
			--port = port + 1
			console:error("Failed to bind to port " .. port .. ": " .. tostring(err))
		else
			console:error(ST_format("Bind", err, true))
			break
		end
	else
		local ok
		ok, err = server:listen()
		if err then
			server:close()
			console:error(ST_format("Listen", err, true))
		else
			console:log("Socket Server Test: Listening on port " .. port)
			server:add("received", ST_accept)
		end
	end
end
