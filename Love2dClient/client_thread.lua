print("Start!")

local socket = require("socket")

local util = require("util")

local ccfg = require("client_cfg")


local client = socket.tcp()

client:setoption("keepalive", true)
client:setoption("reuseaddr", true)
client:settimeout(-1)

assert(client:connect(ccfg.ip, ccfg.port))

repeat
    local cmd = util.buildCommand("test", "ping", "[]")
    print(cmd)
    client:send(cmd)

    print("Message request sent! Waiting for message...")
    data, errormsg = client:receive()

    if data then
        print("Message received!")
        print(data)
    else
        print(errormsg)
        break
    end
until not client

print("Thread!")
client:shutdown("both")
os.exit()