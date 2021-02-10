#?description=Display Run-Time Type Information as a graph showing inheritance relationships between classes
#?shortcut=

from com.pnfsoftware.jeb.client.api import IScript, GraphDialogExtensions
from com.pnfsoftware.jeb.client.api.GraphDialogExtensions import EdgeStyle, VertexShape
from com.pnfsoftware.jeb.core.units import IBinaryUnit
from com.pnfsoftware.jeb.core.util import Digraph
from com.pnfsoftware.jeb.core.input import IInput
from com.pnfsoftware.jeb.util.io import IO

'''
Display class inheritance graph built from Run-Time Type Information extracted by JEB.

This script parses JEB's RTTI text output, provided as 'run-time type information' unit. 

Each line follows the pattern:

class BaseClassName : public|private [virtual] ParentClassName1, ...;

'''
IGNORE_STD = True # True to ignore C++ std classes (when used as base class)
CLASS_SEPARATOR = ' : '
PARENT_SEPARATOR = ', '

class GraphRtti(IScript):
  def run(self, ctx):
  
    # retrieve RTTI unit
    prj = ctx.getMainProject()
    if not prj:
      print('Need a project')
      return

    units = prj.findUnits(IBinaryUnit)
    if not units or len(units) == 0:
      print('Need RTTI unit')
      return
    
    rttiUnit = None
    for unit in units:
      if unit.getName() == 'run-time type information':
        rttiUnit = unit
    if not rttiUnit:
      print('Need RTTI unit')

    data = IO.readInputStream(rttiUnit.getInput().getStream())   
    rttiText = ''.join(chr(c) for c in data)
    
    # parsing
    g = Digraph.create()
    curId = 0
    classToId = dict()
    virtualEdges = list() # [[childId, parentId]]
    lines = rttiText.splitlines()[2:] # skip header
    for line in lines:
      line = line.strip()[:-1] # beautify
      if not line.startswith('class'):
        continue
      classes = line.split(CLASS_SEPARATOR)
      if len(classes) > 2:
        print('error: malformed line (%s)' % line)
        continue
      
      # register base class id      
      baseClassName = classes[0][6:]
      if IGNORE_STD and baseClassName.startswith('std::'):
        continue
      if baseClassName not in classToId.keys():
        g.v(curId, None, baseClassName)
        classToId[baseClassName] = curId
        curId+=1
      print('baseClassName=%s' % baseClassName)
      
      # add edges for each parent, if any
      if len(classes) == 1:
        continue
      for parent in classes[1].split(PARENT_SEPARATOR):
        parentStr = parent.split()
        if len(parentStr) < 2:
          print('error: malformed line (%s)' % line)
          continue
        isPublic = parentStr[0] == 'public'
        isVirtual = parentStr[1] == 'virtual'
        parentStartIndex = 7 if isPublic else 8
        parentStartIndex += 8 if isVirtual else 0
        parentName = parent[parentStartIndex:]
        
        print('  parentName=%s, isPublic = %d, isVirtual = %d' % (parentName, isPublic, isVirtual))
        
        if parentName not in classToId.keys():
          g.v(curId, None, parentName)
          classToId[parentName] = curId
          curId+=1

        g.e(classToId[baseClassName], classToId[parentName])
        if isVirtual:
          virtualEdges.append([classToId[baseClassName], classToId[parentName]])

    class Ext(GraphDialogExtensions):
      def getEdgeStyle(self, vertexId0, vertexId1):
        if [vertexId0, vertexId1] in virtualEdges:
          # dashed edges to represent virtual inheritance
          return EdgeStyle.DASHED
        return EdgeStyle.SOLID
      def getVertexShape(self, vertexId):
        return VertexShape.SQUARE_FILLED
        
    g.done()
    ctx.displayGraph('RTTI Class Relationship Graph', g, Ext())