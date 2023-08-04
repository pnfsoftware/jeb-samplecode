#?description=Demo how to chain GUI actions without blocking the UI thread.
#?shortcut=
from com.pnfsoftware.jeb.client.api import IScript
from java.lang import Runnable
"""
Sample script for JEB Decompiler.

Demo how to chain GUI actions without blocking the UI thread.

Refer to GUIActionScriptSkeleton.py for details about scripting GUI actions.
"""
CTX = None

class GUIActionScriptDemo(IScript):
  def run(self, ctx):
    # globals to be used by all GUI action stubs
    global CTX
    CTX = ctx

    path = ctx.displayFileOpenSelector('Select a file')
    assert path, 'Need a valid file path'

    # close any existing project
    if ctx.getMainProject():
      ctx.closeMainProject()

    # create a new project, analyze one artifact file
    ctx.open(path)

    # give some time for GUI fragments (e.g. disass) to be created and focused
    CTX.uiExecuteWithDelay(2000, T1())

class T1(Runnable):
  def run(self):
    print(CTX.getViews())
