#?description=Add and analyze an additional artifact into an existing project
#?shortcut=
from java.io import File
from com.pnfsoftware.jeb.client.api import IScript
from com.pnfsoftware.jeb.core import Artifact
from com.pnfsoftware.jeb.core.input import FileInput
"""
Sample script for JEB Decompiler.
"""
class AddArtifact(IScript):
  path = ''  # UPDATE

  def run(self, ctx):
    assert path, 'Specify the artifact path in the demo script'

    prj = ctx.getMainProject()
    assert prj, 'Need a project'

    artifactFile = File(self.path)
    a = Artifact(artifactFile.getName(), FileInput(artifactFile))
    print(a)

    la = prj.processArtifact(a)
    print(la)
