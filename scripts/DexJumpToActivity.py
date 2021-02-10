#?description=Jump from an activity name (selected in the Android XML Manifest) to its corresponding bytecode definition in the DEX disassembly fragment
#?shortcut=
from com.pnfsoftware.jeb.client.api import IScript, IGraphicalClientContext, IUnitView
from com.pnfsoftware.jeb.core.units import IUnit, IXmlUnit
from com.pnfsoftware.jeb.core.units.code.android import IDexUnit
from com.pnfsoftware.jeb.core import RuntimeProjectUtil
"""
Sample script for JEB Decompiler.
This JEB UI script allows the user to jump from an activity name (selected in the Android XML
Manifest) to its corresponding bytecode definition in the DEX disassembly fragment.
"""
class DexJumpToActivity(IScript):

  def run(self, ctx):
    prj = ctx.getMainProject()
    assert prj, 'Need a project'

    if not isinstance(ctx, IGraphicalClientContext):
      print('This script must be run within a graphical client')
      return

    fragment = ctx.getFocusedView().getActiveFragment()
    if type(fragment.getUnit()) is IXmlUnit:
      print('Select the Manifest XML view')
      return

    # make sure that the fragment has the focus, els the item would not be considered active
    aname = fragment.getActiveItemAsText()
    if not aname:
      print('Select the activity name')
      return

    # activity name is relative to the package name
    if aname.startswith('.'):
      # unit is the Manifest, of type IXmlUnit; we can retrieve the XML document
      # note: an alternate way would be to retrieve the top-level IApkUnit, and use getPackageName()
      dom = fragment.getUnit().getDocument()
      pname = dom.getElementsByTagName("manifest").item(0).getAttribute("package")
      #print('Package name: %s' % pname)    
      aname = pname + aname

    print('Activity name: %s' % aname)

    addr = 'L' + aname.replace('.', '/') + ';'
    print('Target address: %s' % addr)

    unit = RuntimeProjectUtil.findUnitsByType(prj, IDexUnit, False).get(0)
    if not unit:
      print('The DEX unit was not found')
      return

    ctx.openView(unit)
    # this code assumes that the active fragment is the disassembly (it may not be; strong script should focus the assembly fragment)
    ctx.getFocusedView().getActiveFragment().setActiveAddress(addr)
