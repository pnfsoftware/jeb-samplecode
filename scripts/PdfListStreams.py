from com.pnfsoftware.jeb.client.api import IScript
from com.pnfsoftware.jeb.core.units import UnitUtil, WellKnownUnitTypes
from com.pnfsoftware.jeb.core.output.text import TextDocumentUtil
"""
This sample script relies on the PDF plugin to enumerate and dump decoded stream documents stored in the Stream sub-units of a parsed PDF unit.
The PDF plugin does not implement a specific sub-interface of IUnit (API), mostly because it is an open-source plugin, available on GitHub.
The script below uses hardcoded unit types and document types to retrieve the objects to be dumped.
An alternative is to use proper PDF plugin types directly, eg, com.pnf.plugin.pdf.unit.IPdfUnit
"""
class PdfListStreams(IScript):

  def run(self, ctx):
    # retrieve the primary unit (first unit of first artifact, assume it exists)
    prj = ctx.getMainProject()
    unit = prj.getLiveArtifact(0).getUnits().get(0)
    if unit.getFormatType() != WellKnownUnitTypes.typePdf:
      raise Exception('Expected a PDF file')

    # [OPTIONAL] refer to https://github.com/pnfsoftware/jeb2-plugin-pdf/tree/master/src/main/java/com/pnf/plugin/pdf
    # the unit retrieved is of the IPdfUnit type, and has additional methods, eg getStatistics() provide a PdfSTatistics object
    print 'Encrypted:', unit.getStatistics().isEncrypted()

    # process all PDF Stream units
    for unit in UnitUtil.findDescendantsByFormatType(unit, 'Stream'):
      # the pdf plugin is lazy, make sure to process sub-units before retrieving data
      if not unit.isProcessed():
        unit.process()

      # retrieve the 'Decoded Stream' text document
      for pres in unit.getFormatter().getDocumentPresentations():
        if pres.getLabel() == 'Decoded Stream':
          doc =  pres.getDocument()
          text = TextDocumentUtil.getText(doc)
          print '%s: %s' % (unit.getName(), text[:50] + '...')  # TODO: eg, dump text to file(s)
