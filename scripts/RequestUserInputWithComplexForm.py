#?description=Demo how to generate a UI form to request for complex multiple inputs
#?shortcut=
from com.pnfsoftware.jeb.client.api import IScript, IGraphicalClientContext
from com.pnfsoftware.jeb.client.api import FormEntry
from java.util.function import Predicate
"""
Sample script for JEB Decompiler.
Requires JEB>=5.12.
"""
class RequestUserInputWithComplexForm(IScript):
  def run(self, ctx):
    if not isinstance(ctx, IGraphicalClientContext):
      print('This script must be run within a graphical client')
      return

    # used to validate first name and last name entries
    class NameValidator(Predicate):
      def __init__(self, minlen):
        self.minlen = minlen
      def test(self, val):
        return len(val) >= self.minlen

    # a more complicated form with multi-line field, inline headers, and a validator
    values = ctx.displayForm('Form 2', 'Please provide your full details',
      FormEntry.Text('First name', '', FormEntry.INLINE, NameValidator(3), 0, 0),
      FormEntry.Text('Last name', '', FormEntry.INLINE, NameValidator(6), 0, 0),
      FormEntry.Text('Address', 'default address', 0, None, 40, 5),
    )
    if values:
      print(values)

