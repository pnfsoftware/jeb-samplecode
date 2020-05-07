from com.pnfsoftware.jeb.client.api import IScript
from com.pnfsoftware.jeb.core import RuntimeProjectUtil
from com.pnfsoftware.jeb.core.units import UnitUtil
from com.pnfsoftware.jeb.core.units.code.android import IDexUnit, IDalvikDebuggerUnit

"""
This script looks for all DEX units in the project and registers them to the current Android debugging session.
"""
class AndroidDbgAddAllDex(IScript):

  def run(self, ctx):
    prj = ctx.getMainProject()
    dbg = prj.findUnit(IDalvikDebuggerUnit)
    if not dbg:
      print('Cannot find the Dalvik debugger')
      return

    dexlist = RuntimeProjectUtil.findUnitsByType(prj, IDexUnit, False)
    for dex in dexlist:
      if dbg.registerDebuggee(dex):
        print('Added to debuggees list: %s', UnitUtil.buildFullyQualifiedUnitPath(dex))