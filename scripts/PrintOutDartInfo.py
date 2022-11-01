#?description=Basic demo for the API to access processed Dart AOT snapshots unit
#?shortcut=
from com.pnfsoftware.jeb.client.api import IScript, IGraphicalClientContext
from com.pnfsoftware.jeb.core.units.code import ICodeUnit
from com.pnfsoftware.jeb.core.units.code.dart import IDartAotUnit
"""
Sample script for JEB Decompiler.

Find a Dart AOT Snapshots unit (generated by the Dart AOT Snapshots processor plugin),
and use the API to print out basic snapshot information and generate the primary pool.
"""
class PrintOutDartInfo(IScript):
  def run(self, ctx):
    prj = ctx.getMainProject()
    u = prj.findUnit(IDartAotUnit)
    if not u: return
    print('Found a Dart AOT unit: %s' % u)

    # snapshot is of type IDartAotSnapshotInfo
    snap = u.getIsolateSnapshotInfo()
    print('Used Dart SDK version %s' % snap.getVersionTag())
    print('Isolate: %s' % snap)

    # pool= list of nulls, longs, and IDartInternalObject
    pool = u.generatePrimaryPool()
    print('%d entries in the main pool' % len(pool))
