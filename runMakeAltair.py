#!/usr/bin/python
from os import listdir
import cgi
import cgitb; cgitb.enable()  # for troubleshooting
from makeAltair import altairify

form = cgi.FieldStorage()
inXML =  form['singleInput'].value  if 'singleInput' in form.keys()  else None
new   =  form['newDiffInput'].value if 'newDiffInput' in form.keys() else None
old   =  form['oldDiffInput'].value if 'oldDiffInput' in form.keys() else None
dirs = ["/nfshome0/hcalsw/config_files/ZSConfigFiles/", "/nfshome0/elaird/xml/ngHE/", "/nfshome0/hcalsw/config_files/LEDSettings/"]
print "Content-type: text/html\n\n";
print "<html><body>"


def find(xml):
  found = False
  for xmlDir in dirs:
    if xml in listdir(xmlDir):
      found=True
      location = xmlDir
  if found:
    return found, location

if inXML and not (new or old):
  found, location = find(inXML)
  if found:
    altairify("single", {"inXML":location+"/"+inXML, "new":None, "old":None})
  else:
    print "input xml not found"
    exit(1)

elif not inXML and (new and old):
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
