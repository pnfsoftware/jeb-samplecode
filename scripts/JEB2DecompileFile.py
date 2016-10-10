# -*- coding: utf-8 -*-

"""
This script decompiles a given file using JEB. It can be run on the command-line using JEB's built-in Jython interpreter.

How to run:
- The command line below assumes that this file was dropped in your JEB's scripts/ folder
- Command-line: java -Djeb.engcfg=../bin/jeb-engines.cfg -Djeb.lickey=xxxxxxxxxxxxxxxxxx -jar ../bin/cl/jeb.jar --script=JEB2DecompileFile.py --libdir=. -- FILE OUTPUT_DIR

For additional details, refer to:
https://www.pnfsoftware.com/jeb2/manual/faq/#can-i-execute-a-jeb-python-script-from-the-command-line
"""

import os
import sys

from com.pnfsoftware.jeb.client.api import IScript, IconType, ButtonGroupType
from com.pnfsoftware.jeb.core import JebCoreService, ICoreContext, Artifact, RuntimeProjectUtil
from com.pnfsoftware.jeb.core.dao import IFileDatabase
from com.pnfsoftware.jeb.core.dao.impl import JEB2FileDatabase
from com.pnfsoftware.jeb.core.input import FileInput
from com.pnfsoftware.jeb.core.units.code import ICodeUnit, ICodeItem
from com.pnfsoftware.jeb.core.output.text import ITextDocument
from com.pnfsoftware.jeb.core.util import DecompilerHelper

from java.io import File

class JEB2DecompileFile(IScript):

  def run(self, ctx):
    self.ctx = ctx

    argv = ctx.getArguments()
    if len(argv) < 2:
      return

    self.inputFile = argv[0]
    self.outputDir = argv[1]

    print('Decompiling ' + self.inputFile + '...')

    engctx = ctx.getEnginesContext()

    if not engctx:
      print('Back-end engines not initialized')
      return
    
    # Create a project
    project = engctx.loadProject('PlaceholderProjectName')

    if not project:
      print('Failed to open a new project')
      return

    # Add the input file as a project artifact
    artifact = Artifact('PlaceholderArtifactName',FileInput(File(self.inputFile)))
    project.processArtifact(artifact)

    # Decompile code units
    codeUnits = RuntimeProjectUtil.findUnitsByType(project, ICodeUnit, False)
    for codeUnit in codeUnits:
      self.decompileForCodeUnit(codeUnit)

    print('Done.')

  def decompileForCodeUnit(self, codeUnit):
    decomp = DecompilerHelper.getDecompiler(codeUnit)
    if not decomp:
      print('There is no decompiler available for code unit %s' % codeUnit)
      return

    outdir = os.path.join(self.outputDir, codeUnit.getName() + '_decompiled')
    print('Output folder: %s' % outdir)

    allClasses = codeUnit.getClasses()
    for c in allClasses:
      # do not decompile inner classes
      if (c.getGenericFlags() & ICodeItem.FLAG_INNER) == 0:
        a = c.getAddress()
        srcUnit = decomp.decompile(a)
        if srcUnit:
          self.exportSourceUnit(srcUnit, outdir)


  def exportSourceUnit(self, srcUnit, outdir):
    ext = srcUnit.getFileExtension()

    if ext == 'java':
      csig = srcUnit.getFullyQualifiedName()
      subpath = csig[1:len(csig)-1] + '.java'
      dirname = subpath[:subpath.rfind('/') + 1]

      dirpath = os.path.join(outdir, dirname)
      if not os.path.exists(dirpath):
        os.makedirs(dirpath)

      doc = self.getTextDocument(srcUnit)
      if not doc:
        print('The source text document was not found')
        return False

      text = self.formatTextDocument(doc)

      filepath = os.path.join(outdir, subpath)
      f = open(filepath, 'w')
      f.write('// Decompiled by JEB v%s\n\n' % self.ctx.getSoftwareVersion())
      f.write(text.encode('utf-8'))
      f.close()

    else:
      print('Does not know how to export source types: %s' % ext)
      return False

    
  def getTextDocument(self, srcUnit):
    formatter = srcUnit.getFormatter()
    if formatter and formatter.getDocumentPresentations():
      doc = formatter.getDocumentPresentations()[0].getDocument()
      if isinstance(doc, ITextDocument):
        return doc
    return None
  

  def formatTextDocument(self, doc):
    s = ''
    # retrieve the entire document -it's a source file,
    # no need to buffer individual parts. 10 MLoC is enough 
    alldoc = doc.getDocumentPart(0, 10000000)
    for line in alldoc.getLines():
      s += line.getText().toString() + '\n'
    return s