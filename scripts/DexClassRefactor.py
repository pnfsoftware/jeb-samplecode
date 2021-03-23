#?description=Refactor a dex class, i.e. rename and repackage automatically (if necessary)
#?shortcut=
from com.pnfsoftware.jeb.client.api import IScript, IGraphicalClientContext
from com.pnfsoftware.jeb.core.units.code import ICodeUnit
from com.pnfsoftware.jeb.core.units.code.android.dex import IDexClass
"""
Sample script for JEB Decompiler.
"""
class DexClassRefactor(IScript):
  def run(self, ctx):
    prj = ctx.getMainProject()
    if not isinstance(ctx, IGraphicalClientContext):
      return

    dex = ctx.getFocusedUnit()
    assert dex, 'Need focus on dex'
    item = ctx.getFocusedItem()
    assert item, 'Need caret on item'
    o = dex.getObjectById(item.getItemId())
    assert isinstance(o, IDexClass), 'Not a class item'

    r = ctx.displayQuestionBox('Rename', 'Input the new type descriptor:', o.getSignature())
    if not r:
      return  # user aborted
    if not (r.startswith('L') and r.endswith(';')):
      return  # illegal descriptor
    if r == o.getSignature():
      return  # nothing to do

    pos = r.rfind('/')
    if pos < 0:
      psig = ''
      cname = r[1:-1]
    else:
      psig = r[0:pos+1]
      cname = r[pos+1:-1]

    print('Renaming class to: %s' % cname)
    o.setName(cname)

    pkg = dex.getPackage(psig)
    if not pkg:
      print('Creating package: %s' % psig)
      # note: addPackage() has a glitch, only accepts high-level (dot-separated) forms
      pkg = dex.addPackage(psig[1:-1].replace('/', '.'))
      if not pkg:
        print('Cannot create package: %s' % psig)
        return
    print('Moving: %s to %s' % (o, pkg))

    success = dex.moveToPackage(o, pkg)
    if success:
      dex.notifyGenericChange()
