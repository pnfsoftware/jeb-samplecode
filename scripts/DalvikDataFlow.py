#?description=Examine Dalvik method Control Flow Graph (CFG) and perform data flow analysis on the graph to look at register definition locations and their uses, and register use locations and their definitions
#?shortcut=
from com.pnfsoftware.jeb.client.api import IScript
from com.pnfsoftware.jeb.core.units.code.android import IDexUnit
"""
Sample script for JEB Decompiler.

This script is showing how to examine Dalvik method Control Flow Graph (CFG) and perform
data flow analysis (DFA) on the graph to look at register definition locations and their
uses, and register use locations and their definitions.

What is Data Flow Analysis: a starting point at https://en.wikipedia.org/wiki/Data-flow_analysis
API documentation: start with https://www.pnfsoftware.com/jeb/apidoc/reference/com/pnfsoftware/jeb/core/units/code/IDFA3.html

How to use this sample script:
- open a DEX file
- position the caret somewhere on a Dalvik instruction in the Disassembly view
- run the script to see the uses and/or definitions of the registers manipulated by the instruction
"""
class DalvikDataFlow(IScript):

  def run(self, ctx):
    prj = ctx.getMainProject()
    assert prj, 'Need a project'

    dex = prj.findUnit(IDexUnit)
    assert prj, 'Need a dex unit'

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
    dfa = cfg.doDataFlowAnalysis()
    print('CFG for method was retrieved, DFA was performed')

    insn = cfg.getInstructionAt(off)
    print('Instruction on caret: %s' % insn)

    # DU-map: instruction -> map(register, list(instructions using the defined register))
    dumap = dfa.getDefUseChains(insn.getOffset())
    for regid, addrlist in dumap.items():
      print('[du] r%d: used at %s' % (regid, ','.join(['0x%X ' % (addr) for addr in addrlist])))

    # UD-map: instruction -> map(register, list(instructions using the defined register))
    udmap = dfa.getUseDefChains(insn.getOffset())
    for regid, addrlist in udmap.items():
      print('[ud] r%d: defined at %s' % (regid, ','.join(['0x%X ' % (addr) for addr in addrlist])))
