#?description=Perform a global analysis on a dex unit and display decompilation events
#?shortcut=

from com.pnfsoftware.jeb.client.api import IScript
from com.pnfsoftware.jeb.core.units.code import DecompilationOptions, DecompilationContext
from com.pnfsoftware.jeb.core.units.code.android import IDexUnit, IDexDecompilerUnit

"""
Sample script for JEB Decompiler.

Retrieve a dex decompiler (dexdec) instance to decompile all methods,
and retrieve and display interesting decompilation events.
"""
class AndroidGlobalAnalysis(IScript):

  def run(self, ctx):
    prj = ctx.getMainProject()
    dex = prj.findUnit(IDexUnit)
    dexdec = dex.getDecompiler()

    dexdec.resetGlobalDecompilationEvents()

    f = (IDexDecompilerUnit.FLAG_BATCH_DECOMPILATION
            | IDexDecompilerUnit.FLAG_NO_METHOD_AST_GENERATION
            | IDexDecompilerUnit.FLAG_NO_DEFERRED_DECOMPILATION
            | IDexDecompilerUnit.FLAG_NO_INNER_DECOMPILATION
            | IDexDecompilerUnit.FLAG_TEMP_FORCED_REDECOMPILATIONS)
    ctx = DecompilationContext(DecompilationOptions.Builder.newInstance()
            .maxTimePerMethod(1 * 60 * 1000)
            .maxTimeTotal(5 * 60 * 1000)
            .flags(f)
            .build())

    success = dexdec.decompileAllMethods(ctx);
    print(success)

    # see DexDecompilerEvent
    for e in dexdec.getGlobalDecompilationEvents():
      print(e)