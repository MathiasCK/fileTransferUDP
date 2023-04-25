from sys import argv
from getopt import getopt
from . import responses

# Optional argumens provided on startup
opts, args = getopt(argv[1:], "sc", ["server", "client"])

# Check what mode the process should be ran in
def checkMode():
    for opt, arg in opts:
      if opt in ('-s', '--server'):
          return "server"
      if opt in ('-c', '--client'):
          return "client"  
    # Raise exception if neither -c or -s flag is provided
    responses.syntaxError("You must run either in server or client mode")