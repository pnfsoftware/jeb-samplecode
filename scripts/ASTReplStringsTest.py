import time

from com.pnfsoftware.jeb.client.api import IScript, IGraphicalClientContext
from com.pnfsoftware.jeb.core import RuntimeProjectUtil
from com.pnfsoftware.jeb.core.actions import Actions, ActionContext, ActionXrefsData
from com.pnfsoftware.jeb.core.events import JebEvent, J
from com.pnfsoftware.jeb.core.output import AbstractUnitRepresentation, UnitRepresentationAdapter
from com.pnfsoftware.jeb.core.units.code import ICodeUnit, ICodeItem
from com.pnfsoftware.jeb.core.units.code.java import IJavaSourceUnit, IJavaStaticField, IJavaNewArray, IJavaConstant, IJavaCall, IJavaField, IJavaMethod, IJavaClass

class ASTReplStringsTest(IScript):
  def run(self, ctx):
    prj = ctx.getMainProject()

    unit = prj.findUnits(IJavaSourceUnit).get(0)

    self.replcnt = 0
    self.cstbuilder = unit.getFactories().getConstantFactory()
    self.checkElement(None, unit.getClassElement())

    unit.notifyListeners(JebEvent(J.UnitChange))
    print('Replaced %d strings' % self.replcnt)

  def checkElement(self, parent, e):
    if isinstance(e, IJavaConstant) and e.isString():
      parent.replaceSubElement(e, self.cstbuilder.createString('blah_' + str(time.time())))
      self.replcnt += 1

    for subelt in e.getSubElements():
      self.checkElement(e, subelt)
