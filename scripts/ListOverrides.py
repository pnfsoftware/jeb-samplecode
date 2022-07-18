#?description=Lists overrides (in the generic terms) of the currently active method or field using a generic ActionOverridesData object
#?shortcut=
from com.pnfsoftware.jeb.client.api import IScript
from com.pnfsoftware.jeb.core.actions import Actions, ActionContext, ActionOverridesData
"""
Sample script for JEB Decompiler.
"""
class ListOverrides(IScript):
  def run(self, ctx):
    unit = ctx.getFocusedUnit()
    assert unit, 'Need a focused unit fragment'

    current_item = ctx.getFocusedItem()
    assert current_item, 'Need a focused item'

    data = ActionOverridesData()
    if unit.prepareExecution(ActionContext(unit, Actions.QUERY_OVERRIDES, current_item.getItemId(), None), data):
      for a in data.getAddresses():
        print('Found method: %s' % a)
