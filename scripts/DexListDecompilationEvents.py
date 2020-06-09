from com.pnfsoftware.jeb.core.units.code.android import IDexUnit, IDexDecompilerUnit
from com.pnfsoftware.jeb.core.util import DecompilerHelper
from com.pnfsoftware.jeb.client.api import IScript, IconType, ButtonGroupType
from com.pnfsoftware.jeb.core import RuntimeProjectUtil
from com.pnfsoftware.jeb.core.units.code import ICodeUnit, ICodeItem
from com.pnfsoftware.jeb.core.output.text import ITextDocument
"""
JEB script: list a dexdec object (IDexDecompilerUnit) decompilation events stored in the global event queue.
"""
class DexListDecompilationEvents(IScript):

  def run(self, ctx):
    self.ctx = ctx
    prj = ctx.getMainProject()
    for dexdec in prj.findUnits(IDexDecompilerUnit):
      print('Listing events for %s:' % dexdec)
      for e in dexdec.getGlobalDecompilationEvents():
        print(e)
