import os
from com.pnfsoftware.jeb.client.api import IScript
from com.pnfsoftware.jeb.core import IPlugin, Version
from com.pnfsoftware.jeb.core.units.code.java import IJavaSourceUnit, JavaElementType
"""
Sample client script for PNF Software' JEB.
This script demonstrates how to rename method parameters of decompiled Java methods.
In the example below, generic parameter names ('argX') are renamed based on their type.
Req: JEB 3.6+
"""
class RenameJavaMethodParameters(IScript):
  def run(self, ctx):
    if ctx.getSoftwareVersion() < Version.create(3, 6, 0, 0, 1):
      raise Exception('This script requires JEB 3.6-beta or above')
    prj = ctx.getMainProject()
    # process all Java decompiled source units
    for unit in prj.findUnits(IJavaSourceUnit):
      self.process(unit, unit.getClassElement())

  def process(self, unit, e, level=0):
    if e.getElementType() == JavaElementType.Method:
      if not e.isExternal():
        print 'Method: %s' % e
        namemap = {}
        params = e.getParameters()
        for param in e.getParameters():
          ident = param.getIdentifier()
          original_name = ident.getName()
          if original_name != 'this':
            debug_name = ident.getDebugName()
            effective_name = unit.getIdentifierName(ident)
            print '  Parameter: %s (debug name: %s) (effective: %s)' % (param, debug_name, effective_name)
            if not effective_name and not debug_name and original_name.startswith('arg') and param.getType().isClassOrInterface():
              t = str(param.getType())
              simplename = t[t.rfind('.') + 1:].lower()
              v = namemap.get(simplename, 0)
              namemap[simplename] = v + 1
              effective_name = '%s%d' % (simplename , v)
              print '  -> Renaming to: %s' % effective_name
              unit.setIdentifierName(ident, effective_name)

    elts = e.getSubElements()
    for e in elts:
      self.process(unit, e, level+1)
