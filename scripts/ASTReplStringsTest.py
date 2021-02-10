#?description=Java AST manipulation demo: Find the first Java unit, replace String immediates by random string
#?shortcut=
import time
from com.pnfsoftware.jeb.client.api import IScript
from com.pnfsoftware.jeb.core.units.code.java import IJavaSourceUnit, IJavaConstant
"""
Sample script for JEB Decompiler.
"""
class ASTReplStringsTest(IScript):

  def run(self, ctx):
    prj = ctx.getMainProject()
    assert prj, 'Need a project'

    src = prj.findUnit(IJavaSourceUnit)
    assert src, 'Need a java source unit (decompiled)'
    print('Processing %s' % src)

    self.replcnt = 0
    self.cstbuilder = src.getFactories().getConstantFactory()
    for m in src.getClassElement().getMethods():
      self.checkElement(None, m)

    print('Replaced %d strings' % self.replcnt)
    src.notifyGenericChange()

  def checkElement(self, parent, e):
    if isinstance(e, IJavaConstant) and e.isString():
      parent.replaceSubElement(e, self.cstbuilder.createString('blah_' + str(time.time())))
      self.replcnt += 1
    for subelt in e.getSubElements():
      self.checkElement(e, subelt)
