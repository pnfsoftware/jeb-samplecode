#?description=Rename dex classes to the optionl names provided in the debug metadata
#?shortcut=
from com.pnfsoftware.jeb.client.api import IScript
from com.pnfsoftware.jeb.core.units.code.android import IDexUnit
"""
Sample script for JEB Decompiler.
"""
class RenameDexClassesToDebugNames(IScript):

  def run(self, ctx):
    prj = ctx.getMainProject()
    assert prj, 'Need a project'

    for unit in prj.findUnits(IDexUnit):
      self.process(unit)

  def process(self, dex):
    cnt = 0
    for c in dex.getClasses():
      name = c.getName()
      idx = c.getSourceStringIndex()
      if idx >= 0:
        debugName = dex.getString(idx).getValue()
        #print(debugName)
        if debugName:
          debugName = debugName.replace('.java', '')
          if debugName != name and c.setName(debugName):
            print('Renamed class %s to %s' % (name, debugName))
            cnt += 1
    if cnt > 0:
      dex.notifyGenericChange()
