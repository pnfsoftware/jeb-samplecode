#?type=engines

from java.util import Map

from com.pnfsoftware.jeb.core import AbstractEnginesPlugin, IEnginesContext, IPluginInformation, PluginInformation, Version

"""
Sample JEB Engines Plugin. It may be compiled and dropped in coreplugins/, or it may
be kept as a script plugin in coreplugins/scripts/.

Script plugins can be developed and modified while JEB is running.
Please refer to the javadoc of the IEnginesPlugin interface for additional information.

It is advised to write back-end plugins in Java. Consult EngSampleJava.java for the equivalent code as a Java script.
"""
class EngSamplePython(AbstractEnginesPlugin):

  def getPluginInformation(self):
    return PluginInformation("Sample engines plugin in Python", "", "PNF Software", Version.create(0, 1));

  def load(self, engctx):
    self.logger.debug("Sample engines plugin in Python: load()");

  def execute(self, engctx, executionOptions):
    self.logger.debug("Sample engines plugin in Python: execute()")
