package com.pnf.andhook.handlers;

import com.pnfsoftware.jeb.core.units.code.debug.IDebuggerEventData;
import com.pnfsoftware.jeb.core.units.code.debug.IDebuggerThreadStackFrame;
import com.pnfsoftware.jeb.core.units.code.debug.IDebuggerUnit;
import com.pnfsoftware.jeb.core.units.code.debug.IDebuggerVariable;

/**
 * Hook for Cipher method: <code>int doFinal (byte[] output, int outputOffset)</code>.
 * 
 * @author Nicolas Falliere
 *
 */
public class Handler_doFinal_BaI extends AbstractHandler {

    @Override
    public String getAddress() {
        return "Ljavax/crypto/Cipher;->doFinal([BI)I";
    }

    @Override
    public void onEnter(IDebuggerUnit dbg, IDebuggerEventData data) {
        long tid = data.getThreadId();

        IDebuggerThreadStackFrame f0 = dbg.getThreadById(tid).getFrame(0);
        IDebuggerVariable p1 = f0.getInternalParameter(1, "[B");
        IDebuggerVariable p2 = f0.getInternalParameter(2, "I");

        int outputOffset = readInt(p2.getTypedValue());

        tls.put(tid, "output", p1);
        tls.put(tid, "outputOffset", outputOffset);
    }

    @Override
    public void onExit(IDebuggerUnit dbg, IDebuggerEventData data) {
        long tid = data.getThreadId();

        if(data.getReturnValue() == null) {
            logger.error("Cannot get return value");
            return;
        }
        int outputSize = readInt(data.getReturnValue());

        IDebuggerVariable p1 = tls.get(tid, "output", IDebuggerVariable.class);
        int outputOffset = tls.get(tid, "outputOffset", Integer.class);

        byte[] output = readByteArray(p1.getTypedValue(), outputOffset, outputSize);

        logData(null, output);

        tls.clean(tid);
    }
}
