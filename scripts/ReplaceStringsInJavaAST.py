#?description=Find the first decompiled Java unit and replace String immediates by random string
#?shortcut=
import time
from com.pnfsoftware.jeb.client.api import IScript
from com.pnfsoftware.jeb.core.units.code.java import IJavaSourceUnit, IJavaClass, IJavaConstant
"""
Sample script for JEB Decompiler.
"""
class ReplaceStringsInJavaAST(IScript):

  def run(self, ctx):
    prj = ctx.getMainProject()
    assert prj, 'Need a project'

    src = prj.findUnit(IJavaSourceUnit)
    assert src, 'Need a java source unit (decompiled)'

    print('Processing %s' % src)

    elt = src.getASTElement()
    if not isinstance(elt, IJavaClass): return

    self.replcnt = 0
    self.cstbuilder = src.getDecompiler().getHighLevelContext().getConstantFactory()
    for m in elt.getMethods():
      self.checkElement(None, m)

    print('Replaced %d strings' % self.replcnt)
    src.notifyGenericChange()

  def checkElement(self, parent, e):
    if isinstance(e, IJavaConstant) and e.isString():
      parent.replaceSubElement(e, self.cstbuilder.createString('blah_' + str(time.time())))
      self.replcnt += 1
    for subelt in e.getSubElements():
      self.checkElement(e, subelt)
