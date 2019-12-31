from com.pnfsoftware.jeb.client.api import IScript
from com.pnfsoftware.jeb.core.events import JebEvent, J
from com.pnfsoftware.jeb.core.units import IUnit, UnitChangeEventData
from com.pnfsoftware.jeb.core.units.code.android import IDexUnit
from com.pnfsoftware.jeb.util.events import IEventListener
"""
Sample client script for PNF Software' JEB.

This script shows how to listen to unit-emitted UnitChange events.
Specifically, the script sets up a listener for changes emitted by a DEX unit.
Refer to IDexUnit and UnitChangeEventData API documentation for details.

Requires JEB 3.9+
"""
class ListenToDexChangeEvents(IScript):

  def run(self, ctx):
    dex = ctx.getMainProject().findUnit(IDexUnit)
    if not dex:
      print('This demo script requires an opened DEX unit')
      return

    # remove stale listeners a previous execution of this script may have added
    for listener in dex.getListeners():
      try:
        # note: a check isinstance(listener, SampleListener) will not work here
        # since class objects are different every time the script is run
        if listener.IN_SCRIPT:  
          dex.removeListener(listener)
      except:
        pass

    # add a fresh listener
    dex.addListener(SampleListener(ctx))
    print('Listening to UnitChange events on: %s' % dex)


class SampleListener(IEventListener):
  IN_SCRIPT = 1

  def __init__(self, ctx):
    self.ctx = ctx

  def onEvent(self, e):
    if isinstance(e, JebEvent) and e.type == J.UnitChange and e.data != None:
      print('++++ %s' % e.data)
      if e.data.type == UnitChangeEventData.CommentUpdate:
        msg = 'New comment at %s (unit %s):\nValue:"%s"\nPrevious:"%s"' % (e.data.location, e.data.target, e.data.value, e.data.previousValue)
        self.ctx.displayMessageBox('Comment update', msg, None, None)