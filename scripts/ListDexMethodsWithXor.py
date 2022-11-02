#?description=List dex methods making use of xor instructions
#?shortcut=
from com.pnfsoftware.jeb.client.api import IScript
from com.pnfsoftware.jeb.core.units.code.android import IDexUnit
"""
Sample script for JEB Decompiler.
"""
class ListDexMethodsWithXor(IScript):

  def run(self, ctx):
    prj = ctx.getMainProject()
    assert prj, 'Need a project'

    dex = prj.findUnit(IDexUnit)
    assert dex, 'Need a dex unit'

    cnt = 0
    for m in dex.getMethods():
      if m.isInternal():
        ci = m.getData().getCodeItem()
        if ci and self.checkMethod(ci):
          print(m.getSignature(True, False))
          cnt += 1
    print('Found %d methods' % cnt)

  def checkMethod(self, ci):
    for insn in ci.getInstructions():
      if insn.toString().find('xor-') >= 0:
        return True
    return False
