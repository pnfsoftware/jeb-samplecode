#?description=Display a sample list box
#?shortcut=
from com.pnfsoftware.jeb.client.api import IScript, IGraphicalClientContext
"""
Sample script for JEB Decompiler.
"""
class WidgetList(IScript):
  def run(self, ctx):
    if not isinstance(ctx, IGraphicalClientContext):
      print('This script must be run within a graphical client')
      return
    value = ctx.displayList('Input', 'foo', ['Col1', 'Col2'], [['abc', 'def'], ['ffff', '']])
    print(value)
