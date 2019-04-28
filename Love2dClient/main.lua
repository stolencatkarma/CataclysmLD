function love.threaderror(thread, errorstr)
    print("Thread error!\n"..errorstr)
    -- thread:getError() will return the same error string now.
end


local threadScriptPath = "client_thread.lua"
local clientThread = love.thread.newThread(threadScriptPath)
clientThread:start()


