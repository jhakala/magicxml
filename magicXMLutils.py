from os import getcwd
from inspect import currentframe, getframeinfo, getouterframes

def getSpot():
  (frame, fileName, lineNumber, functionName, lines, index) = getouterframes(currentframe())[2]
  return "{}:{}".format(fileName.replace(getcwd() + "/", ""), lineNumber)

def error(message):
  print "Error [{}]: {}".format(getSpot(), message)
  exit(1)

def info(message, debug=False):
  if debug:
    print "Info [{}]: {}".format(getSpot(), message)
