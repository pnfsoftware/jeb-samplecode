#?description=Open and process a file into a JEB project.
#?shortcut=
from com.pnfsoftware.jeb.client.api import IScript
"""
Sample script for JEB Decompiler.
"""
class ProcessFile(IScript):
  def run(self, ctx):
    # if run in headless mode, you could instead use ctx.getArguments() to retrieve the input file
    # if ctx is IGraphicalClientContext (assumed to be the case here), we display a file selector
    path = ctx.displayFileOpenSelector('Select a file for processing')
    if not path:
      return
    # if no project exists, one will be created and the input file processed as the primary artifact
    # if a project exists, the input file will be added to the project and processed
    ctx.open(path)
