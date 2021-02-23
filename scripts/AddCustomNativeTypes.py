#?description=Create and add custom native structure types to a project
#?shortcut=
from com.pnfsoftware.jeb.client.api import IScript
from com.pnfsoftware.jeb.core.units import INativeCodeUnit
from com.pnfsoftware.jeb.core.units.code.asm.type import TypeUtil
"""
Sample script for JEB Decompiler.
API reference: ITypeManager, IPrimitiveTypeManager, TypeUtil and co.
"""
class AddCustomNativeTypes(IScript):
  def run(self, ctx):
    prj = ctx.getMainProject()
    assert prj, 'Need a project'

    unit = prj.findUnit(INativeCodeUnit)
    assert unit, 'Need a naive code unit'

    print('Will create type for native unit: %s' % unit)
    ''' create the following type:
      // Size: 10, Padding: 1, Alignment: 1
      struct MyStruct1 {
        int a;
        unsigned char[3][2] b;
      };
    '''    
    typeman = unit.getTypeManager()

    # method 1: craft the type manually, using the ITypeManager
    tInt = typeman.getType('int')
    tS1 = typeman.createStructure('MyStruct1')
    typeman.addStructureField(tS1, 'a', tInt)
    typeman.addStructureField(tS1, 'b', TypeUtil.buildArrayType(typeman, 'unsigned char', 2, 3))
    print('Added type: %s' % tS1)

    # method 2: parse a C-type, using a typeman-provided parser
    buf = 'enum SomeEnum {A,B,C};'
    tSomeEnum = typeman.getParser().parseTypesRaw(buf)
    print('Added type: %s' % tSomeEnum)