import java.util.List;

import com.pnfsoftware.jeb.core.units.code.android.ir.AbstractDOptimizer;
import com.pnfsoftware.jeb.core.units.code.android.ir.DOptimizerType;
import com.pnfsoftware.jeb.core.units.code.android.ir.IDEmulatorHooks;
import com.pnfsoftware.jeb.core.units.code.android.ir.IDImm;
import com.pnfsoftware.jeb.core.units.code.android.ir.IDState;
import com.pnfsoftware.jeb.util.base.Wrapper;
import com.pnfsoftware.jeb.util.logging.GlobalLog;
import com.pnfsoftware.jeb.util.logging.ILogger;

/**
 * dexdec IR plugin showing how to set up an emulator hooks for internal dex methods.<br>
 * The hooks are called when the emulator is used by other optimizers.<br>
 * API reference: see IDEmulatorHooks
 */
public class DOptEmuHooksGlobalExample extends AbstractDOptimizer {

    @Override
    public int perform() {
        // here, we are setting up a global emulator hooks (not unregistered) that will impact all optimzers
        // refer to the sample file DOptEmulatorHooksExample.py for details

        IDState emu = g.getEmulator();
        if(emu.getData("hooksSet") == null) {
            emu.setData("hooksSet", true);  // do not set this hooks object more that once per emulator

            emu.registerEmulatorHooks(new IDEmulatorHooks() {
                @Override
                public Wrapper<IDImm> invokeMethod(long reqid, String msig, List<IDImm> args) {
                    logger.info("IR: invokeMethod: id=%d: %s(%s)", reqid, msig, args);
                    // TODO: add custom code
                    return null;
                }

                @Override
                public Wrapper<IDImm> examineMethodResult(long reqid, IDImm result) {
                    logger.info("IR: examineMethodResult: id=%d: ret=%s", reqid, result);
                    // TODO: add custom code
                    return null;
                }
            });
        }
        return 0;
    }
}
