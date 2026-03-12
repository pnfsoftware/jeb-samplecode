#?type=gendec-ast
from com.pnfsoftware.jeb.core.units.code.asm.decompiler.ast.opt import AbstractCOptimizer

'''
Skeleton for an Java Abstract Syntax Tree (AST) optimizer plugin for gendec, JEB's generic decompiler.
This Python plugin is executed during the decompilation pipeline of a method.

How to use:
- Drop this file in your JEB's coreplugins/scripts/ sub-directory
- Make sure to have the setting `.LoadPythonPlugins = true` in your JEB's bin/jeb-engines.cfg file

For additional information regarding dexdec AST optimizer plugins, refer to:
- the Manual (www.pnfsoftware.com/jeb/manual)
- the API documentation: TODO
'''
class COptSamplePython(AbstractCOptimizer):
  # note: Python script optimizers are singleton instances!
  # the engine will instantiate and provide a single instance for all decompilation threads
  # therefore, if you are using object attributes, make sure to provide support for concurrency
  # (this restriction does not apply to Java script optimizers, as well as full-blown jar optimizers;
  # each decompilation thread has its own unique instance of such optimizer objects)
  # for this reason (as well as others), moderately complex AST optimizers should be written in Java

  def __init__(self):
    self.logger.debug('COptSamplePython: instantiated')

  def perform(self):
    self.logger.debug('COptSamplePython: executed')

    # if a value >0 is returned, the decompiler will assume that AST is being transformed and this AST optimizer will be called again
    return 0  # no optimization is performed
