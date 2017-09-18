"""
This JEB UI script allows the user to jump from an activity name (selected in the Android XML
Manifest) to its corresponding bytecode definition in the DEX disassembly fragment.

Requires JEB 2.3.5+
"""

from com.pnfsoftware.jeb.client.api import IScript, IGraphicalClientContext, IUnitView
from com.pnfsoftware.jeb.core.units import IUnit, IXmlUnit
from com.pnfsoftware.jeb.core.units.code.android import IDexUnit
from com.pnfsoftware.jeb.core import RuntimeProjectUtil

class DexJumpToActivity(IScript):

  def run(self, ctx):
    engctx = ctx.getEnginesContext()
    if not engctx:
      print('Back-end engines not initialized')
      return

    projects = engctx.getProjects()
    if not projects:
      print('There is no opened project')
      return

    if not isinstance(ctx, IGraphicalClientContext):
      print('This script must be run within a graphical client')
      return

    prj = projects[0]

    fragment = ctx.getFocusedView().getActiveFragment()
    if type(fragment.getUnit()) is IXmlUnit:
      print('Select the Manifest XML view')
      return

    aname = fragment.getActiveItemAsText()
    if not aname:
      print('Select the activity name')
      return

    # activity name is relative to the package name
    if aname.startswith('.'):
      # unit is the Manifest, of type IXmlUnit; we can retrieve the XML document
      # note: an alternate way would be to retrieve the top-level IApkUnit, and use getPackageName()
      pname = fragment.getUnit().getDocument().getElementsByTagName("manifest").item(0).getAttribute("package")
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
