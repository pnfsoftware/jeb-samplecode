#?description=Scan and register newly-added native type libvraries (typelibs) and signature libraries (siglibs)
#?shortcut=
from com.pnfsoftware.jeb.client.api import IScript
"""
Sample script for JEB Decompiler.
"""
class ReloadNativeTypelibsAndSiglibs(IScript):
  def run(self, ctx):
    engctx = ctx.getEnginesContext()
    engctx.getTypeLibraryService().rescan()
    engctx.getNativeSignatureDBManager().rescan()
