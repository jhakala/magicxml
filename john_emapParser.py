from pprint import pprint

# parses the emap textfiles using dicts
# John Hakala 8/18/17

class emapper:
  def __init__(self, inFileName):
    self.inFileName = inFileName
    self.emap = []

  def parseEmap(self):
    emapFile = open(self.inFileName, "r")
    headerLine = True
    for line in emapFile:
      if "##" in line:
        continue
      if headerLine:
        headers = line.split()
        headers[:] = [item for item in headers if item != "pp"]
        headerLine = False
      else: 
        if "#" in line:
          continue
        emapDict = {}
        items = line.split()
        for iItem in range(0, len(items)):
          emapDict[headers[iItem]]=items[iItem]
        self.emap.append(emapDict)

  def search(self, filterDict):
    matches = []
    for channel in self.emap:
      if all(key in channel and channel[key] == filterDict[key] for key in filterDict):
        matches.append(channel)
    return matches
     
  def listAll(self):
    return self.search({})


if __name__ == "__main__":
  print "this is a test"
  #emap = emapper("HCALmapHBHEP17_J.txt")
  emap = emapper("HCALmapHBHElegacy_J.txt")
  emap.parseEmap()
  searchDict = {}
  searchDict["RBX"] = "HBP01"
  pprint(emap.search(searchDict))
