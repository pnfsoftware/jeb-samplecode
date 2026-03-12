#?type=dexdec-ir
from com.pnfsoftware.jeb.core.units.code.android.ir import AbstractDPatternOptimizer
from com.pnfsoftware.jeb.core.units.code.android.ir.compiler import DPatternCompiler
from com.pnfsoftware.jeb.core.units.code.android.ir.compiler.DPatternCompiler import DPattern

'''
Skeleton for an Intermediate Representation (IR) optimizer plugin for dexdec, JEB's DEX/Dalvik Decompiler.
This Python plugin demos how to perform pattern matching and replacing on the IR of decompiled code.

How to use and see this optimizer in action:
- Drop this file in your JEB's coreplugins/scripts/ sub-directory
- Make sure to have the setting `.LoadPythonPlugins = true` in your JEB's bin/jeb-engines.cfg file
- Download https://pnfsoftware.com/other/SampleForDOptDemoReplacePatterns.dex and open it in JEB
- Decompile the foo() method

For additional information on the IR compiler and IR pattern syntax, refer to the ir and ir.compiler packages:
- https://www.pnfsoftware.com/jeb/apidoc/reference/com/pnfsoftware/jeb/core/units/code/android/ir/package-summary.html
- https://www.pnfsoftware.com/jeb/apidoc/reference/com/pnfsoftware/jeb/core/units/code/android/ir/compiler/package-summary.html
'''

class DOptDemoReplacePatterns(AbstractDPatternOptimizer):  # this handy abstract only requires the implementation of getPatterns()
  def getPatterns(self):  # this method provides a list of DPattern objects (IR match&replace objects)
    self.logger.info('DOptDemoReplacePatterns: Running on: %s', self.ctx)
    # $N syntax matches on any side-effect-free expression, such as a var or an imm
    pattern0 = (DPattern.create("Pseudo pattern that does not mean anything")
            .addInput("($1 & $0) | (~($0 ^ $2))")
            .setOutput("$0 + $1")
            .compile(DPatternCompiler.FLAG_SAME_BITSIZE_FOR_LEAVES))
    return [pattern0]
    #
    # More information on DPattern objects
    # - They accept multiple (alternate) inputs, via additional addInput() calls.
    # - They can be provided a verifier object (that verifies a match, if ad-hoc
    #   checks not expressible in the textual input need to take place).
    # - They can be provided a custom replacer (for similar reasons, that is, if
    #   the textual output cannot express how to generate the replacement expression).
    # - Matching can also be done on instructions and sequences of instructions.