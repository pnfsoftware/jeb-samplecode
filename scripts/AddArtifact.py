#?description=Add and analyze an additional artifact into an existing project
#?shortcut=
from java.io import File
from com.pnfsoftware.jeb.client.api import IScript
from com.pnfsoftware.jeb.core import Artifact
from com.pnfsoftware.jeb.core.input import FileInput
import os
"""
Sample script for JEB Decompiler.
"""
class AddArtifact(IScript):

  def run(self, ctx):
    prj = ctx.getMainProject()
    assert prj, 'Need a project'

    path = ctx.displayFileOpenSelector('Select a file to be added to the project')
    assert path and os.path.isfile(path), 'Need a valid artifact file path'

    artifactFile = File(path)
    a = Artifact(artifactFile.getName(), FileInput(artifactFile))
    print('Adding: %s' % a)

    la = prj.processArtifact(a)
    print(la)
