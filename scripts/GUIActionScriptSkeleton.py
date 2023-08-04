#?description=Demo how to chain GUI actions without blocking the UI thread.
#?shortcut=
from com.pnfsoftware.jeb.client.api import IScript
from java.lang import Runnable
"""
Sample script for JEB Decompiler.

Demo how to chain GUI actions without blocking the UI thread.

Background: the UI thread of the GUI client for JEB is an event-based executor for stubs of code.
Client scripts are meant to execute relatively short actions on the UI thread, and terminate, or
execute more heavy-weight processing on worker threads (e.g. via ctx.executeAsync) and then
terminate. In either scenario, the UI thread is hogged or blocked for the duration of the action.

How to chain UI actions to mimic behaviors to what higher-level macro programs would do?
Example: we want to create a project, add an artifact, wait for it to be loaded, wait for the
client to create various views and fragments, then select a fragment and navigate to it.

Although the JEB scripting API is not truly designed to chain UI actions, it is relatively
straight-forward to obtain the behavior by encapsulating chunks of code, and scheduling them on
the UI thread for execution, when required.
"""

CTX = None  # com.pnfsoftware.jeb.client.api.IGraphicalClientContext

class GUIActionScriptSkeleton(IScript):
  def run(self, ctx):
    global CTX
    CTX = ctx
    # --> ENTRY POINT
    print('A0')
    CTX.uiExecute(T1())  # execute A1 asap, return before the execution is finished

class T1(Runnable):
  def run(self):
    # --> ACTION 1
    print('A1')
    CTX.uiExecuteWithDelay(3000, T2())  # execute A2 in +3 seconds, return asap

class T2(Runnable):
  def run(self):
    # --> ACTION 2
    print('A2')
    CTX.uiExecuteBlocking(T3())  # CAREFUL, will block until T3 is fully executed!

class T3(Runnable):
  def run(self):
    # --> ACTION 3
    print('A3')  # done
