from copy import deepcopy
from os.path import basename
from magicXMLsax import CfgBrick
from magicXMLutils import *

# This class is a special implementation of a CfgBrick that specializes it to parsing zero suppression threshold cfgBricks
# TODO a class like this will be needed for each kind of magicXML
# John Hakala 8/18/17
class CfgBrickZST(CfgBrick):
  def __init__(self, inFileName):
    info("Parsing magic xml {} of type: zero suppression thresholds".format(inFileName))
    CfgBrick.__init__(self)
    self.zsts = []
    self.tmpDict = {}
    self.tmpKinds = ["CRATE", "SLOT", "Data"]
    self.tmpCrate = ""
    self.tmpSlot = ""
    self.tmpZSTs = ""
    self.resultName = "uHTRzsts"
    self.outVar = "zst"
    self.outFileName = self.resultName + "_" + basename(inFileName.replace(".xml", ".json"))


  def contentFiller(self, innerText):
    if self.tmpKind in self.tmpKinds:
      self.tmpContent = innerText
    #print self.tmpContent
    
  def endElement(self, elementName):
    if elementName == "Parameter":
      if self.tmpKind == "CRATE":
        self.tmpCrate = self.tmpContent
        self.clearContent()
      if self.tmpKind == "SLOT":
        self.tmpSlot = self.tmpContent
        self.clearContent()

    if elementName == "Data":
      self.tmpZSTs = self.tmpContent
      self.clearContent()
    
    if elementName == "CFGBrick":
      #info("reached the end of element with name: " + elementName)
      iCh = 0
      #info("self.tmpZSTs: " + self.tmpZSTs)
      #info("ZSTs: " + self.tmpZSTs)
      for ZST in self.tmpZSTs.split():
        self.tmpDict = {}
        self.tmpDict["crate"] = self.tmpCrate
        self.tmpDict["uhtr"] = self.tmpSlot
        self.tmpDict["uhtr_fi"] = str(int(iCh / 3))
        self.tmpDict["fi_ch"] = str(iCh % 3)
        self.tmpDict["zst"] = str(ZST)
        self.zsts.append(self.tmpDict)
        #info("iCh " + str(iCh) + " got mapped to fiber " + self.tmpDict["uhtr_fi"] + " channel " + self.tmpDict["fi_ch"])
        iCh += 1
        

  def endDocument(self):
    from john_emapParser import emapper
    emap = emapper("HCALmapHBHElegacy_J.txt")
    emap.parseEmap()

    for channel in emap.listAll():
      foundChannel = False
      #info("channel: " + str(channel))
      #info("zsts: " + str(self.zsts))
      for zst in self.zsts:
        #info("zst: " + str(zst))
        if channel["crate"] == zst["crate"] and channel["uhtr"] == zst["uhtr"] and channel["uhtr_fi"] == zst["uhtr_fi"] and channel["fi_ch"] == zst["fi_ch"]:
          channel["zst"] = zst["zst"]
          foundChannel = True
      if not foundChannel:
        emap.emap.remove(channel)

    self.formatJson(self.outVar, emap.emap, self.outFileName)

  def getOutJSONinfo(self):
    return (self.outFileName, self.outVar)
