#?description=Lists all cross-references to the currently active item using a generic ActionXrefsData object
#?shortcut=
from com.pnfsoftware.jeb.client.api import IScript
from com.pnfsoftware.jeb.core.actions import ActionContext
from com.pnfsoftware.jeb.core.actions import ActionXrefsData
from com.pnfsoftware.jeb.core.actions import Actions
"""
Sample script for JEB Decompiler.
"""
class ListCrossReferences(IScript):
  def run(self, ctx):
    unit = ctx.getFocusedUnit()
    assert unit, 'Need a focused unit fragment'
    print(unit.getFormatType())

    current_addr = ctx.getFocusedAddress()
    print(current_addr)

    current_item = ctx.getFocusedItem()
    print(current_item)

    data = ActionXrefsData()
    if unit.prepareExecution(ActionContext(unit, Actions.QUERY_XREFS, 0 if not current_item else current_item.getItemId(), current_addr), data):
      for xref_addr in data.getAddresses():
        print(xref_addr)
