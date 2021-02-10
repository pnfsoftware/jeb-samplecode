#?description=Look for all DEX units in the project and registers them to the current Android debugging session
#?shortcut=
from com.pnfsoftware.jeb.client.api import IScript
from com.pnfsoftware.jeb.core import RuntimeProjectUtil
from com.pnfsoftware.jeb.core.units import UnitUtil
from com.pnfsoftware.jeb.core.units.code.android import IDexUnit, IDalvikDebuggerUnit
"""
Sample script for JEB Decompiler.
"""
class AndroidDbgAddAllDex(IScript):
  def run(self, ctx):
    prj = ctx.getMainProject()
    assert prj, 'Need a project'

    dbg = prj.findUnit(IDalvikDebuggerUnit)
    assert dbg, 'Need a dalvik debugger'

    dexlist = RuntimeProjectUtil.findUnitsByType(prj, IDexUnit, False)
    for dex in dexlist:
      if dbg.registerDebuggee(dex):
        print('Added to debuggees list: %s', UnitUtil.buildFullyQualifiedUnitPath(dex))
