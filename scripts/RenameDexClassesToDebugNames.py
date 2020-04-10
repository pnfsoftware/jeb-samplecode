from com.pnfsoftware.jeb.client.api import IScript
from com.pnfsoftware.jeb.core.units.code.android import IDexUnit
from com.pnfsoftware.jeb.core.events import JebEvent, J
"""
Sample client script for PNF Software' JEB.
"""
class RenameDexClassesToDebugNames(IScript):
  def run(self, ctx):
    prj = ctx.getMainProject()
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
      dex.notifyListeners(JebEvent(J.UnitChange))
