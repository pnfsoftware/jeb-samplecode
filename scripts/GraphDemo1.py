#?description=Basic use of the displayGraph() API method, which does not make use of the graph extension
#?shortcut=
from com.pnfsoftware.jeb.client.api import IScript, IGraphicalClientContext
from com.pnfsoftware.jeb.core.util import Digraph
"""
Sample script for JEB Decompiler.
"""
class GraphDemo1(IScript):
  def run(self, ctx):
    g = Digraph.create().e(0, 1).e(0, 2).e(0, 3).e(1, 0).e(3, 4).e(3, 5).e(4, 6).e(5, 7).done()
    ctx.displayGraph('Sample Graph', g)