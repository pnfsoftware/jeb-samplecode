#?description=Rename a Java field to its source variable's name, in a field assignment statement.
#?shortcut=
from com.pnfsoftware.jeb.client.api import IScript, IGraphicalClientContext
from com.pnfsoftware.jeb.core.units.code.android.dex import IDexField
from com.pnfsoftware.jeb.core.units.code.java import IJavaSourceUnit
from com.pnfsoftware.jeb.core.units.code.java import IJavaInstanceField, IJavaAssignment, IJavaIdentifier
"""
Sample script for JEB Decompiler.

Rename a Java field to its source variable's name, in a field assignment statement.

In a decompiled Java method, place the caret on the target object field.
Example: this.field3 = blah;
               ^^^^ caret here
"""
class JavaRenameField1(IScript):
  def run(self, ctx):
    # must be a GUI client
    prj = ctx.getMainProject()
    if not isinstance(ctx, IGraphicalClientContext):
      return

    # retrieve the focused text fragment
    fragment = ctx.getFocusedFragment()
    if not fragment:
      return

    # focused fragment must be decompiled Java, underlying unit is of type IJavaSourceUnit
    ast_unit = fragment.getUnit()
    if not isinstance(ast_unit, IJavaSourceUnit):
      return
    self.dex = ast_unit.getDecompiler().getDex()

    # retrieve the active (highlighted) item, which must be an object field
    item = fragment.getActiveItem()
    if not item:
      return

    # retrieve the underlying IDexField object
    o = ast_unit.getItemObject(item.getItemId())
    if not isinstance(o, IDexField):
      return
    self.target_field = o

    # walk the methods's AST tree, look for assignments to the target field
    for m in ast_unit.getClassElement().getMethods():
      self.processASTMethod(None, m)

  def processASTMethod(self, parent, e):
    if isinstance(e, IJavaAssignment) and isinstance(e.getRight(), IJavaIdentifier) and isinstance(e.getLeft(), IJavaInstanceField):
      dst, src = e.getLeft(), e.getRight()
      # perform the renaming
      ident_name = src.getName()
      fsig = dst.getField().getSignature()
      if self.dex.getField(fsig) == self.target_field:
        self.target_field.setName(ident_name)
    for subelt in e.getSubElements():
      self.processASTMethod(e, subelt)
