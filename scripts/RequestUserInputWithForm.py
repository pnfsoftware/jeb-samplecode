#?description=Demo how to generate a simple UI form to request for multiple inputs
#?shortcut=
from com.pnfsoftware.jeb.client.api import IScript, IGraphicalClientContext
"""
Sample script for JEB Decompiler.
Requires JEB>=5.12.
"""
class RequestUserInputWithForm(IScript):
  def run(self, ctx):
    if not isinstance(ctx, IGraphicalClientContext):
      print('This script must be run within a graphical client')
      return

    # a simple form
    values = ctx.displaySimpleForm('Form 1', 'Please provide your details', 'First name', '', 'Last name', '')
    if values:
      print('Info: %s, %s' % (values[1], values[0]))
