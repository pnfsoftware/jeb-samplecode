#?shortcut=Mod1+D

import datetime
import json
import time
from com.pnfsoftware.jeb.client.api import IScript
from com.pnfsoftware.jeb.core import Version
from com.pnfsoftware.jeb.core.units import UnitUtil
"""
JEB Decompiler script for JEB 3.8+ / Nicolas Falliere
What: set, modify, or remove a bookmark.
How: position the caret in any view (text, tree, table) of any unit or document,
  then invoke via CTRL+D on Win/Linux or Command+D on macOS to bookmark that position
  (can be customized by changing the first line of this script)
See also: companion script BookmarkSet.py
"""
class BookmarkSet(IScript):
  BMKEY = 'BOOKMARKS'

  def run(self, ctx):
    if ctx.getSoftwareVersion() < Version.create(3, 8):
      print('You need JEB 3.8+ to run this script!')
      return

    f = ctx.getFocusedFragment()
    if not f:
      print('Set the focus on a UI fragment, and position the caret at the location you would like to bookmark.')
      return

    label = ctx.getFocusedView().getFragmentLabel(f)
    addr = f.getActiveAddress()
    unit = f.getUnit()
    uid = unit.getUid()
    unitname = unit.getName()
    unitpath = UnitUtil.buildFullyQualifiedUnitPath(unit)

    log('Unit: %d (%s)' % (uid, unitpath))
    log('Address: %s' % addr)
    log('Fragment: %s' % label)

    prj = ctx.getMainProject()
    bmstr = prj.getData(BookmarkSet.BMKEY)
    if bmstr != None:
      bm = json.loads(bmstr)
    else:
      bm = {}

    #log('Current bookmarks (%d): %s' % (len(bm), bm))
    log('Current bookmarks: %d' % len(bm))

    labelmap = bm.get(str(uid))
    if labelmap == None:
      labelmap = {}
      bm[uid] = labelmap

    addrmap = labelmap.get(label)
    if addrmap == None:
      addrmap = {}
      labelmap[label] = addrmap

    e = addrmap.get(addr)
    if e:
      log('Found existing entry')
      comment = e[2]
      savedts = e[3]
      title = 'Update a bookmark'
      caption = 'Current comment. (Clear to delete the bookmark.)\nSet on ' + datetime.datetime.fromtimestamp(savedts).ctime()
    else:
      comment = 'bookmarked'
      title = 'Add a bookmark'
      caption = 'Optional comment.'

    comment = ctx.displayQuestionBox(title, caption, comment)
    if comment == None:
      return

    ts = time.time()
    if comment == '':
      log('Removing entry')
      if addr in addrmap:
        del addrmap[addr]
    else:
      log('Adding/modifying entry')
      addrmap[addr] = [unitpath, unitname, comment, ts]

    prj.setData(BookmarkSet.BMKEY, json.dumps(bm), True)

def log(s):
  pass#print(s)