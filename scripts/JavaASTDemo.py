#?description=Show how to navigate and dump Java AST trees
#?shortcut=
from com.pnfsoftware.jeb.client.api import IScript
from com.pnfsoftware.jeb.core.units.code.java import IJavaSourceUnit, IJavaClass
"""
Sample script for JEB Decompiler.
"""
class JavaASTDemo(IScript):
  def run(self, ctx):
    prj = ctx.getMainProject()
    assert prj, 'Need a project'

    for unit in prj.findUnits(IJavaSourceUnit):
      elt = unit.getASTElement()
      if isinstance(elt, IJavaClass):
        for m in elt.getMethods():
          self.displayTree(m)

  def displayTree(self, e, level=0):
    print('%s%s @ 0x%X' % (level*'  ', e.getElementType(), e.getPhysicalOffset()))
    if e:
      elts = e.getSubElements()
      for e in elts:
        self.displayTree(e, level+1)
