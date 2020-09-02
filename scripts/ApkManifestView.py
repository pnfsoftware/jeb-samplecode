from com.pnfsoftware.jeb.client.api import IScript
from com.pnfsoftware.jeb.core.units.code.android import IApkUnit
from com.pnfsoftware.jeb.core.output.text import TextDocumentUtil
"""
JEB sample script showing how to retrieve the object representing an Android Manifest.
"""
class ApkManifestView(IScript):

  def run(self, ctx):
    # current IRuntimeProject
    prj = ctx.getMainProject()
    # find the first IApkUnit in the project
    apk = prj.findUnit(IApkUnit)
    # retrieve the IXmlUnit representing the Android Manifest
    man = apk.getManifest()

    # 1) print the manifest (first presentation offered by the unit)
    doc = man.getFormatter().getPresentation(0).getDocument()
    print(TextDocumentUtil.getText(doc))

    # 2) retrieve the org.w3c.dom.Document
    doc = man.getDocument()
    # ...