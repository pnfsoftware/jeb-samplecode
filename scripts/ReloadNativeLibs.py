# -*- coding: utf-8 -*-
"""
Script for JEB Decompiler.

Scan and register newly-added native type libvraries (typelibs) and signature libraries (siglibs)
"""

from com.pnfsoftware.jeb.client.api import IScript

# IScript reference: https://www.pnfsoftware.com/jeb/apidoc/reference/com/pnfsoftware/jeb/client/api/IScript.html
class ReloadNativeLibs(IScript):

  # ctx: IClientContext (reference: https://www.pnfsoftware.com/jeb/apidoc/reference/com/pnfsoftware/jeb/client/api/IClientContext.html)
  def run(self, ctx):
    ctx.getEnginesContext().getTypeLibraryService().rescan()
    ctx.getEnginesContext().getNativeSignatureDBManager().rescan()