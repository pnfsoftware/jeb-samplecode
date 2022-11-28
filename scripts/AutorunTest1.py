#?description=This client script will be autorun at start-up (1), project creation (2), and project reloaded (3)
#?autorun=1,2,3
from com.pnfsoftware.jeb.client.api import IScript
"""
Sample script for JEB Decompiler..
Values for the metadata key autorun (CSL):
  0 (no autorun), 1 (after start-up), 2 (after project creation), 3 (after project reloaded) [default:0]
Values for the metadata key autorun_priority:
  any floating value, a high value means a high priority [default:0]

NOTE the priority of this script: it was left to use the implicit default (0).
At start-up, this script will be run after AutorunTest2, whose priority is a 5.

Requires JEB 4.22+
"""
class AutorunTest1(IScript):
  def run(self, ctx):
    print('AutorunTest1: This script was automatically executed by the client')
