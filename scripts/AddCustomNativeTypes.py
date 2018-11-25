"""
Script for JEB Decompiler.

This script demonstrates how to create and add custom native structure types to a project.

API reference: ITypeManager, IPrimitiveTypeManager, TypeUtil and co.

Refer to SCRIPTS.TXT for more information.
"""

from com.pnfsoftware.jeb.client.api import IScript
from com.pnfsoftware.jeb.core import RuntimeProjectUtil
from com.pnfsoftware.jeb.core.units import INativeCodeUnit
from com.pnfsoftware.jeb.core.units.code.asm.type import TypeUtil


class AddCustomNativeTypes(IScript):
  def run(self, ctx):
    engctx = ctx.getEnginesContext()
    if not engctx:
      print('Back-end engines not initialized')
      return

    projects = engctx.getProjects()
    if not projects:
      print('There is no opened project')
      return

    # get the first native code unit available
    units = RuntimeProjectUtil.findUnitsByType(projects[0], INativeCodeUnit, False)
    if not units:
      print('No unit available')
      return

    unit = units[0]
    print('Unit: %s' % unit)

    ''' create the following type:
      // Size: 10, Padding: 1, Alignment: 1
      struct MyStruct1 {
        int a;
        unsigned char[3][2] b;
      };
    '''
    
    typeman = unit.getTypeManager()
    tInt = typeman.getType('int')
    tS1 = typeman.createStructure('MyStruct1')
    typeman.addStructureField(tS1, 'a', tInt)
    typeman.addStructureField(tS1, 'b', TypeUtil.buildArrayType(typeman, 'unsigned char', 2, 3))
