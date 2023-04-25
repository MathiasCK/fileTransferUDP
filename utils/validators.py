import re
from . import responses

# Checks if IP address provided by -I flag is valid with regex
# @ip -> string 
def isValidIP(ip):
    if str(ip) == 'localhost':
       return
    isValid = re.match(r"[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}", ip)
    if str(isValid) == "None":
       responses.syntaxError("Please provide a valid IP address")

# Checks if port provided by -p flag is valid within the range 1024 - 65535
# @port -> number 
def isValidPort(port):
   if not int(port) >= 1024 and int(port) <= 65535:
      responses.syntaxError("Please provide a valid port (range 1024 -> 65535)")