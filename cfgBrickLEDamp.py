from copy import deepcopy
from os.path import basename
from magicXMLsax import CfgBrick
from magicXMLutils import *

# This class is a special implementation of a CfgBrick that specializes it to parsing LED amplitude cfgBricks
# TODO a class like this will be needed for each kind of magicXML
class CfgBrickLEDamp(CfgBrick):
  def __init__(self, inFileName, rbx):
    info("Parsing magic xml {} of type: LED amplitudes".format(inFileName))
    CfgBrick.__init__(self)
    self.ledAmps = {}
    self.tmpDict = {}
    self.rbx = rbx
    self.tmpFlag = ""
    self.tmpFlags = ["RBX", "amplitude"]
    self.resultName = "ledAmplitudes"
    self.outVar = "amplitude"
    self.outFileName = self.resultName + "_" + basename(inFileName.replace(".xml", ".json"))
    if self.rbx != "test":
      self.ledAmps[self.rbx] = []

  def startElement(self, elementName, attributes):
    #info("begin element with name " + elementName)
    if elementName == "Parameter":
      if attributes.getValue("name") == "RBX":
        self.tmpFlag = "RBX"
    if elementName == "Data":
      if attributes.getValue("item") == "amplitude":
        self.tmpFlag = "amplitude"
    

  def contentFiller(self, innerText):
    if self.tmpFlag in self.tmpFlags:
      self.tmpContent = innerText
      #info("tmpContent set to: "  + self.tmpContent)
    
  def endElement(self, elementName):
    #info("end element with name " + elementName)
    if elementName == "Parameter":
      if self.tmpFlag == "RBX":
        self.rbx = self.tmpContent
        self.ledAmps[self.rbx]=[]
        #self.clearContent()

    elif elementName == "CFGBrick":
      self.tmpDict["amplitude"] = self.tmpContent
      self.clearContent()
      self.ledAmps[self.rbx].append(deepcopy(self.tmpDict))
      self.tmpDict = {}
    self.tmpFlag = ""
     
      

  def endDocument(self):
    from john_emapParser import emapper
    # TODO make this settable via argument
    emap = emapper("HCALmapHBHElegacy_J.txt")
    emap.parseEmap()

    for channel in emap.listAll():
      foundChannel = False
      if channel["rbx"] in self.ledAmps.keys():
        for ledAmp in self.ledAmps[channel["rbx"]]:
            channel["amplitude"] = ledAmp["amplitude"]
            foundChannel = True
      if not foundChannel:
        emap.emap.remove(channel)

    keepKey = self.outVar
    self.formatJson(keepKey, emap.emap, self.outFileName)

  def getOutJSONinfo(self):
    return (self.outFileName, self.outVar)
