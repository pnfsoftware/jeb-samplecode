"""
Sample script for JEB Decompiler.

Load an Ethereum EVM contract into JEB 3.0.8+ (build on or after Dec 10 2018); then make sure
the GlobalAnalysis for EVM modules is enabled (it is by default), then run the script: File, Scripts, Run...

This script demonstrates how to retrieve the decompiled EVM code of an Ethereum contract.
- The decompiled contract's Abstract Syntax Tree (AST) is walked and its node types are printed
(reference: https://www.pnfsoftware.com/jeb/apidoc/reference/com/pnfsoftware/jeb/core/units/code/asm/decompiler/ast/package-summary.html)
- The individual methods of the contract are retrieved: their AST is also displayed
- The most refined Intermediate Representation (IR) code of each individual method is also displayed
(reference: https://www.pnfsoftware.com/jeb/apidoc/reference/com/pnfsoftware/jeb/core/units/code/asm/decompiler/ir/package-summary.html)

Additional refs:
- highly recommended (else you will have much difficulty building upon the code below): follow the tutorials on www.pnfsoftware.com/jeb/devportal
- for Native code and Native Decompilers: the com.pnfsoftware.jeb.core.units.code.asm package and sub-packages 
- see apidoc at www.pnfsoftware.com/jeb/apidoc: Native code unit and co, Native decompiler unit and co.

More to be published on the blog and technical papers.

Refer to SCRIPTS.TXT for additional information on how to execute JEB scripts.

Comments, questions, needs more details? message on us on Slack or support@pnfsoftware.com -- Nicolas Falliere
"""

from com.pnfsoftware.jeb.client.api import IScript
from com.pnfsoftware.jeb.core import RuntimeProjectUtil
from com.pnfsoftware.jeb.core.units import INativeCodeUnit
from com.pnfsoftware.jeb.core.units.code.asm.type import TypeUtil
from com.pnfsoftware.jeb.core.units.code.asm.decompiler import INativeSourceUnit
from com.pnfsoftware.jeb.core.util import DecompilerHelper

class WalkEvmDecomp(IScript):

  def run(self, ctx):
    # retrieve JEB's engines from the provided IClientContext
    engctx = ctx.getEnginesContext()
    if not engctx:
      print('Back-end engines not initialized')
      return

    # retrieve the current project (must exist)
    projects = engctx.getProjects()
    if not projects:
      print('There is no opened project')
      return

    # retrieve the primary code unit (must be the result of an EVM contract analysis)
    units = RuntimeProjectUtil.findUnitsByType(projects[0], INativeCodeUnit, False)
    if not units:
      return
    unit = units[0]
    print('EVM unit: %s' % unit)

    # GlobalAnalysis is assumed to be on: the contract is already decompiled
    # we retrieve a handle on the EVM decompiler ...
    decomp = DecompilerHelper.getDecompiler(unit)
    print(decomp)
    # ... and retrieve a handle on the decompiled contract's INativeSourceUnit
    src = decomp.decompile("DecompiledContract")
    print(src)
    
    #targets = src.getDecompilationTargets()
    #print(targets) 

    # let's get the contract's AST
    astDecompClass = src.getRootElement()
    # the commented line below will output the entire decompiled source code 
    #print(astDecompClass)
    # here, we walk the AST tree and print the type of each element in the tree
    print("*** AST of contract")
    self.displayASTTree(astDecompClass)
    
    # now, let's retrieve the individual methods implemented in the contract
    methods = unit.getInternalMethods()
    for method in methods:
      # retrieve the INativeSourceUnit of the method
      r = decomp.decompileMethod(method)
      print("*** AST for method: %s" % method.getName(True))
      self.displayASTTree(r.getRootElement())

      # list of INativeDecompilationTarget for a decompiled method
      decompTargets = r.getDecompilationTargets()
      if decompTargets:
        # get the first (generally, only) target object
        decompTarget = decompTargets.get(0)
        # an INativeDecompilationTarget object aggregates many useful objects resulting from the decompilation of a method
        # here, we retrieve the most refined CFG of the Intermediate Representation for the method
        ircfg = decompTarget.getContext().getCfg()
        # CFG object reference, see package com.pnfsoftware.jeb.core.units.code.asm.cfg
        print("++++ IR-CFG for method: %s" % method.getName(True))
        print(ircfg.formatSimple())
      
      # end of demo, we have enough with one method, uncomment to print out the AST and IR of all methods
      break
        
    
  def displayASTTree(self, e0, level=0):
    print('%s%s' % (level*'  ', e0.getElementType()))
    if e0:
      elts = e0.getSubElements()
      for e in elts:
        self.displayASTTree(e, level+1)
