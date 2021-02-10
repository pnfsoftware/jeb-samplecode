#?description=Customize the metadata of a code unit (and see rendering in the metadata overview bar in GUI)
#?shortcut=
import time
from java.util import ArrayList
from com.pnfsoftware.jeb.client.api import IScript, IGraphicalClientContext
from com.pnfsoftware.jeb.core import RuntimeProjectUtil
from com.pnfsoftware.jeb.core.units import IInteractiveUnit, MetadataGroup, MetadataGroupType
from com.pnfsoftware.jeb.core.units.code import ICodeUnit
"""
Sample script JEB Decompiler.
"""
class CustomizeMetadata(IScript):

  def run(self, ctx):
    prj = ctx.getMainProject()
    assert prj, 'Need a project'

    # pick the first code unit offered by the project
    unit = prj.findUnit(ICodeUnit)
    print('Unit: %s' % unit)

    # the metadata manager is optional (a unit may choose to not provide one)
    mm = unit.getMetadataManager()
    if not mm:
      print('The unit does not have a metadata manager')
      return

    # create a new metadata group that will hold RGB color values    
    g = mm.getGroupByName('custom')
    if not g:
      print('Creating new metadata group (type: RGB) ...')
      g = MetadataGroup('custom', MetadataGroupType.RGB)
      mm.addGroup(g)
      print('Done')

    # mark the beginning of every class; they will be rendered in the overview bar in the client
    for iclass, c in enumerate(unit.getClasses()):
      targetAddress = c.getAddress()

      print('Adding a piece of metadata at address "%s" ...' % targetAddress)
      g.setData(targetAddress, 0x00FF30)
      print('Done')

      print('If the unit has a text document representation with a an Overview bar, do a Refresh to visualize the metadata')

      print('Listing all metadata for this unit (if possible) ...')
      for g1 in mm.getGroups():
        print('- Group %s (type: %s)' % (g1.getName(), g1.getType()))
        alldata = g1.getAllData()
        if alldata == None:
          print('(This group manager does not allow metadata enumeration)')
        else:
          for k in alldata:
            print('  - at "%s" -> %s' % (k, alldata[k]))

    unit.notifyGenericChange()
