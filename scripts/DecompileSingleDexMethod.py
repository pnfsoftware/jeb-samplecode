from com.pnfsoftware.jeb.client.api import IScript, IconType, ButtonGroupType
from com.pnfsoftware.jeb.core import Version
from com.pnfsoftware.jeb.core.util import DecompilerHelper
from com.pnfsoftware.jeb.core.units import UnitUtil
from com.pnfsoftware.jeb.core.units.code import ICodeUnit, IDecompilerUnit, DecompilationContext, DecompilationOptions
"""
This UI script is used to decompile a *single* method.
The class containing the target method is itself not decompiled; inner classes of the method, if any, are not decompiled either.
The decompiled code is displayed in a text box.
"""
class DecompileSingleDexMethod(IScript):

  def run(self, ctx):
    self.ctx = ctx

    if ctx.getSoftwareVersion() < Version.create(3, 17, 0, 0, 1):
      print('You need JEB 3.17+ to run this script!')
      return

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
    opt = DecompilationOptions.Builder().newInstance().flags(IDecompilerUnit.FLAG_NO_INNER_DECOMPILATION|IDecompilerUnit.FLAG_NO_DEFERRED_DECOMPILATION).maxTimePerMethod(30000).build()
    if not decomp.decompileMethod(m.getSignature(), DecompilationContext(opt)):
      print('Failed decompiling method')
      return

    text = decomp.getDecompiledMethodText(m.getSignature())
    #print(text)
    r = ctx.displayText("Decompiled Method: %s" % m.getName(), text, True)
    #print(r)
