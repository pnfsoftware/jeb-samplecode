package com.pnf.andhook;

import java.util.HashMap;
import java.util.Map;

import com.pnfsoftware.jeb.core.units.code.android.IDexUnit;
import com.pnfsoftware.jeb.core.units.code.debug.IDebuggerBreakpoint;
import com.pnfsoftware.jeb.core.units.code.debug.IDebuggerUnit;

/**
 * Handler manager fo hook objects.
 * 
 * @author Nicolas Falliere
 *
 */
public class HandlerManager {
    IDebuggerUnit dbg;
    IDexUnit dex;
    Map<IHandler, IDebuggerBreakpoint> hmap = new HashMap<>();

    public HandlerManager(IDebuggerUnit dbg, IDexUnit dex) {
        this.dbg = dbg;
        this.dex = dex;
    }

    public void register(IHandler handler) {
        String addr = handler.getAddress();
        IDebuggerBreakpoint bp = dbg.setBreakpoint(addr, dex);
        if(bp != null) {
            hmap.put(handler, bp);
        }
    }

    public IHandler getByAddress(String address) {
        for(IHandler h: hmap.keySet()) {
            if(address.startsWith(h.getAddress())) {
                return h;
            }
        }
        return null;
    }

    public boolean unregister(IHandler handler) {
        IDebuggerBreakpoint bp = hmap.get(handler);
        if(bp == null) {
            return false;
        }

        dbg.clearBreakpoint(bp);
        hmap.remove(handler);
        return true;
    }

    public void unregisterAll() {
        for(IHandler h: hmap.keySet()) {
            IDebuggerBreakpoint bp = hmap.get(h);
            dbg.clearBreakpoint(bp);
        }
        hmap.clear();
    }
}
