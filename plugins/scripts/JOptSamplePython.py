#?type=dexdec-ast
from com.pnfsoftware.jeb.core.units.code.java import AbstractJOptimizer

'''
Skeleton for an Java Abstract Syntax Tree (AST) optimizer plugin for dexdec, JEB's DEX/Dalvik Decompiler.
This Python plugin is executed during the decompilation pipeline of a method.

How to use:
- Drop this file in your JEB's coreplugins/scripts/ sub-directory
- Make sure to have the setting `.LoadPythonPlugins = true` in your JEB's bin/jeb-engines.cfg file

For additional information regarding dexdec AST optimizer plugins, refer to:
- the Manual (www.pnfsoftware.com/jeb/manual)
- the API documentation: https://www.pnfsoftware.com/jeb/apidoc/reference/com/pnfsoftware/jeb/core/units/code/java/package-summary.html

Requires JEB 4.23+.
'''
class JOptSamplePython(AbstractJOptimizer):
  # note: Python script optimizers are singleton instances!
  # the engine will instantiate and provide a single instance for all decompilation threads
  # therefore, if you are using object attributes, make sure to provide support for concurrency
  # (this restriction does not apply to Java script optimizers, as well as full-blown jar optimizers;
  # each decompilation thread has its own unique instance of such optimizer objects)
  # for this reason (as well as others), moderately complex AST optimizers should be written in Java

  def __init__(self):
    # default super constructor is called, will set the plugin type to NORMAL (see JOptimizerType constant)
    self.logger.debug('DexDecASTOptimizerSample: instantiated')

  def perform(self):
    # commonly needed objects for AST optimizers are provided as attributes AbstractJOptimizer and sub-classes
    # if the optimizer is about to work on a IJavaMethod, the AST method object is in attribute `m`
    # if the optimizer is about to work on a IJavaClass, the AST class object is in attribute `c`

    # another commonly used class by IR optimizers is JUtil, containing many utitily routines to access and manipulate the AST
    # more: refer to the API documentation

    # UNCOMMENT: message the developer
    #self.logger.debug('DexDecASTOptimizerSample: executed')

    # if a value >0 is returned, the decompiler will assume that AST is being transformed and this AST optimizer will be called again
    return 0  # no optimization is performed
