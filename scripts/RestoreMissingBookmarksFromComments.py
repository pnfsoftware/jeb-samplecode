#?description=Restore missing bookmarks from special comments
#?shortcut=

from com.pnfsoftware.jeb.client.api import IScript
from com.pnfsoftware.jeb.core.units import IInteractiveUnit
from com.pnfsoftware.jeb.core import RuntimeProjectUtil

class RestoreMissingBookmarksFromComments(IScript):
  def run(self, ctx):
    prj = ctx.getMainProject()
    if not prj:
      return
    favcomments = []
    for unit in RuntimeProjectUtil.getAllUnits(prj):
      self.retrieve(unit, favcomments)
    print('Retrieved %d bookmarks (stored as special meta-comments)' % len(favcomments))
    bm = prj.getBookmarkManager()
    cnt = 0
    for unit, addr, desc in favcomments:
      if not bm.get(unit, addr):
        print('Restoring: \'%s\' (@ %s in %s' % (desc, addr, unit))
        bm.set(unit, addr, desc)
        cnt += 1
    print('Restored %d bookmarks' % cnt)

  def retrieve(self, unit, li):
    if not isinstance(unit, IInteractiveUnit):
      return
    cm = unit.getCommentManager()
    if not cm:
      return
    for e in cm.getComments().entrySet():
       addr = e.getKey()
       com = e.getValue()
       for mc in com.getMetaComments():
         s = mc.toString()
         if s.endswith(' (FAVORITE)'):
           li.append((unit, addr, s[:-11]))
