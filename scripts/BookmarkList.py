#?description=List custom bookmarks saved by BookmarkSet
#?shortcut=
#?deprecated
import datetime
import json
import time
from com.pnfsoftware.jeb.client.api import IScript, IconType, ButtonGroupType
from com.pnfsoftware.jeb.core import RuntimeProjectUtil
from BookmarkSet import BookmarkSet
"""
Sample script for JEB Decompiler.

For demo purposes only, this script should not be used to list bookmarks.
JEB uses its own bookmarks facility for projects.
"""
class BookmarkList(IScript):

  def run(self, ctx):
    prj = ctx.getMainProject()
    assert prj, 'Need a project'

    bmstr = prj.getData(BookmarkSet.BMKEY)
    if not bmstr:
      ctx.displayMessageBox('Bookmarks', 'No recorded boolmarks yet!', IconType.INFORMATION, None)
      return

    bm = json.loads(bmstr)      
    log('Current bookmarks (%d): %s' % (len(bm), bm))

    headers = ['Timestamp', 'Full Unit Path', 'Name', 'Fragment', 'Address', 'Comment']
    rows = []
    for uid, labelmap in bm.items():
      for label, addrmap in labelmap.items():
        for addr, e in addrmap.items():
          unitpath, unitname, comment, ts = e
          # note we're appended uid, but it won't be displayed (per the header's spec above, which specifies 6 columns - not 7)
          rows.append([datetime.datetime.fromtimestamp(ts).ctime(), unitpath, unitname, label, addr, comment, uid])

    index = ctx.displayList('Bookmarks', 'List of currently set bookmarks in the active project', headers, rows)
    if index < 0:
      return

    sel = rows[index]
    uid, label, addr = int(sel[6]), sel[3], sel[4]
    log('Selected: uid=%d,fragment=%s,addr=%s' % (uid, label, addr))

    unit = RuntimeProjectUtil.findUnitByUid(prj, uid)
    if not unit:
      print('Unit with uid=%d was not found in the project or no longer exists!' % uid)
      return

    if not ctx.openView(unit):
      print('Could not open view for unit!')
    else:
      f = ctx.findFragment(unit, label, True)
      if not f:
        print('Fragment "%s" not found!' % label)
      elif addr:
        f.setActiveAddress(addr)

def log(s):
  print(s)
