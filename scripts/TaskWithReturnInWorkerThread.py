#?description=Run an interruptible task in a worker thread
#?shortcut=
import time
from java.lang import Thread
from java.util.concurrent import Callable
from com.pnfsoftware.jeb.client.api import IScript, IGraphicalClientContext
"""
Sample script for JEB Decompiler.
"""
class TaskWithReturnInWorkerThread(IScript):
  def run(self, ctx):
    if not isinstance(ctx, IGraphicalClientContext):
      print('This script must be run within a graphical client')
      return
    # will start a worker thread and run the task; a pop-up will be shown to provide a way to interrupt the task
    r = ctx.executeAsyncWithReturn('Counting... and returning a value', SimpleTask())
    print r

# note the use of Callable here
class SimpleTask(Callable):
  def call(self):
    for i in range(5):
      # react to user pressing Cancel
      if Thread.interrupted():
        print('The task was interrupted')
        break
      print('Counter: %d' % i)
      time.sleep(1)
    return 123
