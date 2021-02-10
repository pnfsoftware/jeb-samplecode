#?description=Add and process additional artifacts into a JEB project
#?shortcut=
from java.io import File
from com.pnfsoftware.jeb.client.api import IScript
from com.pnfsoftware.jeb.core import Artifact
from com.pnfsoftware.jeb.core.input import FileInput
"""
Sample script for JEB Decompiler.
This script demonstrates how to add and process additional artifacts into a JEB project.
"""
class AddArtifact(IScript):
  path = 'PATH_TO_FILE'  # customize

  def run(self, ctx):
    prj = ctx.getMainProject()
    assert prj, 'Need a project'

    artifactFile = File(self.path)
    a = Artifact(artifactFile.getName(), FileInput(artifactFile))
    print(a)

    la = prj.processArtifact(a)
    print(la)

