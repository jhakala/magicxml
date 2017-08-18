#!/usr/bin/python
from os import listdir
import cgi
import cgitb; cgitb.enable()  # for troubleshooting
from makeAltair import altairify

# cgi interface for makeAltair.py
# A user of this page will ask makeAltair to process the xmls
# and generate the visualizations from scratch
# John Hakala 8/16/17

# TODO: one might consider bookkeeping whether the plot has been processed already
# and display a cached plot, instead of doing the processing each time a user makes a click

form = cgi.FieldStorage()
inXML =  form['singleInput'].value  if 'singleInput' in form.keys()  else None
new   =  form['newDiffInput'].value if 'newDiffInput' in form.keys() else None
old   =  form['oldDiffInput'].value if 'oldDiffInput' in form.keys() else None
dirs = ["/nfshome0/hcalsw/config_files/ZSConfigFiles/", "/nfshome0/elaird/xml/ngHE/", "/nfshome0/hcalsw/config_files/LEDSettings/"]
print "Content-type: text/html\n\n";
print "<html><body>"


def find(xml):
  # look to see if the xml is really there
  found = False
  for xmlDir in dirs:
    if xml in listdir(xmlDir):
      found=True
      location = xmlDir
  if found:
    return found, location

if inXML and not (new or old):
  # run in 'single mode': just visualize the parameters in a given magicXML
  found, location = find(inXML)
  if found:
    altairify("single", {"inXML":location+"/"+inXML, "new":None, "old":None})
  else:
    print "input xml not found"
    exit(1)

elif not inXML and (new and old):
  # run in 'diff mode': make a plot of the differences between two magicXMLs
  if new == old:
    print "cannot diff a file against itself"
    exit(1)
  foundNew, locationNew = find(new)
  foundOld, locationOld = find(old)
  found = foundNew and foundOld
  if found:
    altairify("diff", {"inXML":None, "new":locationNew+"/"+new, "old":locationOld+"/"+old})
  else:
    print "input xmls not found"
    exit(1)

else:
  print "invalid inputs"
  exit(1)
print "</body></html>"
