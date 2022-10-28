from com.pnfsoftware.jeb.core.units.code.android.ir import AbstractDOptimizer, IDSandboxHooks
from com.pnfsoftware.jeb.util.base import Wrapper
'''
dexdec IR plugin showing how to set up an emulator sandbox hooks for external methods.
The plugin below is an IR optimizer repeatedly invoked during the IR optimization phase of decompilation.
API reference: see IDSandboxHooks
'''
class DOptEmuSandboxHooksExample(AbstractDOptimizer):
  def perform(self):
    # retrieve or create the current decompiler thread emulator
    emu = self.g.getEmulator()
    # create and register a hooks object
    # in this sample code, the emulator's sandbox will hooks field accesses to
    # android.os.Build.VERSION and provide an alternate value (27) to the caller
    hooks_id = emu.registerSandboxHooks(SandboxHooks(emu))
    try:
      # do some work using the emulator
      # when/if the sandbox executes external dex methods, the hooks routines will be called
      pass
    finally:
      assert emu.unregisterSandboxHooks(hooks_id)

    # alternatively, you may want to set up global hooks to customize how other optimizers do their work
    # in this case, you want to make sure to not re-register the same hooks every time this optimizer is called
    # and also not unregister the hooks object when done
    '''
    emu = self.g.getEmulator()
    if not emu.getData('sandboxHooksSet'):
      emu.setData('sandboxHooksSet', True)
      emu.registerSandboxHooks(SandboxHooks(emu))
    '''
    return 0

class SandboxHooks(IDSandboxHooks):
  def __init__(self, emu):
    self.emu = emu

  def getField(reqid, addr, fsig, obj):
    if fsig == 'Landroid/os/Build$VERSION;->SDK_INT:I':
      # force-return the Android Oreo API level
      return Wrapper.wrap(27)
    return None

  # additional hook methods (for field setting, post-access checks, method invocation,
  # object construction, class loading) can be implemented: refer to IDSandboxHooks
  # in the API reference documentation