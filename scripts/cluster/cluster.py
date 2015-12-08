#!/usr/bin/python3

'''
Simple graph community detection using edge-betweenness method.
Dependency: igraph

Input file format:

    # vertices (160)
    v,449
    v,475
    ...
    # edges (322)
    e,376,391,2
    e,519,478,3
    ...

Output file format:

    # clusters
    449,711,684,344,497,...
    475,340,633,324,527,...

Author: Nicolas Falliere
'''

import sys
from igraph import *


class TypeGraph:

  def __init__(self, filename):
    self.nodes = []
    self.edges = []
    self.idToIndex = {}

    with open(filename) as f:
      lines = f.readlines()
      for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
          continue
        elts = line.split(',')
        if elts[0] == 'v':
          nodeId = int(elts[1])
          nodeLabel = elts[2] if len(elts) > 2 else None
          self.idToIndex[nodeId] = len(self.nodes)
          self.nodes.append((nodeId, nodeLabel))
        if elts[0] == 'e':
          src = int(elts[1])
          dst = int(elts[2])
          weight = int(elts[3]) if len(elts) > 3 else 1
          if weight == 0:
            raise Exception('Weight cannot be 0')
          self.edges.append((src, dst, weight))

    self.g = self.__createGraph()

  def __createGraph(self):
    g = Graph()
    g.add_vertices(len(self.nodes))
    _edges = []
    _weights = []
    for src, dst, weight in self.edges:
      _edge = (self.idToIndex[src], self.idToIndex[dst])
      if _edge in _edges or src == dst:
        raise Exception('Error in input graph: edge %d->%d' % (src, dst))
      _edges.append(_edge)
      _weights.append(weight)
    g.add_edges(_edges)
    g.es['weight'] = _weights
    return g

  def getGraph(self):
    return self.g

  def getNodeId(self, index):
    return self.nodes[index][0]

  def getNodeLabel(self, index):
    return self.nodes[index][1]


if __name__ == '__main__':
  if len(sys.argv) != 3:
    sys.exit(-1)

  typeGraph = TypeGraph(sys.argv[1])
  g = typeGraph.getGraph()
  print(g)

  dendro = g.community_edge_betweenness(directed=True, weights='weight')
  print(dendro)

  clusters = dendro.as_clustering()
  print(clusters)

  output = '# clusters\n'
  for cluster in clusters:
    _cluster = []
    for i in cluster:
      _cluster.append(str(typeGraph.getNodeId(i)))
    output += '%s\n' % ','.join(_cluster)

  with open(sys.argv[2], 'w') as f:
    f.write(output)
