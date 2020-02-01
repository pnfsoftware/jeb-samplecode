from com.pnfsoftware.jeb.client.api import IScript
from com.pnfsoftware.jeb.core.units.code.android import IDexUnit
"""
Script for JEB Decompiler.

Sample script showing how to examine Dalvik method Control Flow Graph (CFG) and perform
data flow analysis on the graph to look at register definition locations and their uses,
and register use locations and their definitions.

What is Data Flow Analysis: a starting point at https://en.wikipedia.org/wiki/Data-flow_analysis
API documentation: start with https://www.pnfsoftware.com/jeb/apidoc/reference/com/pnfsoftware/jeb/core/units/code/android/controlflow/CFG.html

Key methods: doDataFlowAnalysis(), getFullDefUseChains(), getFullUseDefChains(), getSimpleDefUseChains(), getSimpleUseDefChains()

How to use this sample script: open a DEX file, position the caret somewhere on a Dalvik instruction in the Disassembly view
"""
class DalvikDataFlow(IScript):

  def run(self, ctx):
    prj = ctx.getMainProject()
    dex = prj.findUnit(IDexUnit)
    if not dex:
      print('Open a DEX unit')
      return

    addr = ctx.getFocusedView().getActiveFragment().getActiveAddress()
    pos = addr.find('+')
    if pos >= 0:
      mname = addr[0:pos]
      off = int(addr[pos + 1:].rstrip('h'), 16)
    else:
      mname = addr
      off = 0

    m = dex.getMethod(mname)
    if not m:
      print('No method found at address: %s' % addr)
      return

    print('Method: %s, Offset: 0x%X' % (mname, off))

    cfg = m.getData().getCodeItem().getControlFlowGraph()
    cfg.doDataFlowAnalysis()
    print('CFG for method was retrieved, DFA was performed')

    insn = cfg.getInstructionAt(off)
    print('Instruction on caret: %s' % insn)

    # DU-map: instruction -> map(register, list(instructions using the defined register))
    dumap = cfg.getFullDefUseChains().get(insn)
    for regid, using_insnlist in dumap.items():
      print('[du] r%d: %s' % (regid, ['0x%X: %s' % (insn.getOffset(), insn.format(None)) for insn in using_insnlist]))

    # UD-map: instruction -> map(register, list(instructions using the defined register))
    udmap = cfg.getFullUseDefChains().get(insn)
    for regid, defining_insnlist in udmap.items():
      print('[ud] r%d: %s' % (regid, ['<init>' if insn == None else '0x%X: %s' % (insn.getOffset(), insn.format(None)) for insn in defining_insnlist]))
