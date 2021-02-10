#?description=Create a debugger unit for an APK object
#?shortcut=
from com.pnfsoftware.jeb.client.api import IScript
from com.pnfsoftware.jeb.core.units.code.android import IApkUnit, IDexUnit
from com.pnfsoftware.jeb.core.units.code.debug.impl import DebuggerSetupInformation
from com.pnfsoftware.jeb.core.util import DebuggerHelper
"""
Script for JEB Decompiler.
"""
class AndroidDbgCreate(IScript):
  def run(self, ctx):
    prj = ctx.getMainProject()
    assert prj, 'Need a project'

    # let's retrieve the primary apk unit loaded in the project, if there is one
    apk = prj.findUnit(IApkUnit)
    assert apk, 'Need an APK unit'

    # a debugger unit is the child of another unit
    dbg = DebuggerHelper.getDebugger(apk, True)
    if not dbg:
      print 'Cannot create or retrieve debugger'
      return

    # after creation, the debugger unit is not attached to any target
    print(dbg)

    if not dbg.isAttached():
      # we will find a matching compatible target on the devices that can be enumerated by the debugger unit
      setup = findTarget(dbg, apk)
      if not setup:
        print 'Target not found'
        return
      # UNCOMMENT below to request all threads to be stopped before attaching
      #setup.setSuspendThreads(True)
      # UNCOMMENT below to allow the creation of a child debugger for APK's native code
      #setup.setUseChildrenDebuggers(True)
      dbg.attach(setup)

    print 'Debugger found and attached: %s' % dbg


def findTarget(dbg, apk):
  # here, we use the un-attached debugger unit to enumerate compatible targets,
  # enumerate processes on those targets, and find one that matches our apk
  # this process may seem convoluted, but keep in mind that IDebuggerUnit are
  # not specific to android, they are a generic interface for any type of debugger
  te = dbg.getTargetEnumerator()
  for m in te.listMachines():
    for p in m.getProcesses():
      # match by exact package name
      if p.getName() == apk.getPackageName():
        return DebuggerSetupInformation.create(m, p)
  return None
