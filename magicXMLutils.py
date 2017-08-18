from os import getcwd
from inspect import currentframe, getframeinfo, getouterframes

# helper functions for making error messages and info messages
# John Hakala 8/10/17

def getSpot():
  # point you to the spot in the code
  (frame, fileName, lineNumber, functionName, lines, index) = getouterframes(currentframe())[2]
  return "{}:{}".format(fileName.replace(getcwd() + "/", ""), lineNumber)

def error(message):
  # a fatal error
  print "Error [{}]: {}".format(getSpot(), message)
  exit(1)

# optional info. all the "print" statements in the code are typically
# intended for the apache server to parse
# so if you want to debug, it's best not to include 'print' statements in the code
# instead add an info message, and set debug=True below
def info(message, debug=False):
  if debug:
    print "Info [{}]: {}".format(getSpot(), message)
