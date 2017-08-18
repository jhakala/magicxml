from xml.sax import saxutils, handler, make_parser
from os import path, makedirs
from magicXMLutils import error, info

# base class for defining the parser for any kind of magic xml
# John Hakala 8/10/17

class CfgBrick():
  def __init__(self):
    self.rbx = "test"
    self.tmpContent = ""
    self.tmpKind = "other"
    self.resultName = "test"
    self.outFileName = "blah"
    self.initialized = False

  def clearContent(self):
    self.tmpContent = ""

  def setKind(self, kind):
    self.tmpKind = kind

  def resetKind(self):
    self.tmpKind = "other"

  def startElement(self, elementName, attributes):
    if (elementName == "Parameter"):
      self.setKind(attributes.getValue("name"))
    if (elementName == "Data"):
      self.setKind("Data")

  def contentFiller(self, innerText):
    if not self.initialized:
      self.tmpContent = innerText

  def endElement(self, elementName):
    if self.tmpKind == "RBX":
      self.rbx = self.tmpContent

  def endDocument(self):
    pass

  def formatJson(self, keepKey, emap, outFileName):
    keepKeys = ["side", "eta", "phi", "depth", keepKey]
    for channel in emap:
      for key in channel.keys():
        if not key in keepKeys:
          del channel[key]
        #else:

    import json
    outputDir = "../../html/jhakala/outputJSONs"
    if not (path.exists(outputDir)):
      makedirs(outputDir)
    with open(path.join(outputDir, path.basename(outFileName)), "w") as outFile:
     json.dump(emap, outFile)

  def getOutJSONinfo(self):
    return (["not filled"], "not filled")
  
# this is meant to be a generic sax parser for all the different kind of magic xmls
# to parse different types of magic xmls, you endow its' "self.brick" member object
# which will direct it to pull the particular stuff of interest from the xml
class magicSAX(handler.ContentHandler):
  def __init__(self, inFileName):
    self.brick = CfgBrick()
    handler.ContentHandler.__init__(self)
    self.outDict = {}
    self.inFileName = inFileName
    self.outJSONname = "none"
    self.outVar = "none"
    self.initialized = False

    ## TODO this will need to be changed for all different kinds of magicXMLs
    self.validInfoTypes = ["DELAY", "LED", "ZST"]
  
  def setOutJSONinfo(self):
    (self.outJSONname, self.outVar) = self.brick.getOutJSONinfo()

  # this factory is used so that the handler can inherit specific 
  def CfgBrickFactory(self, infotype):
    #info("CfgBrickFactory was called with infotype " + infotype)
    if not infotype in self.validInfoTypes:
      # for some reason, ZSTs don't have infotypes...
      error("the infotype found was not valid: " + infotype)

    ## TODO this will need to be changed for all different kinds of magicXMLs
    if infotype == "DELAY":
      from cfgBrickDelay import CfgBrickDelay
      self.brick = CfgBrickDelay(self.inFileName)
    elif infotype == "LED":
      from cfgBrickLEDamp import CfgBrickLEDamp
      self.brick = CfgBrickLEDamp(self.inFileName, self.brick.rbx)
    elif infotype == "ZST":
      from cfgBrickZST import CfgBrickZST
      self.brick = CfgBrickZST(self.inFileName)
      #print "constructed CfgBrickZST"
    else:
      error("did not find infotype" + infotype)

  def startElement(self, elementName, attributes):
    self.brick.startElement(elementName, attributes)

  def characters(self, innerText):
    self.brick.contentFiller(innerText)

  def endElement(self, elementName):
    # this infotype parameter should come first
    # based on it, we cast the magicSAX's member "brick" to a particular kind of brick
    # corresponding to a a given kind of magic xml
    # the different bricks it inherits from overload the handler's methods to grab only
    # the relevant chunks from the xml depending on the infotype parameter
    if self.brick.tmpKind == "INFOTYPE":
      self.CfgBrickFactory(self.brick.tmpContent)
      self.initialized = True
      self.brick.initialized = True
      self.brick.clearContent()
    if self.brick.tmpKind == "RBX":
      self.brick.rbx = self.brick.tmpContent
    if self.brick.tmpKind == "TAG" :
      #info("found parameter with name 'TAG'; building ZST cfgBrick.")
      if not self.initialized:
        self.CfgBrickFactory("ZST")
        self.initialized = True
        self.brick.initialized = True
    self.brick.endElement(elementName)

  def endDocument(self):
    self.setOutJSONinfo()
    self.brick.endDocument()

# function to call if you want to dump a json from another python script (e.g. makeAltair.py)
def makeJSON(inputName):
  from os.path import isfile, isdir
  if isfile(inputName):
    inFiles = [inputName]
  elif isdir(inputName):
    inDir = inputName
    from glob import glob
    inFiles = glob("{}/*.xml".format(inputName))
    
  else:
    error("the input specified does not seem to be a valid file or directory: " + inputName)
     
  outJSONnames = []
  saxParser = make_parser()
  for inFile in inFiles:
    saxParser.setContentHandler(magicSAX(inFile))
    saxParser.parse(inFile)
    outJSONnames.append(saxParser.getContentHandler().outJSONname)
  return (outJSONnames, saxParser.getContentHandler().outVar)

