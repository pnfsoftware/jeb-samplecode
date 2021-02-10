#?description=Use the specialized IDexUnit interface to replace all dex strings 'text/html' by 'foobar'.
#?shortcut=
from com.pnfsoftware.jeb.client.api import IScript
from com.pnfsoftware.jeb.core.units.code import ICodeUnit, ICodeItem
from com.pnfsoftware.jeb.core.units.code.android import IDexUnit
from com.pnfsoftware.jeb.core.units.code.android.dex import IDexString
"""
Sample script for JEB Decompiler.
"""
class DexManipulation(IScript):
  def run(self, ctx):
    prj = ctx.getMainProject()
    assert prj, 'Need a project'
    for codeUnit in prj.findUnits(IDexUnit):
      self.processDex(codeUnit)

  def processDex(self, dex):
    # replace DEX strings
    cnt = 0
    for s in dex.getStrings():
      if s.getValue().startswith('text/html'):
        s.setValue('foobar')
        cnt += 1
        print('String replaced')
    if cnt > 0:
      dex.notifyGenericChange()
