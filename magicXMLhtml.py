# creates html with the necessary stuff for rendering vega plots
# John Hakala 8/18/17
def printHeader():
  print '''<!DOCTYPE html>
<head>
  <title>Vega-Lite Chart</title>
  <meta charset="utf-8">

  <script src="https://d3js.org/d3.v3.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/vega/2.6.5/vega.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/vega-lite/1.2.1/vega-lite.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/vega-embed/2.2.0/vega-embed.min.js" charset="utf-8"></script>

  <style media="screen">
    /* Add space between vega-embed links  */
    .vega-actions a {
      margin-right: 5px;
    }
  </style>
</head>
<body>
  <!-- Container for the visualization -->
  <div id="vis"></div>

  <script>
  var vlSpec ='''

def printFooter():
  print '''
  var embedSpec = {
    mode: "vega-lite",  // Instruct Vega-Embed to use the Vega-Lite compiler
    spec: vlSpec
  };

  // Embed the visualization in the container with id `vis`
  vg.embed("#vis", embedSpec, function(error, result) {
    // Callback receiving the View instance and parsed Vega spec
    // result.view is the View, which resides under the '#vis' element
  });
  </script>
</body>
</html>
'''

def printChart(chartName):
  with open(chartName, 'r') as c:
    print c.read()

def makePage(chartName):
  printHeader()
  printChart(chartName)
  printFooter()
