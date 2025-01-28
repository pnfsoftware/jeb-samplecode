#?description=Decompile a file provided to JEB
#?shortcut=
import getopt
import os
import sys
import time
from com.pnfsoftware.jeb.util.io import IO
from com.pnfsoftware.jeb.util.logging import GlobalLog
from com.pnfsoftware.jeb.client.api import IScript, IGraphicalClientContext
from com.pnfsoftware.jeb.core.units import INativeCodeUnit, UnitUtil
from com.pnfsoftware.jeb.core.units.code import ICodeUnit, ICodeItem
from com.pnfsoftware.jeb.core.output.text import ITextDocument
from com.pnfsoftware.jeb.core.util import DecompilerHelper
from com.pnfsoftware.jeb.core.units.code.asm.decompiler import INativeSourceUnit
from com.pnfsoftware.jeb.core.units.code.android import IDexUnit, DexDecompilerExporter
from com.pnfsoftware.jeb.core.output.text import TextDocumentUtil
from com.pnfsoftware.jeb.util.base import ProgressCallbackAdapter
"""
Sample script for JEB Decompiler.
- This script decompiles some or all code units of the project
- If run on the command line, the provided input file will be analyzed
- It makes use of the 'decompiler exporter' objects to provide fast decompilation.

How to run & options: see usage() below.

For additional details, refer to:
https://www.pnfsoftware.com/jeb/manual/faq/#can-i-execute-a-jeb-python-script-from-the-command-line
"""
class DecompileFile(IScript):

  def usage(self):
    print('''DecompileFile.py -- demo how to use JEB to decompile code for automation purposes.

How to run:
  $ <JEB> -c --script=DecompileFile.py -- [options] INPUT_FILE OUTPUT_DIR

Options:
  -h            : display help and exit
  -v            : increase verbosity
  --mtimeout=T  : decompilation timeout for individual methods, in seconds
  --decompile=L : comma-separated list of targets to decompile, e.g. 'dalvik,arm64'
                  Supported targets:
                  dalvik    : decompile x86 32-bit code
                  x86       : decompile x86 32-bit code
                  x64       : decompile x86 64-bit code
                  arm       : decompile Arm code
                  arm64     : decompile Arm 64-bit (aarch64) code
                  all       : decompile all code decompilable by your JEB instance
    ''')
    return


  def run(self, ctx):
    # for messages issued by JEB, limit ourselves to warn and above
    GlobalLog.setCutoffLevel(GlobalLog.LEVEL_WARN);

    self.ctx = ctx

    self.verbose = False
    self.inputFile = None
    self.inputDir = None
    self.method_timeout = -1
    self.decomp_dalvik = False
    self.decomp_x86 = False
    self.decomp_x64 = False
    self.decomp_arm = False
    self.decomp_arm64 = False
    self.decomp_all = False

    args = ctx.getArguments()
    iarg = 0
    for arg in args:
      if not arg.startswith('-'):
        break
      if arg == '-h':
        self.usage()
        return
      elif arg == '-v':
        self.verbose = True
      elif arg.startswith('--mtimeout='):
        self.method_timeout = int(arg[11:])
      elif arg.startswith('--decompile='):
        for elt in arg[12:].split(','):
          elt = elt.strip().lower()
          if elt in ('dalvik', 'dex'):
            self.decomp_dalvik = True
          elif elt == 'x86':
            self.decomp_x86 = True
          elif elt in ('x64', 'x86_64', 'x86-64', 'amd64'):
            self.decomp_x64 = True
          elif elt == 'arm':
            self.decomp_arm = True
          elif elt in ('arm64', 'aarch64'):
            self.decomp_x64 = True
          elif elt == 'all':
            self.decomp_all = True
          else:
            print('Unknown processor for decompilation: %s' % elt)
            self.usage()
            return
      else:
        print('Unknown option: %s' % arg)
        self.usage()
        return
      iarg += 1

    if iarg >= len(args):
        print('Provide an input file')
        return
    self.inputFile = args[iarg]
    iarg += 1

    if iarg >= len(args):
        print('Provide the output folder')
        return
    self.outputDir = args[iarg]
    iarg += 1

    if self.method_timeout: print('Method decompilation timeout: %ds' % self.method_timeout)
    if self.decomp_all: print('Decompiling all')
    if self.decomp_dalvik: print('Decompiling Dalvik')
    if self.decomp_x86: print('Decompiling x86')
    if self.decomp_x64: print('Decompiling x64')
    if self.decomp_arm: print('Decompiling Arm')
    if self.decomp_arm64: print('Decompiling Arm64')

    print('Processing file: %s...' % self.inputFile)
    ctx.open(self.inputFile)

    prj = ctx.getMainProject()
    assert prj, 'Need a project'

    t0 = time.time()
    for codeUnit in prj.findUnits(ICodeUnit):
      self.decompileCodeUnit(codeUnit)

    exectime = time.time() - t0
    print('Exectime: %f' % exectime)


  def decompileCodeUnit(self, codeUnit):
    upath = UnitUtil.buildFullyQualifiedUnitPath(codeUnit)

    proceed = False
    if self.decomp_all:
      proceed = True
    elif isinstance(codeUnit, IDexUnit) and self.decomp_dalvik:
      proceed = True
    elif isinstance(codeUnit, INativeCodeUnit):
      procname = codeUnit.getProcessorName()
      if procname == 'x86' and self.decomp_x86:
        proceed = True
      elif procname == 'x86_64' and self.decomp_x64:
        proceed = True
      elif procname == 'arm' and self.decomp_arm:
        proceed = True
      elif procname == 'arm64' and self.decomp_arm64:
        proceed = True
    if not proceed:
      print('Skipping code: filtered out: %s' % upath)
      return

    # make sure the code unit is processed
    if not codeUnit.isProcessed():
      if not codeUnit.process():
        print('Skipping code: cannot be processed: %s' % upath)
        return

    decomp = DecompilerHelper.getDecompiler(codeUnit)
    if not decomp:
      print('Skipping code: no decompiler available: %s' % upath)
      return

    print('Decompiling code: %s' % upath)

    outdir = os.path.join(self.outputDir, UnitUtil.buildFullyQualifiedUnitPath(codeUnit, True, '_').replace(' ', '-'))
    print('Output folder: %s' % outdir)  # created only if necessary, i.e. some contents was exported

    # DecompilerExporter object
    exp = decomp.getExporter()

    exp.setOutputFolder(IO.createFolder(outdir))

    if self.method_timeout > 0:
      exp.setMethodTimeout(self.method_timeout * 1000)

    #exp.setTotalTimeout(...)

    # set a callback to output real-time information about what's being decompiled
    class DecompCallback(ProgressCallbackAdapter):
      def message(self, _id, msg):
        print('%d/%d: %s' % (self.getCurrent(), self.getTotal(), msg))
    if self.verbose:
      exp.setCallback(DecompCallback())

    # decompile & export
    if not exp.export():
      cnt = len(exp.getErrors())
      i = 1
      for sig, err in exp.getErrors().items():
        print('%d/%d DECOMPILATION ERROR: METHOD %s: %s' % (i, cnt, sig, err))
        i += 1
