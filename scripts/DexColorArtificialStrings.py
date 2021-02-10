#?description=Visualize artificial (e.g. decrypted) strings in the navbar
#?shortcut=
from com.pnfsoftware.jeb.client.api import IScript
from com.pnfsoftware.jeb.core import RuntimeProjectUtil
from com.pnfsoftware.jeb.core.output import ItemClassIdentifiers
from com.pnfsoftware.jeb.core.units import MetadataGroup, MetadataGroupType, AddressPrefixMetadataGroup
from com.pnfsoftware.jeb.core.units.code.android import IDexUnit
from com.pnfsoftware.jeb.core.units.code.android.dex import DexPoolType
"""
Sample script for JEB Decompiler.
This script will update the navbar and generate colors where artificial strings are being used.
Note: artificial strings are strings that were not originally present in the dex pool(s), e.g. auto-decrypted strings.
Demo: open com.parental.control.v4.apk; run a Global Analysis; execute the script
"""
class DexColorArtificialStrings(IScript):
  def run(self, ctx):
    f = ctx.getFocusedFragment()
    if not f:
      print('Set the focus on a UI fragment, and position the caret on a valid address')
      return

    unit = f.getUnit()
    if not isinstance(unit, IDexUnit):
      print('Focus a fragment representing a dex unit')
      return

    mm = unit.getMetadataManager()
    if not mm:
      print('The unit does not have a metadata manager')
      return

    g = mm.getGroupByName('astrings')
    if not g:
      g = AddressPrefixMetadataGroup(unit, 'astrings')
      mm.addGroup(g)

    for s in unit.getStrings():
      if s.isArtificial():
        #print('String: %s' % s)
        refs = unit.getReferenceManager().getReferences(DexPoolType.STRING, s.getIndex())
        for ref in refs:
          a = ref.getInternalAddress()
          #print('Coloring at: %s' % a)
          pos = a.find('+')
          if pos >= 0: a = a[:pos]
          success = g.setData(a, ItemClassIdentifiers.STRING_GENERATED)

    unit.notifyGenericChange()
