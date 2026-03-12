#?type=gendec-ir
from com.pnfsoftware.jeb.core.units.code.asm.decompiler.ir.opt import AbstractEOptimizer

'''
Skeleton for an Intermediate Representation (IR) optimizer plugin for gendec, JEB's generic decompiler.
This Python plugin is executed during the decompilation pipeline of a routine.

How to use:
- Drop this file in your JEB's coreplugins/scripts/ sub-directory
- Make sure to have the setting `.LoadPythonPlugins = true` in your JEB's bin/jeb-engines.cfg file

For additional information regarding gendec IR optimizer plugins, refer to:
- the Manual (www.pnfsoftware.com/jeb/manual)
- the API documentation: https://www.pnfsoftware.com/jeb/apidoc/reference/com/pnfsoftware/jeb/core/units/code/asm/decompiler/ir/opt/package-summary.html
'''
class EOptSamplePython(AbstractEOptimizer):  # we extend AbstractEOptimizer for convenience, instead of implementing IEOptimizer from scratch
  # note: Python script optimizers are singleton instances!
  # the engine will instantiate and provide a single instance for all decompilation threads
  # therefore, if you are using object attributes, make sure to provide support for concurrency
  # (this restriction does not apply to Java script optimizers, as well as full-blown jar optimizers;
  # each decompilation thread has its own unique instance of such optimizer objects)
  # for this reason (as well as others), moderately complex IR optimizers should be written in Java

  def __init__(self):
    # default super constructor is called, will set the plugin type to NORMAL (see DOptimizerType constant)
    self.logger.debug('EOptSamplePython: instantiated')

  def perform(self):
    # UNCOMMENT: message the developer
    self.logger.debug('EOptSamplePython: the optimizer is running')
    #self.logger.debug('GenDecIROptimizerSample: executed: %s', self.cfg.format())

    # UNCOMMENT: some random work...
    #for blk in self.cfg:  # BasicBlock (of IEStatement)
    #  for insn in blk:  # IEStatement
    #    pass

    # if a value >0 is returned, the decompiler will assume that IR is being transformed and this IR optimizer will be called again
    return 0  # no optimization is performed
