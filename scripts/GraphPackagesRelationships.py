#?description=Build callgraph between user routines and routines belonging to specific packages
#?shortcut=
from com.pnfsoftware.jeb.client.api import IScript, IGraphicalClientContext, GraphDialogExtensions
from com.pnfsoftware.jeb.core.units import UnitAddress, INativeCodeUnit
from com.pnfsoftware.jeb.core.units.code import ICodeUnit, CodeUtil
from com.pnfsoftware.jeb.core.units.code.android import IDexUnit, DalvikCallgraphBuilder
from com.pnfsoftware.jeb.core.util import Digraph
"""
Build callgraph between unknown routines (whose name start with 'sub_') 
and routines from specific packages (whose names are prefixed by known package names).

This serves to see relationships between user code and library code. 

Modify PACKAGES_OF_INTEREST below to suit your needs.
"""
PACKAGES_OF_INTEREST = ['OpenSSL', 'cURL']

class GraphPackagesRelationships(IScript):

  def getRootModule(self, label):
    if '::' in label:
      return label.split('::')[0]
    return None

  def run(self, ctx):
    prj = ctx.getMainProject()
    assert prj, 'Need a project'

    code = prj.findUnit(INativeCodeUnit)
    assert code, 'Need a code unit'

    g = Digraph.create()
    model = code.getCodeModel()
    cg = model.getCallGraphManager().getGlobalCallGraph()
    routines = code.getInternalMethods()

    for srcRtn in routines:
      srcName = srcRtn.getName(True)
      srcModule = self.getRootModule(srcName)
      srcIndex = routines.indexOf(srcRtn)
      callees = cg.getCallees(srcRtn, False)
      for target in callees:
        if not target.isInternal():
          continue
        targetRtn = code.getInternalMethod(target.getInternalAddress().getAddress(), True)
        if not targetRtn:
          continue

        targetName = targetRtn.getName(True)
        dstModule = self.getRootModule(targetName)
        if (srcModule != dstModule) \
          and (srcName.startswith('sub_') or targetName.startswith('sub_')) \
          and (srcModule in PACKAGES_OF_INTEREST or dstModule in PACKAGES_OF_INTEREST):
          targetIndex = routines.indexOf(targetRtn)

          if not g.getVertex(srcIndex):
            g.v(srcIndex, None, srcName)
          if not g.getVertex(targetIndex):
            g.v(targetIndex, None, targetName)
          if not g.getEdge(srcIndex, targetIndex):
            g.e(srcIndex, targetIndex)
            
    g.done()

    class Ext(GraphDialogExtensions):
      def getUnitAddress(self, vertexId):
        # implement navigation
        rtn = routines[vertexId]
        if not rtn:
          return None
        addr = rtn.getAddress()
        if not addr:
          return None
        return UnitAddress(code, addr)

    ctx.displayGraph('Packages Callgraph', g, Ext())