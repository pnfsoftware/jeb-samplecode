#?description=Attempt to find the high-level entry-point of a binary file
#?shortcut=

from com.pnfsoftware.jeb.client.api import IScript
from com.pnfsoftware.jeb.core.units import INativeCodeUnit

'''
Sample script for JEB Decompiler.

Search for the high-level entry-point (the main() or similar) of a compiled binary file.
Currently supported: MSVC WinMain/wWinMain x86 and x64

Requirement: JEB 5.7+
'''
class FindMain(IScript):
  def run(self, ctx):
    prj = ctx.getMainProject()
    u = prj.findUnit(INativeCodeUnit)
    if not u:
      print('No native code unit')
      return

    hlep = u.getHighLevelEntryPointAddress()
    if hlep != -1:
      print('[NOTE] A high-level entry-point is already set: 0x%X' % hlep)

    # each detection routine returns either None or a tuple (br_to_hlep, hlep, wanted_name)
    r = None
    if not r:
      r = find_hlep_msvc_x86(u)
    if not r:
      r = find_hlep_msvc_x64(u)
    # NOTE: add more detection code here
    if not r:
      print('Nothing found')
      return

    br_to_hlep, hlep, wanted_name = r[0], r[1], r[2]
    print('Found high-level entry-point at 0x%X (branched from 0x%X)' % (hlep, br_to_hlep))

    cm = u.getCommentManager()
    cm.setInlineComment(cm.memoryToAddress(br_to_hlep), 'Jump to high-level entry-point')

    m = u.getInternalMethod(hlep)
    if m and wanted_name:
      print('Renaming entry-point to \'%s\'' % wanted_name)
      m.setName(wanted_name)

#------------------------------------------------------------------------------
def find_hlep_msvc_x86(u):
  if u.getProcessorName() != 'x86':
    return None

  # call __security_init_cookie
  # jmp  next
  ep = u.getEntryPointAddress()
  if not check_bytes(u, ep, 'e8 ?? ?? ?? ?? e9 ?? ?? ?? ??'):
    return None

  # resolve the jmp target
  addr = ep + 5
  addr += 5 + u.getMemory().readLEInt(addr + 1)

  # the previous instructions may not have been associated to the routine at addr
  m = u.getInternalMethod(addr, False)
  if not m:
    return None

  cfg = m.getData().getCFG()    
  br_to_hlep, hlep = -1, -1
  for b in cfg:
    if b.size() >= 2:
      i = b.size() - 2
      if b.get(i).getMnemonic() == 'push' and b.get(i + 1).getMnemonic() == 'call':
        addr, insn = b.getAddressOfInstruction(i), b.get(i)
        if check_bytes(u, addr, '68 ?? ?? ?? ??'):
          addr = u.getMemory().readLEInt(addr + 1)
          if addr == u.getVirtualImageBase():
            addr, insn = b.getAddressOfInstruction(i+1), b.get(i+1)            
            hlep = insn.getPrimaryBranchAddress(addr)
            br_to_hlep = addr
            break
  if hlep == -1:
    return None
  return (br_to_hlep, hlep, 'winmain')

#------------------------------------------------------------------------------
def find_hlep_msvc_x64(u):
  if u.getProcessorName() != 'x86_64':
    return None

  # sub  rsp, xxx
  # call _security_init_cookie
  # add  rsp, xxx
  # jmp  next
  ep = u.getEntryPointAddress()
  if not check_bytes(u, ep, '48 83 ec ?? e8 ?? ?? ?? ?? 48 83 c4 ?? e9 ?? ?? ?? ??'):
    return None

  # resolve the jmp target
  addr = ep + 13
  addr += 5 + u.getMemory().readLEInt(addr + 1)

  # the previous instructions may not have been associated to the routine at addr    
  m = u.getInternalMethod(addr, False)
  if not m:
    return None

  # search for basic block ending with: lea rcx, [IMAGE_BASE] / call
  cfg = m.getData().getCFG()
  br_to_hlep, hlep = -1, -1
  for b in cfg:
    if b.size() >= 2:
      i = b.size() - 2
      if b.get(i).getMnemonic() == 'lea' and b.get(i + 1).getMnemonic() == 'call':
        addr, insn = b.getAddressOfInstruction(i), b.get(i)
        if check_bytes(u, addr, '48 8d 0d ?? ?? ?? ??'):
          addr += 7 + u.getMemory().readLEInt(addr + 3)
          if addr == u.getVirtualImageBase():
            addr, insn = b.getAddressOfInstruction(i+1), b.get(i+1)            
            hlep = insn.getRoutineCall(addr).getTargets().get(0).getAddress()
            br_to_hlep = addr
            break
  if hlep == -1:
    return None
  return (br_to_hlep, hlep, 'winmain')

#------------------------------------------------------------------------------
def check_bytes(u, addr, pattern):
  pattern = pattern.replace(' ', '')
  pattern2 = ''
  mask = ''
  if len(pattern) % 2 != 0: raise Exception()
  for c in pattern:
    if c == '?':
      mask += '0'
      pattern2 += '0'
    else:
      mask += 'f'
      pattern2 += c
  import binascii
  binpattern = binascii.unhexlify(pattern2)
  binmask = binascii.unhexlify(mask)
  size = len(binpattern)
  data = [-1] * size
  for bval, bmask in zip(binpattern, binmask):
    x = u.getMemory().readByte(addr)
    if (x & ord(bmask)) != ord(bval):
      return False
    addr += 1
  return True
