#?description=Show how the Java AST API can be used to modify and create elements in a decompiled syntax tree
#?shortcut=
import time
from com.pnfsoftware.jeb.client.api import IScript
from com.pnfsoftware.jeb.core.units.code.java import IJavaSourceUnit
"""
Sample script for JEB Decompiler.

The script shows how to use the Java factory to create an external method reference (also available for fields),
create a new statement (here, a call to 'new String("...")'), and replace an arbitrary selected statement
(index 0 in the currently selected method) by the new statement.

- Open an APK/DEX, decompile any class or method
- In the Decompiled view, position the caret somewhere in a method
- Execute the script
"""
class JavaASTCreateMethodRef(IScript):

  def run(self, ctx):
    # retrieve the currently active UI fragment (make sure to select a Decompiled Java fragment)
    f = ctx.getFocusedFragment()
    assert f, 'Need a focused fragment'

    unit = f.getUnit()
    assert isinstance(unit, IJavaSourceUnit), 'Need a java unit'

    # a DEX-style address: TYPENAME->METHODNAME(PARAMTYPES)RETTYPE+OFFSET
    addr = f.getActiveAddress()

    # IDexDecompilerUnit
    dexdec = unit.getParent()

    pos = addr.find('+')
    if pos >= 0: addr = addr[:pos]

    # retrieve the already decompiled IJavaMethod on caret
    _m = dexdec.getMethod(addr)

    # method body...
    _blk = _m.getBody()
    # we pick the first statement
    _stm0 = _blk.get(0)
    print('Will replace statement: "%s"' % _stm0)

    # IJavaFactories
    self.jfactory = unit.getFactories()

    # now, replace that first method statement by a call to 'new String("...")'
    if self.replaceStatement(_blk, _stm0):
      unit.notifyGenericChange()


  def replaceStatement(self, parent, e):
    m = self.jfactory.createMethodReference('Ljava/lang/String;-><init>(Ljava/lang/String;)V', False)
    t = self.jfactory.getTypeFactory().createType('Ljava/lang/String;')
    args = [self.jfactory.getConstantFactory().createString('FOOBAR__' + str(time.time()))]
    stm = self.jfactory.createNew(t, m, args)
    return parent.replaceSubElement(e, stm)
