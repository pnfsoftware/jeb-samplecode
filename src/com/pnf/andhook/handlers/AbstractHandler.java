package com.pnf.andhook.handlers;

import java.util.List;

import com.pnf.andhook.IHandler;
import com.pnf.andhook.ThreadStore;
import com.pnfsoftware.jeb.core.units.code.debug.IDebuggerVariable;
import com.pnfsoftware.jeb.core.units.code.debug.ITypedValue;
import com.pnfsoftware.jeb.core.units.code.debug.impl.ValueByte;
import com.pnfsoftware.jeb.core.units.code.debug.impl.ValueInteger;
import com.pnfsoftware.jeb.core.units.code.debug.impl.ValueObject;
import com.pnfsoftware.jeb.util.Formatter;
import com.pnfsoftware.jeb.util.logging.GlobalLog;
import com.pnfsoftware.jeb.util.logging.ILogger;

/**
 * Base class for hook objects.
 * 
 * @author Nicolas Falliere
 *
 */
public abstract class AbstractHandler implements IHandler {
    protected static final ILogger logger = GlobalLog.getLogger(AbstractHandler.class);

    protected ThreadStore tls = new ThreadStore();

    protected void logData(byte[] in, byte[] out) {
        StringBuilder sb = new StringBuilder();
        sb.append(String.format("[CRYPTO] %s\n", getAddress()));
        if(in != null) {
            sb.append(String.format(">>>>\n%s", Formatter.formatBinaryBlock(in)));
        }
        if(out != null) {
            sb.append(String.format("<<<<\n%s", Formatter.formatBinaryBlock(out)));
        }
        logger.info(sb.toString());
    }

    public static int readInt(ITypedValue v) {
        if(!(v instanceof ValueInteger)) {
            throw new IllegalArgumentException();
        }

        return ((ValueInteger)v).getValue();
    }

    public static byte[] readByteArray(ITypedValue v) {
        // read all
        return readByteArray(v, 0, -1);
    }

    public static byte[] readByteArray(ITypedValue v, int offset, int size) {
        if(!(v instanceof ValueObject)) {
            throw new IllegalArgumentException();
        }
        ValueObject o = (ValueObject)v;

        @SuppressWarnings("unchecked")
        List<IDebuggerVariable> byteVariables = (List<IDebuggerVariable>)o.getValue();

        int cnt = size < 0 ? byteVariables.size(): size;
        byte[] in = new byte[cnt];

        int i = 0;
        for(IDebuggerVariable byteVar: byteVariables.subList(offset, offset + cnt)) {
            in[i] = ((ValueByte)byteVar.getTypedValue()).getValue();
            i++;
        }
        return in;
    }
}
