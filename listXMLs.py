#!/usr/bin/python
import cgi
import cgitb; cgitb.enable()  # for troubleshooting
from os import listdir
from xmlListHtml import *

# Generates the listing for a given kind of magic xml
# It looks at the directory where that kind of magicxml lives
# John Hakala, 8/17/17

def getDetails(xmlType):
  # define the different directories of magic xmls, their types, and a title for them
  nameFilter = ""
  if xmlType == "ngDelays":
    title = "ngHEP17 RBX delays"
    directory = "/nfshome0/elaird/xml/ngHE/"
    nameFilter = "Delay"
  elif xmlType == "ZSTs":
    title = "HBHE zero suppression thresholds"
    directory = "/nfshome0/hcalsw/config_files/ZSConfigFiles/"
  elif xmlType == "LEDamps":
    title = "HBHE LED settings"
    directory = "/nfshome0/hcalsw/config_files/LEDSettings/"
  else:
    print "invalid xmlType", xmlType
    exit(1)
  return title, directory, nameFilter

def makeRadio(inputName, which):
  # creates the radio buttons for each magic xml with the proper form names for diff or single mode
  if which in ["singleInput", "newDiffInput", "oldDiffInput"]:
    return "\n        <input type='radio' name='{1}' value='{0}'> {0}  <br>".format(inputName, which)
  else:
    exit(1)

def makeRadios(title, directory, which, nameFilter):
   # puts together all the radiobuttons
   singleButtons = ""
   title = "<h3> {} </h3>".format(title)
   options = listdir(directory)
   for option in options:
     if nameFilter in option:
       singleButtons += makeRadio(option, which)
   return singleButtons

def makeSingleButtons(xmlType):
  # formats the radio buttons for the single mode menu
  which = "singleInput"
  title, directory, nameFilter = getDetails(xmlType)
  singleButtons = makeRadios("visualize " + title, directory, which, nameFilter)

  return '''    {}
    <form action="runMakeAltair.py" type="submit" method="get">
      <tt>
        <br>{}<br><br>
      </tt>
      <input type='submit'>
    </form>'''.format(title, singleButtons)

def makeDiffButtons(xmlType):
  # formats the radio buttons for the diff mode menu
  title, directory, nameFilter = getDetails(xmlType)
  newDiffButtons = makeRadios(title, directory, "newDiffInput", nameFilter)
  oldDiffButtons = makeRadios(title, directory, "oldDiffInput", nameFilter)

  return '''    {}
    <form action="runMakeAltair.py" type="submit" method="get">
        <table><tbody><tr>
          <td> new: <br><tt>{}</tt></td><td> old: <br><tt>{}</tt></td>
        </tr></tbody></table>
      <input type='submit'>
    </form>'''.format("diff " + title, newDiffButtons, oldDiffButtons)

def getBody(xmlType, mode):
  # puts together the main chunk of the html
  body = getHeader()
  body +=  "    <!-- begin body -->\n"
  if not xmlType in ["ngDelays", "ZSTs", "LEDamps"]:
    body += "the xmlType was not found: <tt>%s</tt>"%xmlType
    exit(1)
  else:
    if mode == "single":
      body += makeSingleButtons(xmlType)
    elif mode == "diff":
      body += makeDiffButtons(xmlType)
    else:
      print "invalid mode"
      exit(1)
    body += "\n    <!-- body end -->"
  return body

form = cgi.FieldStorage()
xmlType =  form.getvalue('xmlType')
mode =  form.getvalue('mode')
html = getBody(xmlType, mode)
html += getFooter()

print "Content-type: text/html"
print
print html
