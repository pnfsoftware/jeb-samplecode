#?description=Demo how to use the property manager programmatically
#?shortcut=
from com.pnfsoftware.jeb.client.api import IScript
from com.pnfsoftware.jeb.core.units.code.android import IDexDecompilerUnit
"""
Sample script for JEB Decompiler.
Reference doc to review:
- IPropertyDefinitionManager
- IPropertyManager
"""
class DexdecDisableEmulation(IScript):
  def run(self, ctx):
    prj = ctx.getMainProject()
    assert prj, 'Need a project'
    u = prj.findUnit(IDexDecompilerUnit)
    if u:
      # the associated PDM (property definition manager) of a PM (property manager) lists the properties, their types, legal values, etc.
      # they are also listed here for reference: https://www.pnfsoftware.com/jeb/manual/engines-configuration/
      # other objects can be configured via a PM, including JEB's engines context and its primary GUI client
      u.getPropertyManager().setInteger('EmulationSupport', 0)  # disable the emulator!