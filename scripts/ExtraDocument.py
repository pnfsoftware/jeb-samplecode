#?description=Generate an extra document for the first found interactive unit (new tab: Quotes)
#?shortcut=
from java.util import ArrayList
from com.pnfsoftware.jeb.client.api import IScript, IGraphicalClientContext
from com.pnfsoftware.jeb.core import RuntimeProjectUtil
from com.pnfsoftware.jeb.core.output import AbstractUnitRepresentation, UnitRepresentationAdapter
from com.pnfsoftware.jeb.core.output.text.impl import Line, StaticTextDocument
from com.pnfsoftware.jeb.core.units import IInteractiveUnit
"""
Sample script JEB Decompiler.
"""
class ExtraDocument(IScript):
  def run(self, ctx):
    prj = ctx.getMainProject()
    assert prj, 'Need a project'

    # pick the first interactive unit
    unit = prj.findUnit(IInteractiveUnit)
    assert unit, 'Need a unit'
    print('Unit: %s' % unit)

    # retrieve the formatter, which is a producer of unit representations
    formatter = unit.getFormatter()

    # create an extra document (text document), wrap it in a representtion
    lines = ArrayList()
    lines.add(Line('There are two hard problems in computer science: cache invalidation, naming things, and off-by-one errors.'))
    lines.add(Line('   - Phil Karlton (and others)'))
    extraDoc = StaticTextDocument(lines)
    extraPres = UnitRepresentationAdapter(100, 'Quotes', False, extraDoc)

    # add the newly created representation to our unit, and notify clients
    # the second argument indicates that the presentation should be persisted when saving the project
    formatter.addPresentation(extraPres, True)
    unit.notifyGenericChange()

    # done - if you are running a UI client, the additional document should be displayed
    # in a fragment view (eg, sub-tab in the case of the official RCP client)
