import re
from . import responses
from pathlib import Path

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

# Checks if file provided by client exists in tree
# @file_path -> path of file
# Returns file_path if valid 
def isValidFile(file_path):
   if Path(f"./{file_path}").is_file() is False:
      responses.syntaxError('Image path is not valid')
   return file_path

# Checks if trigger provided by client or server is valid
# @arg -> -t flag value
def isValidTrigger(arg):
   isValid = re.match(r"^(?:skipack|loss)$", arg, re.IGNORECASE)
   if str(isValid) == "None":
       responses.syntaxError("Please provide a valid trigger format (skipack/loss)")

# Checks if reliability provided by client or server is valid
# @arg -> -r flag value
def isValidReliability(arg):
   isValid = re.match(r"^(?:saw|gbn|sr)$", arg, re.IGNORECASE)
   if str(isValid) == "None":
       responses.syntaxError("Please provide a valid reliability format (SAW/GBN/SR)")