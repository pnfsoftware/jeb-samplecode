#?description=
#?shortcut=
from com.pnfsoftware.jeb.client.api import IScript, IGraphicalClientContext
from com.pnfsoftware.jeb.core.units.code.java import IJavaSourceUnit
from com.pnfsoftware.jeb.core.units.code.java import IJavaInstanceField, IJavaAssignment, IJavaIdentifier
"""
Sample script for JEB Decompiler.

Rename a Java field to its source variable's name, in a field assignment statement.

Demo for ITextFragment.getDocumentObjectsAtCaret()
Requires JEB 4.21 or above
"""
class JavaRenameField2(IScript):
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
    dex = ast_unit.getDecompiler().getDex()

    # ITextFragment.getDocumentObjectsAtCaret() is key to this demo script
    # this API function retrieves a stack of unit objects relating to the text element where the caret is currently positioned
    # these objects are unit-specific; in the case of an IJavaSourceUnit object, they are IJavaElement objects (AST objects)
    astobjstk = fragment.getDocumentObjectsAtCaret()
    if len(astobjstk) < 2:
      return
    ast0 = astobjstk[-1]
    ast1 = astobjstk[-2]

    # we want: some_object.some_field = some_var
    #                      ^ (the caret is supposed to highlight the field item)
    if not isinstance(ast0, IJavaInstanceField):
      return
    if not isinstance(ast1, IJavaAssignment):
      return
    if not isinstance(ast1.getRight(), IJavaIdentifier):
      return

    # perform the renaming
    ident_name = ast1.getRight().getName()
    fsig = ast0.getField().getSignature()
    dex.getField(fsig).setName(ident_name)
