#?description=Create a native code class into the first found native code unit
#?shortcut=
from com.pnfsoftware.jeb.client.api import IScript
from com.pnfsoftware.jeb.core.units import INativeCodeUnit
from com.pnfsoftware.jeb.core.units.code.asm.type import TypeUtil
"""
Script for JEB Decompiler.
"""
class CreateEmptyClass(IScript):

  def run(self, ctx):
    prj = ctx.getMainProject()
    assert prj, 'Need a project'

    unit = prj.findUnit(INativeCodeUnit)
    assert unit, 'Need a native code unit'

    # class type (abstract)
    cname = 'Class001'
    typeman = unit.getTypeManager()
    #tInt = typeman.getType('int')
    ctype = typeman.getType(cname)
    if not ctype:
      ctype = typeman.createClassType(cname, 1, 0)
      typeman.completeClassTypeInitialization(ctype)
    print(ctype)

    # class item (concrete)
    classman = unit.getClassManager()
    c = classman.createClass(ctype)
    classman.completeClassInitialization(c)
    print(c)

    # make the first routine found in the code a static method of that class
    m = unit.getInternalMethods().get(0)
    if m:      
      classman.addStaticMethod(c, m)

    unit.notifyGenericChange()

    #tS1 = typeman.createStructure('MyStruct1')
    #typeman.addStructureField(tS1, 'a', tInt)
    #typeman.addStructureField(tS1, 'b', TypeUtil.buildArrayType(typeman, 'unsigned char', 2, 3))
