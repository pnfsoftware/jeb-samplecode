import os
from com.pnfsoftware.jeb.core.units.code.android import IDexUnit
from com.pnfsoftware.jeb.core.util import DecompilerHelper
from com.pnfsoftware.jeb.client.api import IScript, IconType, ButtonGroupType
from com.pnfsoftware.jeb.core import RuntimeProjectUtil
from com.pnfsoftware.jeb.core.units.code import ICodeUnit, ICodeItem
from com.pnfsoftware.jeb.core.output.text import ITextDocument
"""
*** DEPRECATED ***
This script is largely inefficient. Use IDexDecompilerUnit.decompileMethod(msig, context) to decompile a specific method.
Refer to the sample script DecompileSingleMethod.py.
"""
class DecompileDexMethod(IScript):

  # fetch this dynamically
  targetMethod = 'Lcom/pnfsoftware/raasta/AppHelp;->onCreate(Landroid/os/Bundle;)V'

  def run(self, ctx):
    raise Exception('DEPRECATED')

    self.ctx = ctx

    dex = ctx.getMainProject().findUnit(IDexUnit)
    javaMethod = self.getDecompiledMethod(dex, targetMethod)
    if not javaMethod:
      print('The method was not found or was not decompiled')
      return

    print('Java Method: %s (%s)' % (javaMethod, javaMethod.getName()))


  def getDecompiledMethod(self, dex, msig):
    m = dex.getMethod(msig)
    if not m:
      return None

    c = m.getClassType()
    if not c:
      return None

    decomp = DecompilerHelper.getDecompiler(dex)
    if not decomp:
      return None

    csig = c.getSignature(False)
    javaUnit = decomp.decompile(csig)
    if not javaUnit:
      return None

    msig0 = m.getSignature(False)
    for m in javaUnit.getClassElement().getMethods():
      if m.getSignature() == msig0:
        return m
    return None
