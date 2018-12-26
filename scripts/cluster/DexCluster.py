"""
Sample client script for PNF Software' JEB.

Cluster DEX classes in order to rebuild an obfuscated+flattened code hierarchy.

Requires Jython 2.7

Refer to SCRIPTS.TXT for more information.
"""

import os

from java.lang import Runnable, Thread

from com.pnfsoftware.jeb.client.api import IScript, IGraphicalClientContext, IconType, ButtonGroupType
from com.pnfsoftware.jeb.core import RuntimeProjectUtil
from com.pnfsoftware.jeb.core.units.code import ICodeUnit, ICodeItem
from com.pnfsoftware.jeb.core.output.text import ITextDocument
from com.pnfsoftware.jeb.core.actions import Actions, ActionContext, ActionCreatePackageData, ActionMoveToPackageData


class DexCluster(IScript):

  OUTDIR = 'C:/Users/Nicolas/jeb2/jeb2-rcpclient/scripts'
  TARGETP = 'o.'  # customize

  def run(self, ctx):
    self.ctx = ctx
    # customize this
    self.outputDir = DexCluster.OUTDIR

    engctx = ctx.getEnginesContext()
    if not engctx:
      print('Back-end engines not initialized')
      return

    projects = engctx.getProjects()
    if not projects:
      print('There is no opened project')
      return

    codeUnit = RuntimeProjectUtil.findUnitsByType(projects[0], ICodeUnit, False)[0]

    print('Clustering: %s' % codeUnit)
    self.clusterUnit(codeUnit, DexCluster.TARGETP)

    print('Done.')


  def clusterUnit(self, codeUnit, basePackage=''):
    #print(codeUnit)
    typeToInternalMethods = {}
    typeToExternalMethods = {}
    # method -> list of called methods
    methodToMethods = {}
    # reverse map: method -> list of methods callers
    xmethodToMethods = {}
    methodToType = {}

    for classObject in codeUnit.getClasses():
      if (classObject.getGenericFlags() & ICodeItem.FLAG_INNER) != 0:
        #print('Inner class, skipping: %s' % classObject)
        continue

      pname = classObject.getPackage().getSignature(True)
      pname = pname[1:-1].replace('/', '.') + '.'
      if not pname.startswith(basePackage):
        #print('Class not in target package, skipping: %s' % classObject)
        continue

      typeIndex = classObject.getClassType().getIndex()
      typeToInternalMethods[typeIndex] = []
      methodObjects = classObject.getMethods()
      if not methodObjects:
        continue

      print('Processing: %s (type: %d)' % (classObject, typeIndex))
      for methodObject in methodObjects:
        methodIndex = methodObject.getIndex()
        typeToInternalMethods[typeIndex].append(methodIndex)

        methodToType[methodIndex] = typeIndex

        #print(methodObject)
        instructions = methodObject.getInstructions()
        if not instructions:
          continue

        print('  %s' % methodObject)
        for insn in instructions:
          s = insn.format(None)
          refMethodIndex = self.extractMethodIndex(s)
          if refMethodIndex >= 0:
            print('    %d -> %d' % (methodIndex, refMethodIndex))
            if methodIndex not in methodToMethods:
              methodToMethods[methodIndex] = []
            methodToMethods[methodIndex].append(refMethodIndex)
            #if refMethodIndex not in xmethodToMethods:
            #  xmethodToMethods[refMethodIndex] = []
            #xmethodToMethods[refMethodIndex].append(methodIndex)

    # derive type-to-type connections
    # map: edge(couple=src,dst) TO weight(int)
    edgemap = {}
    vertices = set()
    for methodIndex in methodToMethods:
      typeIndex = methodToType[methodIndex]
      for targetMethodIndex in methodToMethods[methodIndex]:
        targetTypeIndex = methodToType.get(targetMethodIndex, -1)
        if targetTypeIndex >= 0 and targetTypeIndex != typeIndex:
          #print ('%d -> %d' % (typeIndex, targetTypeIndex))
          edge = (typeIndex, targetTypeIndex)
          vertices.add(typeIndex)
          vertices.add(targetTypeIndex)
          if edge not in edgemap:
            edgemap[edge] = 0
          edgemap[edge] += 1

    types = codeUnit.getTypes()

    # graph definition (graphviz)
    gd = 'digraph {\n'
    for typeIndex in vertices:
      gd += '  %d [label="%s"]\n' % (typeIndex, self.getTypeLabel(types[typeIndex]))
    gd += '\n'
    for edge, weight in edgemap.items():
      gd += '  %d -> %d [weight=%d]\n' % (edge[0], edge[1], weight)
    gd += '}'
    with open(os.path.join(self.outputDir, 'graph.dot'), 'w') as f:
      f.write(gd)

    # graph definition (custom, for igraph)
    gd = '# vertices (%d)\n' % len(vertices)
    for typeIndex in vertices:
      gd += 'v,%d\n' % typeIndex
    gd += '# edges (%d)\n' % len(edgemap)
    for edge, weight in edgemap.items():
      gd += 'e,%d,%d,%d\n' % (edge[0], edge[1], weight)
    fileGraph = os.path.join(self.outputDir, 'graph.txt')
    with open(fileGraph, 'w') as f:
      f.write(gd)

    # clustering (external)
    fileClusteringScript = os.path.join(self.outputDir, 'cluster.py')
    fileClusters = os.path.join(self.outputDir, 'graph-clusters.txt')
    task = ClusterTask(fileClusteringScript, fileGraph, fileClusters)
    if isinstance(self.ctx, IGraphicalClientContext):
      self.ctx.executeAsync('Clustering...', task)
    else:
      task.run()

    # reading clusters
    clusters = self.readClusters(fileClusters)
    print('Clusters(types): %s' % clusters)

    # refactoring
    for i, cluster in enumerate(clusters):
      pname = basePackage + 'cluster%03d' % i

      # create a package clusterX
      data = ActionCreatePackageData()
      data.setFqname(pname)
      codeUnit.executeAction(ActionContext(codeUnit, Actions.CREATE_PACKAGE, 0, None), data)

      # move related classes to the virtual package
      for typeIndex in cluster:
        t = types[typeIndex]
        c = t.getImplementingClass()
        itemId = c.getItemId()

        data = ActionMoveToPackageData()
        data.setDstPackageFqname(pname)
        codeUnit.executeAction(ActionContext(codeUnit, Actions.MOVE_TO_PACKAGE, itemId, None), data)


  def readClusters(self, filepath):
    clusters = []
    with open(filepath) as f:
      lines = f.readlines()
      for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
          continue
        cluster = [int(elt) for elt in line.split(',')]
        clusters.append(cluster)
    return clusters


  def getTypeLabel(self, t):
    #t.getSignature(True)
    return 'type_%d' % t.getIndex()


  def extractMethodIndex(self, s):
    if s.startswith('invoke'):
      #print(s)
      i = s.find('method@')
      if i >= 0:
        i += 7
        j = s.find(',', i)
        if j < 0:
          j = len(s)
        return int(s[i:j])
    return -1


class ClusterTask(Runnable):

  def __init__(self, fileClusteringScript, fileGraph, fileClusters):
    self.fileClusteringScript = fileClusteringScript
    self.fileGraph = fileGraph
    self.fileClusters = fileClusters

  def run(self):
    os.system('%s %s %s' % (self.fileClusteringScript, self.fileGraph, self.fileClusters))
