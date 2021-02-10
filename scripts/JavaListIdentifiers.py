#?description=Enumerate the IJavaIdentifiers (parameters, local vars) of IJavaMethod objects of a decompiled IJavaClass. Rename some identifiers. List all identifiers.
#?shortcut=
from com.pnfsoftware.jeb.client.api import IScript
from com.pnfsoftware.jeb.core.units.code.java import IJavaSourceUnit
"""
Sample script for JEB Decompiler.
Enumerate the IJavaIdentifiers (parameters, local vars) of IJavaMethod objects of a decompiled IJavaClass. Rename some identifiers. List all identifiers 
"""
class JavaListIdentifiers(IScript):

  def run(self, ctx):
    prj = ctx.getMainProject()
    assert prj, 'Need a project'

    f = ctx.getFocusedFragment()
    assert f, 'Need a focused fragment'

    # assume a fragment is focused, assumed it is backed by an IUnit
    unit = f.getUnit()
    if not isinstance(unit, IJavaSourceUnit): return

    # assume the unit is an IJavaSourceUnit
    c = unit.getClassElement()

    # 1) DEMO: rename some method identifiers
    # enumerate all methods in the class (NOTE: nested classes are not enumerated, this is just a demo script)
    idx = 0
    for m in c.getMethods():
      identifiers = m.getIdentifierManager().getIdentifiers()
      print('METHOD: %s: identifiers=%s' % (m, identifiers))
      for ident in identifiers:
        print('  current=%s original=%s debug=%s' % (unit.getIdentifierName(ident), ident.getName(), ident.getDebugName()))

        # rename all non-this identifiers (including param names) that do not carry a debug name
        if ident.getName() != 'this' and ident.getDebugName() == None:
          newName = 'RENAMED_%d' % idx
          idx += 1
          print('  -> renaming to %s' % newName)
          unit.setIdentifierName(ident, newName)

    # 2) DEMO: note that all identifiers are uniquely identified by their CodeCoordinates
    # they can be enumerated via IDexUnit (the parent of an IDexDecompilerUnit, itself parent of all IJavaSourceUnit)
    dexdec = unit.getParent()
    dex = dexdec.getParent()
    print('All renamed identifiers: %s' % dex.getRenamedIdentifiers())
