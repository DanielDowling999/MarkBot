lastkeys = nil
server = nil
ST_sockets = {}
nextID = 1

local KEY_NAMES = { "A", "B", "s", "S", "<", ">", "^", "v", "R", "L" }

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
	local myUnitsData = GetUnitData(address)
	return myUnitsData
end

function GetUnitData(address)
	local iterator = 1
	local data = ''
	--Units take up 72 bytes of data, and as far as I know, if we reach a section of the unitID code with no data, then we have reached the end of the unit list
	while(emu:read16(address)>0x0000) do
		data = data .. emu:readRange(address,72)
		address = address+72
		iterator = iterator +1
	end
	if data == '' then
		data = 'empty'
	end
	console:log("Found " .. tostring(iterator-1) .. " units.")
	return data

end
function GetEnemyData()
	local enemyAddress = 0x0202CEC0
	local enemyData = GetUnitData(enemyAddress)
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
	

function ST_received(id)
	local sock = ST_sockets[id]
	local data = "invalid command"
	local msg
	if not sock then return end
	while true do
		local p, err = sock:receive(1024)
		--console:log(p)
		if p then
			msg = p:match("^(.-)%s*$")
			if msg == "getIsPlayerPhase" then
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
end

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



callbacks:add("keysRead", ST_scankeys)

local port = 8888
server = nil
while not server do
	server, err = socket.bind(nil, port)
	if err then
		if err == socket.ERRORS.ADDRESS_IN_USE then
			port = port + 1
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
