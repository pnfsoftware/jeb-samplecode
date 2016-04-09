package com.pnf.andhook;

import java.util.HashMap;
import java.util.Map;

/**
 * Simple thread local storage, implemented as a map-to-map structure.
 * 
 * @author Nicolas Falliere
 *
 */
public class ThreadStore {
    private Map<Long, Map<String, Object>> tls = new HashMap<>();

    public void put(long tid, String name, Object object) {
        Map<String, Object> m = tls.get(tid);
        if(m == null) {
            m = new HashMap<String, Object>();
            tls.put(tid, m);
        }
        m.put(name, object);
    }

    @SuppressWarnings("unchecked")
    public <T> T get(long tid, String name, Class<T> c) {
        Map<String, Object> m = tls.get(tid);
        if(m == null) {
            return null;
        }

        Object o = m.get(name);
        if(o == null) {
            return null;
        }

        //if(!c.isAssignableFrom(o.getClass())) {
        //    return null;
        //}
        return (T)o;
    }

    public void clean(long tid) {
        tls.remove((Long)tid);
    }
}
