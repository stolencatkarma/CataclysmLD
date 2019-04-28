
local json = require("json")

local util = {}

function util.buildCommand(id, command, args)
  local cmdT = {}
  cmdT.ident = id
  cmdT.command = command
  cmdT.args = args
  
  return json.encode(cmdT)
end


return util