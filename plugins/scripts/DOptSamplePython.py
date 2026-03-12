#?type=dexdec-ir
from com.pnfsoftware.jeb.core.units.code.android.ir import AbstractDOptimizer

'''
Skeleton for an Intermediate Representation (IR) optimizer plugin for dexdec, JEB's DEX/Dalvik Decompiler.
This Python plugin is executed during the decompilation pipeline of a method.

How to use:
- Drop this file in your JEB's coreplugins/scripts/ sub-directory
- Make sure to have the setting `.LoadPythonPlugins = true` in your JEB's bin/jeb-engines.cfg file

For additional information regarding dexdec IR optimizer plugins, refer to:
- the Manual (www.pnfsoftware.com/jeb/manual)
- the API documentation: https://www.pnfsoftware.com/jeb/apidoc/reference/com/pnfsoftware/jeb/core/units/code/android/ir/package-summary.html
'''
class DOptSamplePython(AbstractDOptimizer):  # we extend AbstractDOptimizer for convenience, instead of implementing IDOptimizer from scratch
  # note: Python script optimizers are singleton instances!
  # the engine will instantiate and provide a single instance for all decompilation threads
  # therefore, if you are using object attributes, make sure to provide support for concurrency
  # (this restriction does not apply to Java script optimizers, as well as full-blown jar optimizers;
  # each decompilation thread has its own unique instance of such optimizer objects)
  # for this reason (as well as others), moderately complex IR optimizers should be written in Java

  def __init__(self):
    # default super constructor is called, will set the plugin type to NORMAL (see DOptimizerType constant)
    self.logger.debug('DexDecIROptimizerSample: instantiated')

  def perform(self):
    # commonly needed objects for IR optimizers are provided as attributes AbstractDOptimizer:
    # - ctx: the IDMethodContext
    # - cfg: the IR CFG (control flow graph)
    # - irb: IR element builder
    # - tf: a type factory
    # - of: an operator factory
    # - g: the global IR context, referring to other important decompiler objects
    # - dex: the underlying dex file
    # ...
    # as well as useful methods, such as:
    # - cleanGraph(): to be called in structural modifications of teh CFG were made
    # - analyzeChains(): to perform DFA (data flow analysis) if data chains are needed by the optimizer
    # ...
    # and more: refer to the API documentation
    #
    # another commonly used class by IR optimizers is DUtil, containing many utitily routines to access and manipulate the IR

    # UNCOMMENT: message the developer
    #self.logger.debug('DexDecIROptimizerSample: executed: %s', self.cfg.format())

    # UNCOMMENT: some random work...
    #for blk in self.cfg:  # BasicBlock (of IDInstruction)
    #  for insn in blk:  # IDInstruction
    #    if insn.isJcond():
    #      # we found a JCOND instruction, do something
    #      pass

    # if a value >0 is returned, the decompiler will assume that IR is being transformed and this IR optimizer will be called again
    return 0  # no optimization is performed
