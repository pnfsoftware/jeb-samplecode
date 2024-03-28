#?description= Jump to method code providing a dex file offset
#?shortcut=

from com.pnfsoftware.jeb.client.api import IScript, IGraphicalClientContext
from com.pnfsoftware.jeb.core.units.code.android import IDexUnit
"""
Sample script for JEB Decompiler.

Providing a file offset and an optional classesN.dex index, find the corresponding method and the
bytecode location, and jump to that location in the disassembly view.
"""
class DexJumpToFileOffset(IScript):
  def run(self, ctx):
    assert isinstance(ctx, IGraphicalClientContext), 'Must run in GUI'

    prj = ctx.getMainProject()
    assert prj, 'Need an opened project'

    dex = prj.findUnit(IDexUnit)
    assert dex, 'Need a processed dex'

    val = ctx.displayQuestionBox('Provide a dex file offset',
      'Offset (hex), followed by optional classes.dex file. Examples:\n'
      + '1000 => offset 0x1000 in classes.dex; 2000,2 => offset 0x2000 in classes2.dex', '')
    if not val: return
    val = val.strip()
    if val == '': return
    elts = val.split(',')
    offset = int(elts[0].strip(), 16)
    dexidx = 1 if len(elts) < 2 else int(elts[1].strip(), 16)
    print('Searching for method bytecode at: offset 0x%X in classes%s.dex' % (offset, '' if dexidx == 1 else str(dexidx)))

    target_addr = None
    for m in dex.getMethods():
      if m.isInternal():
        code = m.getData().getCode()
        if code:
          if code.getDexFileIndex() + 1 == dexidx:
            start = code.getInstructionsOffset()
            if offset >= start and offset < start + code.getInstructionsSize():
              target_addr = m.getAddress()
              moff = offset - start
              for insn in code.getInstructions():
                insn_offset = insn.getOffset()
                if moff >= insn_offset and moff < insn_offset + insn.getSize():
                  target_addr += '+%Xh' % insn_offset

    if not target_addr:
      print('Not found.')
      return

    print('Found: %s' % target_addr)
    f = ctx.findFragment(dex, 'Disassembly', True)
    f.setActiveAddress(target_addr)
