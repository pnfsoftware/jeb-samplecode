#?description=
#?shortcut=
from com.pnfsoftware.jeb.client.api import IScript
from java.lang import Runnable
"""
Sample script for JEB Decompiler.

Demo how to chain GUI actions without blocking the UI thread.
Refer to GUIActionScriptSkeleton.py for details about scripting GUI actions.
"""
CTX = None
PATH_TO_SOME_FILE = r'C:\Users\nicol\jeb2\jeb3-core\core\testdata\dex\raasta-classes.dex'  # TODO: CUSTOMIZE

class GUIActionScriptDemo(IScript):
  def run(self, ctx):
    assert PATH_TO_SOME_FILE, 'Update the PATH_TO_SOME_FILE global!'

    # globals to be used by all GUI action stubs
    global CTX
    CTX = ctx

    # close any existing project
    if ctx.getMainProject():
      ctx.closeMainProject()

    # create a new project, analyze one artifact file
    ctx.open(PATH_TO_SOME_FILE)

    # give some time for GUI fragments (e.g. disass) to be created and focused
    CTX.uiExecuteWithDelay(2000, T1())

class T1(Runnable):
  def run(self):
    print(CTX.getViews())
