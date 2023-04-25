from sys import argv
from getopt import getopt
from . import responses, validators

# Optional argumens provided on startup
opts, args = getopt(argv[1:], "scI:p:", ["server", "client", "bind=", "port="])

# Check what mode the process should be ran in
def checkMode():
    for opt, arg in opts:
      if opt in ('-s', '--server'):
          return "server"
      if opt in ('-c', '--client'):
          return "client"  
    # Raise exception if neither -c or -s flag is provided
    responses.syntaxError("You must run either in server or client mode")


# Check for optional arguments for client startup
def checkClientOpts():
    # Default values for ip, port, time, format, interval, parallel and num
    global ip # server IP addres (default localhost)
    ip = "localhost"
    global port # server port (default 8088)
    port = 8080

    # Check default values should be overwritten
    for opt, arg in opts:
        if opt in ('-I', '--serverip'):
          # Validate ip address
          validators.isValidIP(arg)
          ip = arg
        if opt in ('-p', '--port'):
            # Validate port
            arg = int(arg)
            validators.isValidPort(arg)
            port = arg

    return ip, port