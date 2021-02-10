#?description=
#?shortcut=
#?nolist
from com.pnfsoftware.jeb.client.api import IScript
from com.pnfsoftware.jeb.core import RuntimeProjectUtil
from com.pnfsoftware.jeb.core.output import ItemClassIdentifiers
from com.pnfsoftware.jeb.core.units import MetadataGroup, MetadataGroupType, AddressPrefixMetadataGroup
"""
Package/Class/Method coloring scrip.
We use the AddressPrefixMetadataGroup object to store metadata information, displayed in a text navbar.
"""
class DexColorPackage(IScript):
  def run(self, ctx):
    f = ctx.getFocusedFragment()
    if not f:
      print('Set the focus on a UI fragment, and position the caret on a valid address')
      return

    addr = f.getActiveAddress()
    unit = f.getUnit()
    if not unit or not addr:
      print('No unit or no address at current location')
      return

    mm = unit.getMetadataManager()
    if not mm:
      print('The unit does not have a metadata manager')
      return
    g = mm.getGroupByName(AddressPrefixMetadataGroup.DEFAULT_NAME)
    if not g:
      g = AddressPrefixMetadataGroup(unit)
      mm.addGroup(g)

    addr = unit.getCanonicalAddress(addr)
    addrlist = [addr]
    # hack: include inner classes if addr is a class address
    if addr.find('->') < 0 and addr.endswith(';'):
      addrlist.append(addr[:-1] + '$')

    for a in addrlist:
      if g.getAllData().get(a) != None:
        success = g.setData(a, None)
      else:
        success = g.setData(a, ItemClassIdentifiers.INFO_NORMAL)
      print('%s: %s' % (a, success))

    unit.notifyGenericChange()
