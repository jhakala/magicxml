from os import path, makedirs
from glob import glob
from pandas import read_json
from altair import Row, Column, Chart, Text, load_dataset
import json 
from magicXMLsax import makeJSON
from magicXMLutils import *
from magicXMLhtml import *

# John Hakala 8/16/17

# taken from https://altair-viz.github.io/recipes.html#plot-recipes/population
def heatmap(data, row, column, color, cellsize=(30, 15)):
   """Create an Altair Heat-Map

   Parameters
   ----------
   row, column, color : str
      Altair trait shorthands
   cellsize : tuple
      specify (width, height) of cells in pixels
   """
   return Chart(data).mark_text(
          applyColorToBackground=True,
        ).encode(
          row=row,
          column=column,
          text=Text(value=' '),
          color=color
        ).configure_scale(
          textBandWidth=cellsize[0],
          bandSize=cellsize[1]
        )

def altairify(mode, args):
    # creates an altair heatmap from magic xmls

    # validate arguments
    if mode == "single":
      if not args["inXML"] or args["new"] or args["old"]:
        error("Please pick one and only one input file  with the --inXML option")
      else:
        inFileNames = [args["inXML"]]
    if mode == "diff":
        if  not (args["new"] and args["old"]) or args["inXML"]:
          error("Please pick one and only one new file and one and only one old file  with the --new and --old options")
        else:
          inFileNames = [args["old"], args["new"]]

    # initialize bookkeeping
    outJSONmap = {}
    outPlotsDir = "../../html/jhakala/outputPlots"
    if not path.exists(outPlotsDir):
      makedirs(outPlotsDir)
    outJSONvar = ""
    lastOutJSONvar = ""
    first = True
    combinedOutJSONnames = []
    
    # process all the xml into JSONs, validate they are consistent, put them into a map
    info("inFileNames:" + str(inFileNames))
    for inFileName in inFileNames:
      (singleOutJSONnames, outJSONvar) = makeJSON(inFileName)
      #info("singleOutJSONnames" + str(singleOutJSONnames) + "outJSONvar" + str(outJSONvar))
      if not first and outJSONvar != lastOutJSONvar:
        error("The input files seem to define inconsistent variables: {} and {}".format(lastOutJSONvar, outJSONvar))
      outJSONmap[inFileName] = singleOutJSONnames
      first = False
      lastOutJSONvar = outJSONvar
    # at this point the outJSONmap can look like:
    #     {"inXml1":["outJson1"]}
    # or  {"indir1":["outJson1.1", "outJson1.2", "outJson1.3"]}
    # or  {"inXml1":["outJson1"], "inXml2":["outJson2"]}
    # or  {"indir1":["outJson1.1", "outJson1.2", "outJson1.3"], "inXml2":["outJson2"]} 
    # or  {"indir1":["outJson1.1", "outJson1.2", "outJson1.3"], "indir2":["outJson2.0", "outJson2.1"]} 
    # etc.


    # now we want to squish it down to one outJson per input
    info("intermediate JSONs: " + str(outJSONmap))
    fullOutJSONnames = []
    for outJSONkey in outJSONmap.keys():
      if len(outJSONmap[outJSONkey]) == 1:
        fullOutJSONnames.extend(outJSONmap[outJSONkey])
      elif len(outJSONmap[outJSONkey]) > 1:
        combinedList = []
        for outJSON in outJSONmap[outJSONkey]: 
          with open(path.join("../../html/jhakala/outputJSONs", outJSON)) as partialListFile:
            partialList = json.load(partialListFile)
            combinedList.extend(partialList)
        with open(path.join("../../html/jhakala/outputJSONs", "fullJSON_{}.json".format(outJSONkey.replace("/", "_"))), "w") as outFullJSON:
          json.dump(combinedList, outFullJSON)
          fullOutJSONnames.append(path.basename(outFullJSON.name))
          outPlotNames = ["plot_{}".format(outFullJSON.name.replace(".json", ""))]
      else:
        error("magicXMLsax parser returned {} indicating there was no output file".format(outJSONmap[outJSONkey]))
       

    if mode == "single":
      info("making visualization of " + inFileName)
      plotName = fullOutJSONnames[0]
  
    elif mode == "diff":
      if (path.basename(args['old']).replace(".xml", "") in fullOutJSONnames[1]):
        fullOutJSONnames.reverse()
      #else:
      #  print "args['old']:", path.basename(args['old'])
      #  print "args['new']:", path.basename(args['new'])
      #  print fullOutJSONnames
      #  exit(1)
      with open(path.join("../../html/jhakala/outputJSONs", fullOutJSONnames[0])) as inFileOld:
        old = json.load(inFileOld)
      with open(path.join("../../html/jhakala/outputJSONs", fullOutJSONnames[1])) as inFileNew:
        new = json.load(inFileNew)

      # match channels and subtract the relevant variable
      for channelNew in new: 
        for channelOld in old:
          if channelNew["eta"] == channelOld["eta"] and channelNew["phi"] == channelOld ["phi"] and channelNew["depth"] == channelOld["depth"] and channelNew["side"] == channelOld["side"]:
            channelNew[outJSONvar] = str(int(channelNew[outJSONvar]) - int(channelOld[outJSONvar]))
      outDiffName = 'diff_{}_{}'.format(fullOutJSONnames[0].replace(".json",""), fullOutJSONnames[1])
      with open(path.join("../../html/jhakala/outputJSONs", outDiffName), "w") as outFile:
        json.dump(new, outFile)
      plotName = outDiffName

    else:
      error("invalid mode '{0}': must be either 'diff' or 'single'".format(mode))
      exit(1)
      
    # the jsons now have all positive etas but separate plus vs. minus with a "side" that's 1 or -1
    with open(path.join("../../html/jhakala/outputJSONs", plotName)) as inFile:
      jsonDict = json.load(inFile)
      for channel in jsonDict:
        channel["eta"] = str(int(channel["side"])*int(channel["eta"]))
  
    # make one plot in ieta/iphi per depth
    print """<body>
    <form action='/cgi-bin/jhakala/draw.py' type='submit' method='get'>"""
    for depth in range(1,10):
      depthDict = [channel for channel in jsonDict if int(channel["depth"]) == depth]
      # TODO probably can have pandas directly read the dict instead of going back to JSON first
      depthData = read_json(json.dumps(depthDict))
      #plot = heatmap(depthData, row="phi", column="eta", color="amplitude")
      plot = heatmap(depthData, row="phi", column="eta", color=outJSONvar)
      outChartName = path.join(outPlotsDir, "{}_depth{}.json".format(plotName.replace(".json", ""), depth))
      plot.savechart(outChartName, "json")
      print "      <input type='radio' name='inPlot' value='{}'> depth {}<br>".format(outChartName.replace("../../html", ""), depth)
    print """      <br><br><input type='submit' value='plot'>
    </form>
  """


if __name__ == "__main__":
  # for testing
  from argparse import ArgumentParser
  argParser = ArgumentParser(description = "parses magic xmls and creates JSON representations")
  argParser.add_argument("--mode"  , dest="mode"   ,  
                         help = "either 'single' or 'diff"                   )
  argParser.add_argument("--inXML" , dest="inXML"  ,  
                         help = "for single mode: input filename"            )
  argParser.add_argument("--new"   , dest="new" ,  
                         help = "for diff mode: new input xml filename"      )
  argParser.add_argument("--old"   , dest="old" ,  
                         help = "for diff mode: old input xml filename"      )
  args = argParser.parse_args()

  altairArgs = {"inXML": args.inXML, "old": args.old, "new": args.new}
  altairify(args.mode, altairArgs)

