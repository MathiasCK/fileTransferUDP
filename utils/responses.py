# Internal server custom error
# @err -> string
def err(err):
    print(f"Error: {repr(err)}")
    # Exit excecution
    exit()

# Connection refused custom error
# @err -> string
def connectionRefused(err):
    print(f"Failed to connect: {repr(err)}")
    exit()

# Connection custom error
# @err -> string
def connectionError(err):
    print(f"Connection error: {repr(err)}")
    exit()

# Keyboard interrupt custom error
def keyBoardInterrupt():
    print("Stopped by Ctrl+C")
    exit()

# Connection aborted custom error
def connectionAbortedError():
    print("Connection aborted")
    exit()

# Syntax custom error
# @msg -> string
def syntaxError(msg):
    raise SyntaxError(msg)