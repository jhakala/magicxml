from copy import deepcopy
from os.path import basename
from magicXMLsax import CfgBrick
from magicXMLutils import *

# This class is a special implementation of a CfgBrick that specializes it to parsing RBX delay cfgBricks
# TODO a class like this will be needed for each kind of magicXML
class CfgBrickDelay(CfgBrick):
  def __init__(self, inFileName):
    info("Parsing magic xml {} of type: ngRBX Delays".format(inFileName))
    CfgBrick.__init__(self)
    self.rbx = "test"
    self.qieDelays = {}
    self.tmpDict = {}
    self.tmpFlag = ""
    self.tmpFlags = ["RBX", "Data"]
    self.resultName = "rbxDelays"
    self.outVar = "delay"
    self.outFileName = self.resultName + "_" + basename(inFileName.replace(".xml", ".json"))

  def startElement(self, elementName, attributes):
    if elementName == "Parameter":
      if attributes.getValue("name") == "RBX":
        self.tmpFlag = "RBX"
    if elementName == "Data":
      self.tmpFlag = "Data"
      self.tmpDict = {"qie": attributes.getValue("qie"), "rm":attributes.getValue("rm")}
    

  def contentFiller(self, innerText):
    if self.tmpFlag in self.tmpFlags:
      self.tmpContent = innerText
    
  def endElement(self, elementName):
    if self.tmpFlag == "RBX":
      self.rbx = self.tmpContent
      self.qieDelays[self.rbx]=[]
      self.clearContent()
      self.tmpFlag = ""

    elif self.tmpFlag == "Data":
      self.tmpDict["delay"] = self.tmpContent
      self.clearContent()
      self.qieDelays[self.rbx].append(deepcopy(self.tmpDict))
      self.tmpDict = {}
      self.clearContent()
      self.tmpFlag = ""

  def endDocument(self):
    from john_emapParser import emapper
    # TODO make this settable via argument
    emap = emapper("HCALmapHBHEP17_J.txt")
    emap.parseEmap()

    for channel in emap.listAll():
      foundChannel = False
      #info("channel: " + str(channel))
      if channel["RBX"] in self.qieDelays.keys():
        for qieDelay in self.qieDelays[channel["RBX"]]:
          #info("qieDelay: " + str(qieDelay))
          if channel["RM"] == qieDelay["rm"] and int(channel["card"])*int(channel["QIE"]) == int(qieDelay["qie"]):
            channel["delay"] = qieDelay["delay"]
            foundChannel = True
      if not foundChannel:
        emap.emap.remove(channel)

    self.formatJson(self.outVar, emap.emap, self.outFileName)

  def getOutJSONinfo(self):
    return (self.outFileName, self.outVar)
