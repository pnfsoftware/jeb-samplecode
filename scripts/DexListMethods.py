#?description=List methods of all dex units found in the current project
#?shortcut=
from com.pnfsoftware.jeb.client.api import IScript
from com.pnfsoftware.jeb.core.units.code.android import IDexUnit
"""
Sample script for JEB Decompiler.
"""
class DexListMethods(IScript):

  def run(self, ctx):
    prj = ctx.getMainProject()
    assert prj, 'Need a project'

    # replace IDexUnit by ICodeUnit to find all code units (that includes dex units as well)
    for codeUnit in prj.findUnits(IDexUnit):
      self.processDex(codeUnit)

  def processDex(self, unit):
    for m in unit.getMethods():
      print m.getSignature()
