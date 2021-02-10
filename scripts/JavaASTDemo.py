#?description=Show how to navigate and dump Java AST trees
#?shortcut=
import os
from com.pnfsoftware.jeb.client.api import IScript
from com.pnfsoftware.jeb.core.units.code.java import IJavaSourceUnit
"""
Sample script for JEB Decompiler.
"""
class JavaASTDemo(IScript):
  def run(self, ctx):
    prj = ctx.getMainProject()
    assert prj, 'Need a project'

    for unit in prj.findUnits(IJavaSourceUnit):
      c = unit.getClassElement()
      for m in c.getMethods():
        self.displayTree(m)

  def displayTree(self, e, level=0):
    print('%s%s @ 0x%X' % (level*'  ', e.getElementType(), e.getPhysicalOffset()))
    if e:
      elts = e.getSubElements()
      for e in elts:
        self.displayTree(e, level+1)
