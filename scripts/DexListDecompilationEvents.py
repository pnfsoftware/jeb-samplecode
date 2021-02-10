#?description=List a dexdec object (IDexDecompilerUnit) decompilation events stored in the global event queue
#?shortcut=
from com.pnfsoftware.jeb.core.units.code.android import IDexUnit, IDexDecompilerUnit
from com.pnfsoftware.jeb.core.util import DecompilerHelper
from com.pnfsoftware.jeb.client.api import IScript, IconType, ButtonGroupType
from com.pnfsoftware.jeb.core import RuntimeProjectUtil
from com.pnfsoftware.jeb.core.units.code import ICodeUnit, ICodeItem
from com.pnfsoftware.jeb.core.output.text import ITextDocument
"""
Sample script for JEB Decompiler.
Note that dexdec's events can be seen in a Decompiler's unit node (Project Explorer view), "Events" tab
"""
class DexListDecompilationEvents(IScript):
  def run(self, ctx):
    prj = ctx.getMainProject()
    assert prj, 'Need a project'
    for dexdec in prj.findUnits(IDexDecompilerUnit):
      print('Listing events for %s:' % dexdec)
      for e in dexdec.getGlobalDecompilationEvents():
        print(e)
