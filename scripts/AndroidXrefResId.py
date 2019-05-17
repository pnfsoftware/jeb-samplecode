#?shortcut=Shift+X

# Android APK cross-reference navigation from Resource XML units to DEX Disassembly unit
# Nicolas Falliere, PNF Software
# Usage:
# - Position the caret on a resource id in XML (eg, '  <public id="0x7f05000d" ...')
# - Press Shift+X, select your target xref, and press Enter to navigate to it

from com.pnfsoftware.jeb.client.api import IScript, IGraphicalClientContext
from com.pnfsoftware.jeb.core.units.code.android import IApkUnit, IDexUnit
from com.pnfsoftware.jeb.core import IPlugin, Version
from com.pnfsoftware.jeb.core.units.code.android.dex import IDalvikInstruction
from com.pnfsoftware.jeb.util.encoding import Conversion

class AndroidXrefResId(IScript):

  def run(self, ctx):
    if not isinstance(ctx, IGraphicalClientContext):
      print('This script must be run within a graphical client')
      return

    apk = ctx.getMainProject().findUnit(IApkUnit)
    if not apk:
      print('APK unit not found')
      return

    dex = ctx.getMainProject().findUnit(IDexUnit)
    if not dex:
      print('DEX unit not found')
      return

    f = ctx.getFocusedFragment()
    if not f:
      print('Focus must be on a UI fragment')
      return
    sel = f.getSelectedText() or f.getActiveItemAsText()
    if not sel:
      print('Please position the caret on an item or select a piece of text')
      return
    resid = Conversion.stringToInt(sel)
    if not resid:
      print('Not a resource ID: "%s"' % sel)
      return
    print('Searching for code xrefs to id: 0x%X' % resid)

    # building a database of integer immediate usage location
    # map: int_imm -> list_of_usage_addresses
    # opti: to avoid rebuilding the map each time the script is called, we cache it in the client transient store
    # (needs JEB 3.4+)
    jeb34 = ctx.getSoftwareVersion() >= Version.create(3, 4, 0, 0, 1)
    immdb = None
    if jeb34: immdb = ctx.getTransientStore().get('intImmDb')
    if immdb == None:
      immdb = {}
      if jeb34: ctx.getTransientStore().put('intImmDb', immdb)
      for m in dex.getMethods():
        if m.isInternal():
          ci = m.getData().getCodeItem()
          if ci:
            for insn in ci.getInstructions():
              for param in insn.getParameters():
                if param.getType() == IDalvikInstruction.TYPE_IMM:
                  val = param.getValue()
                  addr = '%s+%Xh' % (m.getSignature(False), insn.getOffset())
                  if val not in immdb:
                    immdb[val] = []
                  immdb[val].append(addr)
      #print(immdb)

    candidate_addresses = immdb.get(resid)
    if not candidate_addresses:
      print('No location found')
      return

    # pick the best candidate xref; if there are multiple, pop-up a dialog and let the user pick
    if len(candidate_addresses) == 1:
      addr = candidate_addresses[0]
    else:
      rows = []
      for candidate_address in candidate_addresses:
        rows.append([candidate_address])
      print 'Found %d locations: %s' % (len(candidate_address), candidate_address)
      index = ctx.displayList('Select a location (%d candidates)' % len(candidate_addresses), None, ['Addresses'], rows)
      if index < 0:
        return
      addr = candidate_addresses[index]
    print('Navigating to: %s' % addr)

    # find, bring up, and focus on the DEX unit Disassembly fragment
    for view in ctx.getViews(dex):
      for fragment in view.getFragments():
        if view.getFragmentLabel(fragment) == 'Disassembly':
          view.setFocus()
          view.setActiveFragment(fragment)
          fragment.setActiveAddress(addr)
          return
    print('Assembly fragment was not found?')