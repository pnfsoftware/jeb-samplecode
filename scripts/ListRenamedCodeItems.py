#?description=List renamed code items (classes, methods, fields)
#?shortcut=
from com.pnfsoftware.jeb.client.api import IScript
from com.pnfsoftware.jeb.core.units.code import ICodeUnit
"""
Sample script JEB Decompiler.
"""
class ListRenamedCodeItems(IScript):
  def run(self, ctx):
    prj = ctx.getMainProject()
    assert prj, 'Need a project'
    units = prj.findUnits(ICodeUnit)
    cnt = 0
    for unit in units:
      for o in unit.getClasses():
        if o.isRenamed():
          print('Class renamed: %s from %s' % (o.getName(), o.getName(False)))
          cnt += 1
      for o in unit.getMethods():
        if o.isRenamed():
          print('Method renamed: %s from %s' % (o.getName(), o.getName(False)))
          cnt += 1
      for o in unit.getFields():
        if o.isRenamed():
          print('Field renamed: %s from %s' % (o.getName(), o.getName(False)))
          cnt += 1
    print('Items renamed: %d' % cnt)
