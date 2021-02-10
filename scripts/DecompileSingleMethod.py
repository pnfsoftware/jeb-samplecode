#?description=Decompile a single method.
#?shortcut=
from com.pnfsoftware.jeb.client.api import IScript
from com.pnfsoftware.jeb.core.util import DecompilerHelper
from com.pnfsoftware.jeb.core.units.code import ICodeUnit, IDecompilerUnit, DecompilationContext, DecompilationOptions
"""
Sample script for JEB Decompiler.
The class containing the target method is itself not decompiled; inner classes of the method, if any, are not decompiled either.
The decompiled code is displayed in a text box.
"""
class DecompileSingleMethod(IScript):

  def run(self, ctx):
    self.ctx = ctx

    f = ctx.getFocusedFragment()
    if not f:
      print('Set the focus on a UI fragment, and position the caret somewhere in the method you would like to decompile.')
      return

    addr = f.getActiveAddress()
    unit = f.getUnit()
    if not isinstance(unit, ICodeUnit):
      print('Not a code unit: %s' % unit)
      return

    m = unit.getMethod(addr)
    if not m:
      print('Not a method at address: %s' % addr)
      return

    decomp = DecompilerHelper.getDecompiler(unit)
    if not decomp:
      print('Cannot acquire decompiler for unit: %s' % decomp)
      return

    # *** decompilation Options and Context are optional ***
    # here, we're creating an Options object to:
    # - override the decompiler settings (if any), and cap method decompilation to 30 seconds
    # - prevent the decompilation of inner classes or any deferred decompilations: we decompile the target and only the target
    opt = DecompilationOptions.Builder.newInstance().flags(IDecompilerUnit.FLAG_NO_INNER_DECOMPILATION|IDecompilerUnit.FLAG_NO_DEFERRED_DECOMPILATION).maxTimePerMethod(30000).build()
    if not decomp.decompileMethod(m.getSignature(), DecompilationContext(opt)):
      print('Failed decompiling method')
      return

    text = decomp.getDecompiledMethodText(m.getSignature())
    #print(text)
    r = ctx.displayText("Decompiled Method: %s" % m.getName(), text, True)
    #print(r)
