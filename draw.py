#!/usr/bin/python
from os import listdir
import cgi
import cgitb; cgitb.enable()  # for troubleshooting
from magicXMLhtml import *

# cgi interface for makePage.py
# parses the form from apache, and hands back the proper html
# John Hakala 8/18/17

print "Content-type: text/html\n\n";
form = cgi.FieldStorage()
inPlot =  form.getvalue('inPlot')
inPlotShortName = inPlot.replace("/jhakala/outputPlots/", "")
if inPlotShortName in listdir("../../html/jhakala/outputPlots"):
  makePage("../../html" + inPlot)
else:
  print "bad input file:", inPlotShortName
  print listdir("../../html/jhakala/outputPlots")
