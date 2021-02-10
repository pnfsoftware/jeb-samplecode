#?description=Focus the first view found that contains a fragment named 'Disassembly', and select and focus that fragment.
#?shortcut=
from com.pnfsoftware.jeb.client.api import IScript
"""
Sample script for JEB Decompiler.
"""
class FocusDisassembly(IScript):
  def run(self, ctx):
    success = focusDisassemblyFragment(ctx)
    print('Focused Disassembly fragment: %s' % success)

def getDisassemblyFragment(view):
  for fragment in view.getFragments():
    if view.getFragmentLabel(fragment) == 'Disassembly':
      return fragment

def focusDisassemblyFragment(ctx):
  for view in ctx.getViews():
    fragment = getDisassemblyFragment(view)
    if fragment:
      view.setFocus()
      view.setActiveFragment(fragment)
      return True
  return False
