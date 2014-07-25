# config file for overlord agent

AGENT_HOSTNAME = "fe" # Must be the same as in DB
AGENT_AUTHKEY = "none" # Not implemented
SERVER_LISTEN = "http://fe:8081/listen"
SERVER_GETJOBS = "http://fe:8081/getjobs"
INTERVAL = 15 # Seconds
PID_FILE = "/tmp/overlord_agent.pid"

CPU_BUSY = 50 # Percent
NET_BUSY = 10240000 # Bytes
