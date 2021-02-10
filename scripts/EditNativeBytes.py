#?description=Write memory bytes of a native unit
#?shortcut=
from com.pnfsoftware.jeb.client.api import IScript
from com.pnfsoftware.jeb.util.encoding import Conversion
from com.pnfsoftware.jeb.core.units import INativeCodeUnit
"""
Sample script for JEB Decompiler
"""
class EditNativeBytes(IScript):

  # ctx:IGraphicalClientContext
  def run(self, ctx):
    f = ctx.getFocusedFragment()
    assert f, 'Need a focused fragment'

    text = ctx.displayQuestionBox("Write byte", "Address:", "")
    if not text:
      return
    addr = int(text, 16)

    text = ctx.displayQuestionBox("Write byte", "Value to write at 0x%X:" % addr, "")
    if not text:
      return
    val = int(text, 16)

    u = f.getUnit()
    if not isinstance(u, INativeCodeUnit):
      return

    u.undefineItem(addr)
    u.getMemory().writeByte(addr, val)
    u.notifyGenericChange()
