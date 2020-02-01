from com.pnfsoftware.jeb.client.api import IScript
from com.pnfsoftware.jeb.core.units.code.android import IDexUnit

"""
Sample showing:
- how a script can be invoked after a cmdline-provided file has been processed by the JEB UI client
- currently, this script simply searches for a Dex code unit, attempts to find a disassembly fragment for it, and navigate to the cmdline-provided address

How to use:
$ jeb_startup_script --script=ScriptPath -- InputFile AddressToJumpTo

This script can also be used when invoking the JEB UI client via the URI handler 'jeb:'
Example:
- drop this script in your JEB folder scripts/ directory
- open a browser and navigate to the URL: jeb:--script%3DJumpTo.py+--+https%3A%2F%2Fwww.pnfsoftware.com%2Fz.apk+Lcom%2Fpnfsoftware%2Fraasta%2FCoordinatesE6%3B
"""
class JumpTo(IScript):
  def run(self, ctx):
    if len(ctx.getArguments()) < 2:
      return

    # arg[0] is the InputFile
    addr = ctx.getArguments()[1]
    print('Will jump to: %s' % addr)

    dexunit = ctx.getMainProject().findUnit(IDexUnit)
    if dexunit:
      f = ctx.findFragment(dexunit, 'Disassembly', True)
      if f:
        f.setActiveAddress(addr)
