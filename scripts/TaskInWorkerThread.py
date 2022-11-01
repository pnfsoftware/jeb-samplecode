#?description=Run an interruptible task in a worker thread
#?shortcut=
import time
from java.lang import Runnable, Thread
from com.pnfsoftware.jeb.client.api import IScript, IGraphicalClientContext
"""
Sample script for JEB Decompiler.
"""
class TaskInWorkerThread(IScript):
  def run(self, ctx):
    if not isinstance(ctx, IGraphicalClientContext):
      print('This script must be run within a graphical client')
      return
    # will start a worker thread and run the task; a pop-up will be shown to provide a way to interrupt the task
    ctx.executeAsync('Counting...', SimpleTask())
    print('Done.')

class SimpleTask(Runnable):
  def run(self):
    for i in range(10):
      # react to user pressing Cancel
      if Thread.interrupted():
        print('The task was interrupted')
        break
      print('Counter: %d' % i)
      time.sleep(1)
