"""
Sample UI client script for PNF Software' JEB2.
Requires: JEB 2.1

This script demonstrates how to use the JEB2 UI API to query and augment the views offered by JEB2 UI clients.

Refer to SCRIPTS.TXT for more information.
"""

import time

from java.lang import Runnable, Thread

from com.pnfsoftware.jeb.client.api import IScript, IGraphicalClientContext


class JEB2UIDemo(IScript):
  def run(self, ctx):
    if not isinstance(ctx, IGraphicalClientContext):
      print('This script must be run within a graphical client')
      return

    # enumerate all unit views (views representing units) and fragments within those views
    views = ctx.getViews()
    for view in views:
      print('- %s' % view.getLabel())
      fragments = view.getFragments()
      for fragment in fragments:
        print('  - %s' % view.getFragmentLabel(fragment))

    # focus the second viw
    if len(views) >= 2:
      views[1].setFocus()

    # done