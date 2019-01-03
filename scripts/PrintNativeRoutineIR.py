"""
Sample script for JEB Decompiler.

===> How to use:
Two modes:
- Using the UI desktop client:
  - load a binary file into JEB 3.0.8+
  - make sure GlobalAnalysis for code plugins is enabled (it is by default)
  - then run the script: File, Scripts, Run...
  - the script will process your loaded executable
- Using the command line:
  - run like: jeb_wincon.bat -c --srv2 --script=<THIS_SCRIPT> -- <BINARY_FILE>
  - the script will create a JEB project and process the file provided on the command line

===> What is it:
This script demonstrates how to retrieve and print out the Intermediate Representation of a decompiled routine.

===> Additional references:
- reference blog post: [TODO]
- highly recommended (else you will have much difficulty building upon the code below): follow the tutorials on www.pnfsoftware.com/jeb/devportal
- for Native code and Native Decompilers: the com.pnfsoftware.jeb.core.units.code.asm package and sub-packages 
- see API documentation at www.pnfsoftware.com/jeb/apidoc: Native code unit and co, Native decompiler unit and co.

Refer to SCRIPTS.TXT for additional information on how to execute JEB scripts.

Comments, questions, needs more details? message on us on Slack or support@pnfsoftware.com -- Nicolas Falliere
"""

from com.pnfsoftware.jeb.client.api import IScript
from com.pnfsoftware.jeb.core import RuntimeProjectUtil, Artifact
from com.pnfsoftware.jeb.core.units import INativeCodeUnit
from com.pnfsoftware.jeb.core.units.code.asm.type import TypeUtil
from com.pnfsoftware.jeb.core.units.code.asm.decompiler import INativeSourceUnit
from com.pnfsoftware.jeb.core.util import DecompilerHelper
from com.pnfsoftware.jeb.core.input import FileInput

from java.io import File

class PrintNativeRoutineIR(IScript):

  def run(self, ctx):
    # retrieve JEB's engines from the provided IClientContext
    engctx = ctx.getEnginesContext()
    if not engctx:
      print('Back-end engines not initialized')
      return

    # retrieve the current project (must exist)
    projects = engctx.getProjects()
    if projects:
      project = projects[0]
    else:
      argv = ctx.getArguments()
      if len(argv) < 1:
        print('No project found, please provide an input contract file')
        return

      self.inputFile = argv[0]
      print('Processing ' + self.inputFile + '...')

      # create a project
      project = engctx.loadProject('Project')

      # load and process the artifact
      artifact = Artifact('Artifact', FileInput(File(self.inputFile)))
      project.processArtifact(artifact)

      project = engctx.getProjects()[0]

    # retrieve the primary code unit (must be the result of an EVM contract analysis)
    units = RuntimeProjectUtil.findUnitsByType(project, INativeCodeUnit, False)
    if not units:
      print('No native code unit found')
      return
    unit = units[0]
    print('Native code unit: %s' % unit)

    # GlobalAnalysis is assumed to be on (default)
    decomp = DecompilerHelper.getDecompiler(unit)
    if not decomp:
      print('No decompiler unit found')
      return

    # retrieve a handle on the method we wish to examine
    method = unit.getInternalMethods().get(0)#('sub_1001929')
    src = decomp.decompile(method.getName(True))
    if not src:
      print('Routine was not decompiled')
      return
    print(src)
    
    decompTargets = src.getDecompilationTargets()
    print(decompTargets)

    decompTarget = decompTargets.get(0)
    ircfg = decompTarget.getContext().getCfg()
    # CFG object reference, see package com.pnfsoftware.jeb.core.units.code.asm.cfg
    print("+++ IR-CFG for %s +++" % method)
    print(ircfg.formatSimple())
