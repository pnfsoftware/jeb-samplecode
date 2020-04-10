import os
import sys
from com.pnfsoftware.jeb.util.io import IO
from com.pnfsoftware.jeb.client.api import IScript
from com.pnfsoftware.jeb.core.units import INativeCodeUnit
from com.pnfsoftware.jeb.core.units.code import ICodeUnit, ICodeItem
from com.pnfsoftware.jeb.core.output.text import ITextDocument
from com.pnfsoftware.jeb.core.util import DecompilerHelper
from com.pnfsoftware.jeb.core.units.code.asm.decompiler import INativeSourceUnit
from com.pnfsoftware.jeb.core.units.code.android import IDexUnit, DexDecompilerExporter
from com.pnfsoftware.jeb.core.output.text import TextDocumentUtil
"""
This sample script decompiles a given file using JEB.
It can be run on the command-line using JEB's built-in Jython interpreter.

How to run (eg, on Windows):
  $ jeb_wincon.bat -c --srv2 --script=DecompileFile.py -- INPUT_FILE OUTPUT_DIR

For additional details, refer to:
https://www.pnfsoftware.com/jeb/manual/faq/#can-i-execute-a-jeb-python-script-from-the-command-line
"""
class DecompileFile(IScript):
  def run(self, ctx):
    self.ctx = ctx

    argv = ctx.getArguments()
    if len(argv) < 2:
      print('Provide an input file and the output folder')
      return

    self.inputFile = argv[0]
    self.outputDir = argv[1]

    self.decompileDex = True
    self.decompileNative = False

    print('Processing file: ' + self.inputFile + '...')
    ctx.open(self.inputFile)

    prj = ctx.getMainProject()
    # note: replace IDexUnit by ICodeUnit to decompile all code (incl. native)
    # replace IDexUnit by INativeCodeUnit to decompile native code only
    for codeUnit in prj.findUnits(IDexUnit):
      self.decompileCodeUnit(codeUnit)


  def decompileCodeUnit(self, codeUnit):
    # make sure the code unit is processed
    if not codeUnit.isProcessed():
      if not codeUnit.process():
        print('The code unit cannot be processed!')
        return

    decomp = DecompilerHelper.getDecompiler(codeUnit)
    if not decomp:
      print('There is no decompiler available for code unit %s' % codeUnit)
      return

    outdir = os.path.join(self.outputDir, codeUnit.getName() + '_decompiled')
    print('Output folder: %s' % outdir)

    if self.decompileNative and isinstance(codeUnit, INativeCodeUnit):
      for m in codeUnit.getMethods():
        a = m.getAddress()
        print('Decompiling: %s' % a)
        srcUnit = decomp.decompile(a)
        if srcUnit:
          self.exportSourceUnit(srcUnit, outdir)

    elif self.decompileDex and isinstance(codeUnit, IDexUnit):
      exp = DexDecompilerExporter(decomp)
      exp.setOutputFolder(IO.createFolder(outdir))

      # limit to 1 minute max per method
      exp.setMethodTimeout(1 * 60000)

      # limit to 15 minutes (total)
      exp.setTotalTimeout(15 * 60000)

      # set a callback to output real-time information about what's being decompiled
      from com.pnfsoftware.jeb.util.base import ProgressCallbackAdapter
      class DecompCallback(ProgressCallbackAdapter):
        def message(__self__, msg):
          print(msg)
      exp.setCallback(DecompCallback())

      # decompile & export
      if not exp.export():
        cnt = len(exp.getErrors())
        i = 1
        for sig, err in exp.getErrors().items():
          print('%d/%d DECOMPILATION ERROR: METHOD %s: %s' % (i, cnt, sig, err))
          i += 1


  def exportSourceUnit(self, srcUnit, outdir):
    ext = srcUnit.getFileExtension()
    if isinstance(srcUnit, INativeSourceUnit):
      filename = srcUnit.getName() + '.' + ext
      dirpath = outdir
    else:
      csig = srcUnit.getFullyQualifiedName()
      filename = csig[1:len(csig)-1] + '.' + ext
      dirpath = os.path.join(outdir, filename[:filename.rfind('/') + 1])

    if not os.path.exists(dirpath):
      os.makedirs(dirpath)

    doc = srcUnit.getSourceDocument()
    text = TextDocumentUtil.getText(doc)

    filepath = os.path.join(outdir, filename)
    with open(filepath, 'wb') as f:
      f.write('// Decompiled by JEB v%s\n\n' % self.ctx.getSoftwareVersion())
      f.write(text.encode('utf-8'))
