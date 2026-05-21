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
    # will start a worker thread and run the task; 
    # a pop-up will be shown to provide a way to interrupt the task
    try:
        ctx.executeAsync('Counting...', SimpleTask())
        # under the hood com.pnfsoftware.jeb.util.concurrent.ThreadUtil.start( ) is used to launch the thread

    except  (InterruptedException,KeyboardInterrupt,):
        print('The task was interrupted')

        #https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/lang/Thread.html#interrupt()
        #"Interrupts this thread.
        # If none of the previous conditions hold then this thread's interrupt status will be set."
        #BUT
        # If this thread is blocked in an invocation of the wait() ... join(), ... sleep..., then 
        # its interrupt status will be cleared !!! 
        # and it will receive an InterruptedException.
        
        # By this we set the missing interrupted status so SimpleTask gets the signal to stop
        SimpleTask.WorkerThread_crutch.interrupt()
    else:
        print('Done.')

class SimpleTask(Runnable):
  def run(self):
    SimpleTask.WorkerThread_crutch=Thread.currentThread()
    
    for i in range(10):
      
      # react to user pressing Cancel
      if Thread.interrupted():
        print('The task was interrupted')
        break

      print('Counter: %d' % i)
      time.sleep(1)
