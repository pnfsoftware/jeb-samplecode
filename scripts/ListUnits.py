#?description=List all units (as well as their byte sizes) of the currently opened project
#?shortcut=
from com.pnfsoftware.jeb.client.api import IScript
from com.pnfsoftware.jeb.core.units import IBinaryUnit
"""
Sample script for JEB Decompiler.
"""
class ListUnits(IScript):

  def run(self, ctx):
    prj = ctx.getMainProject()
    assert prj, 'Need a project'

    print('=> Listing units int project "%s":' % prj.getName())
    for art in prj.getLiveArtifacts():
      for unit in art.getUnits():
        self.checkUnit(unit)

  def checkUnit(self, unit, level=0):
    unitsize = -1
    if isinstance(unit, IBinaryUnit):
      unitinput = unit.getInput()
      # use the input
      # ...
      unitsize = unitinput.getCurrentSize()
    s = '  ' * level + unit.getName()
    if unitsize >= 0:
      s += ' (%d bytes)' % unitsize
    print(s)

    # recurse over children units
    for c in unit.getChildren():
      self.checkUnit(c, level + 1)
