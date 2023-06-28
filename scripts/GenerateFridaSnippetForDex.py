#?description=Create a Frida hook for the selected Dex method
#?shortcut=

from com.pnfsoftware.jeb.client.api import IScript
from com.pnfsoftware.jeb.core import Artifact
from com.pnfsoftware.jeb.core.units.code.android import IDexUnit

'''
Python script for JEB Decompiler.

Frida hook generator for Dex methods. Respect original method names, display effective (renamed) names.

Forked from https://github.com/cryptax/misc-code/blob/master/jeb/Jeb2Frida.py
'''
class GenerateFridaSnippetForDex(IScript):

  def run(self, ctx):
    addr = ctx.getFocusedAddress()
    unit = ctx.getFocusedUnit()
    if not addr or not isinstance(unit, IDexUnit):
      print("Position the caret on a Dex method inside a text fragment")
      return

    # clear the bytecode position if the caret inside a method (as opposed to being on the method's header)
    pos = addr.find('+')
    if pos >= 0:
      addr = addr[:pos]
    # retrieve the method object, we'll need that to collect the original and effective (current) names
    m = unit.getMethod(addr)
    if not m:
      print("The selected address does not resolve to a Dex method")
      return

    print("Generating Frida snippet for method: %s" % m.getSignature())
    addr = m.getSignature(False)  # original names

    # original type name (used in the binary)
    cl = m.getClassType().getSignature(False, False)

    # original method name (used in the binary)
    mname = m.getName(False)
    if mname == "<init>":
      mname = "$init"

    # original parameter types (used in the binary)
    partypes = []
    parnames = []
    for i, partype in enumerate(m.getParameterTypes()):
      partypes.append(partype.getSignature(False, False))
      parnames.append("arg%d" % i)  # TODO: retrieve the decompiler-provided param names

    no_return = m.getReturnType().isVoid()

    # the tag rendered in the console will use the method's actual names (i.e. the renames if any), not the original names
    tag = "%s.%s" % (m.getClassType().getSignature(True, False, False), m.getName(True))

    hook = self.generate(tag, cl, mname, partypes, parnames, no_return)

    snippet = "// Frida hook for %s:\nJava.perform(function() {\n%s});\n" % (m.getSignature(), hook)
    print(snippet)

  def generate(self, tag, cl, mname, partypes, parnames, no_return):
    hook = ""
    hook += "  var cl = Java.use('%s');\n" % cl
    hook += "  var m = cl.%s" % mname

    if partypes:
      hook += ".overload("
      for i, partype in enumerate(partypes):
        if i > 0:
          hook += ", "
        hook += "'%s'" % partype
      hook += ")"
    hook += ";\n"
    
    hook += "  m.implementation = function(%s) {\n" % (', '.join(parnames))

    hook += "    console.log('[%s] called with:" % tag
    if parnames:
      for i, parname in enumerate(parnames):
        if i > 0:
          hook += ", "
        hook += " arg%d=' + %s + '" % (i, parname)
      hook += "'"
    hook += ");\n"

    if no_return:
      hook += "    this.%s(%s);" % (mname, ', '.join(parnames))
    else:
      hook += "    var ret = this.%s(%s);\n" % (mname, ', '.join(parnames))
      hook += "    console.log('[%s] returned: ' + ret);\n" % tag
      hook += "    return ret;"

    hook += "\n  };\n"
    return hook
