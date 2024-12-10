#?description=Advanced use of displayGraph() to display the callgraph
#?shortcut=
from com.pnfsoftware.jeb.client.api import IScript, IGraphicalClientContext, GraphDialogExtensions
from com.pnfsoftware.jeb.core.units import UnitAddress
from com.pnfsoftware.jeb.core.units.code import ICodeUnit, CodeUtil
from com.pnfsoftware.jeb.core.units.code.android import IDexUnit, DalvikCallgraphBuilder
from com.pnfsoftware.jeb.util.graph import Digraph
"""
Sample script for JEB Decompiler.
"""
class GraphDemo2(IScript):

  def run(self, ctx):
    prj = ctx.getMainProject()
    assert prj, 'Need a project'

    code = prj.findUnit(ICodeUnit)
    assert code, 'Need a code unit'

    b = CodeUtil.createCallgraphBuilder(code)
    g = b.buildModel()

    class Ext(GraphDialogExtensions):
      #def getLayoutMode(self):
      #  return GraphDialogExtensions.LayoutMode.FDC_NO_WEIGHT
      #def getVertexShape(self, vertexId):
      #  return GraphDialogExtensions.VertexShape.SQUARE
      #def getVertexColor(self, vertexId):
      #  return 0x0080A0
      def processNewVertexName(self, vertexId, newName):
        addr = b.getAddressForVertexId(vertexId)
        return code.getMethod(addr).setName(newName)
      def getUnitAddress(self, vertexId):
        addr = b.getAddressForVertexId(vertexId)
        if not addr:
          return None
        return UnitAddress(code, addr)
      def getVertexMark(self, vertexId):
        addr = b.getAddressForVertexId(vertexId)
        return code.getInlineComment(addr) == 'MARKED'
      def processVertexMark(self, vertexId, mark):
        addr = b.getAddressForVertexId(vertexId)
        code.setInlineComment(addr, 'MARKED' if mark else '')
        return True

    ctx.displayGraph('Callgraph', g, Ext())
