#?description=Demo how to invoke common dialog boxes
#?shortcut=
from com.pnfsoftware.jeb.client.api import IScript, IGraphicalClientContext
from com.pnfsoftware.jeb.client.api import IconType, ButtonGroupType
"""
Sample script for JEB Decompiler.
"""
class RequestUserInput(IScript):
  def run(self, ctx):
    if not isinstance(ctx, IGraphicalClientContext):
      print('This script must be run within a graphical client')
      return

    value = ctx.displayQuestionBox('Input', 'Enter a random string', '3')
    if value != None:
      ctx.displayMessageBox('Information', 'The value was %s' % value, IconType.INFORMATION, ButtonGroupType.OK)

    # other dialogs: see IGraphicalClientContext.displayXxx() methods
